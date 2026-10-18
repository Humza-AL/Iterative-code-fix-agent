
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage
from tools import read_file, write_file, run_python

load_dotenv()

# 1. Set up the AI model
llm = ChatOpenAI(
    model="gpt-5.6",
    temperature=0,
    reasoning_effort="none"
)

# 2. Give the AI access to our tools
llm_with_tools = llm.bind_tools([
    read_file,
    write_file,
    run_python
])

# 3. Tell the AI what task to perform
messages = [
    (
        "human",
        """
        Fix the Python function in buggy_code_working.py.

        Follow these rules:

        1. Read buggy_code_working.py and agent_tests.py before making changes.
        2. Identify the implementation bug and relevant edge cases.
    3. Fix the implementation in buggy_code_working.py when the code is actually incorrect.
    4. Preserve existing tests in agent_tests.py. Do not remove or weaken a valid test just to make the suite pass.
    5. Ensure agent_tests.py covers:
        - Normal input: [1, 2, 3, 4] returns 2.5.
        - Empty input: [] returns 0.
        - Negative and floating-point input: [-2, 1.5, 3.5] returns 1.0.
    6. If a test fails, inspect the error and determine whether the implementation or the test expectation is wrong.
    7. If the implementation is wrong, fix buggy_code_working.py. If a test expectation is wrong, explain why before correcting that test.
    8. Run the complete agent_tests.py test suite after every change to buggy_code_working.py.
    9. Inspect the actual test output. If tests fail, use the errors to guide the next correction.
    10. Stop when all required tests pass or the maximum of 3 writes to buggy_code_working.py is reached.
    11. Never claim the tests passed unless the actual test output confirms success.
    12. Only modify buggy_code_working.py and agent_tests.py.
    13. In your final report, explain the bug, the fix, which tests ran, and whether they passed.

    Do not change correct implementation code just to satisfy an incorrect test. Do not remove existing valid test coverage.
        """
    )
]

# 4. Ask the AI what to do first
response = llm_with_tools.invoke(messages)


# 5. Handle tool requests, with a limit on rounds
max_rounds = 8
max_fix_attempts = 3
fix_attempts = 0

for round_number in range(max_rounds):

    # Stop if the AI has no more tools to call
    if not response.tool_calls:
        break

    # Add the AI's requests to the conversation
    messages.append(response)

    # Execute each requested tool
    for tool_call in response.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        try:
            if tool_name == "read_file":
                tool_result = read_file.invoke(tool_args)

            elif tool_name == "write_file":
                file_path = tool_args.get("file_path", "")

                # Only allow changes to these two files
                if file_path not in (
                    "buggy_code_working.py",
                    "agent_tests.py"
                ):
                    tool_result = (
                        "File not allowed. You may only modify "
                        "buggy_code_working.py and agent_tests.py."
                    )

                # Count attempts to fix the working code
                elif file_path == "buggy_code_working.py":
                    if fix_attempts >= max_fix_attempts:
                        tool_result = (
                            "Maximum of 3 code-write attempts reached. "
                            "Do not modify buggy_code_working.py again."
                        )
                    else:
                        fix_attempts += 1

                        print(
                            f"\nFix attempt "
                            f"{fix_attempts}/{max_fix_attempts}"
                        )

                        # Write the corrected code
                        write_result = write_file.invoke(tool_args)

                        # Automatically run the test file
                        test_result = run_python.invoke({
                            "file_path": "agent_tests.py"
                        })

                        # Send both results back to the AI
                        tool_result = (
                            str(write_result)
                            + "\n\nAutomatic test results:\n"
                            + str(test_result)
                            + "\nInspect these results. If tests fail, "
                            "fix the code and try again, within the "
                            "attempt limit."
                        )

                # Allow the AI to create or update its test file
                else:
                    tool_result = write_file.invoke(tool_args)

            elif tool_name == "run_python":
                tool_result = run_python.invoke(tool_args)

            else:
                tool_result = f"Unknown tool: {tool_name}"

        except Exception as error:
            tool_result = f"Tool error: {error}"

        # Return the tool result to the AI
        messages.append(
            ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call["id"]
            )
        )

    # Let the AI inspect the tool results and decide what to do next
    response = llm_with_tools.invoke(messages)


# 6. Print the final response
if response.tool_calls:
    print("Stopped: reached the maximum number of tool rounds.")
    print("The agent may need another run to finish.")
else:
    print(response.content)

print("\n--- Original Code ---")
original_code = read_file.invoke({
    "file_path": "buggy_code.py"
})
print(original_code)




# 7. Display the corrected code
print("\n--- Corrected Code ---")

try:
    fixed_code = read_file.invoke({
        "file_path": "buggy_code_working.py"
    })
    print(fixed_code)

except Exception as error:
    print(f"Could not display corrected code: {error}")




# 8. Run and display the tests
print("\n--- Running Tests ---")

test_result = run_python.invoke({
    "file_path": "agent_tests.py"
})

test_output = str(test_result)
print(test_output)

# Determine success from the actual test execution result
if "Exit code: 0" in test_output:
    print("\nFINAL STATUS: PASS - All tests completed successfully.")
else:
    print("\nFINAL STATUS: FAIL - Check the test output above.")

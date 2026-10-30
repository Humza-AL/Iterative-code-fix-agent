
import ast
import builtins
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()

llm = ChatOpenAI(
    model="gpt-5.6",
    temperature=0,
    reasoning_effort="none"
)


# -----------------------------------------
# 1. AI CODE CORRECTION
# -----------------------------------------

def fix_code(user_code: str) -> dict:
    """Ask the AI to correct code and check its syntax."""

    messages = [
        (
            "human",
            f"""
            Review this Python code for bugs and edge cases.
            Return the complete corrected code in one Python
            code block, followed by an explanation.

            Do not claim you executed or tested the code.

            Submitted code:
            ```python
            {user_code}
            ```
            """
        )
    ]

    response = llm.invoke(messages)
    ai_response = response.content

    match = re.search(
        r"```(?:python)?\s*\n(.*?)```",
        ai_response,
        re.DOTALL | re.IGNORECASE
    )

    corrected_code = match.group(1).strip() if match else ""

    syntax_valid = False
    syntax_message = ""

    if not corrected_code:
        syntax_message = "No Python code block was found."

    else:
        try:
            ast.parse(corrected_code)
            syntax_valid = True
            syntax_message = "Python syntax is valid."

        except SyntaxError as error:
            syntax_message = (
                f"Syntax error on line {error.lineno}: {error.msg}"
            )

    return {
        "original_code": user_code,
        "corrected_code": corrected_code,
        "ai_response": ai_response,
        "syntax_valid": syntax_valid,
        "syntax_message": syntax_message,
    }


# -----------------------------------------
# 2. AI-GENERATED TEST SUGGESTIONS
# -----------------------------------------

def generate_tests(corrected_code: str) -> dict:
    """Ask the AI to suggest behavioral tests, including exceptions."""

    if not corrected_code.strip():
        return {
            "success": False,
            "tests": [],
            "message": "No corrected code is available.",
        }

    prompt = f"""
You are helping test a Python function.

Review this code and suggest up to 5 useful behavioral tests.
Include normal inputs, edge cases, and boundary cases where relevant.

Rules:
- Only suggest tests for functions defined in the submitted code.
- Do not invent expected behavior when it is ambiguous.
- Mark uncertain expectations as needing_review.
- Each test must include:
  function_name, arguments, expected,
  expected_exception, and needs_review.
- arguments must be a JSON list of positional arguments.
- expected must be a JSON value, or null if an exception is expected
  or the expected behavior is unclear.
- expected_exception must be the name of a built-in Python exception
  such as "ValueError", "TypeError", or "ZeroDivisionError".
- Use null for expected_exception when no exception is expected.
- If behavior is unclear, use null for expected and expected_exception,
  and set needs_review to true.
- Return ONLY a valid JSON array. Do not use Markdown fences.

Example:
[
  {{
    "function_name": "add",
    "arguments": [2, 3],
    "expected": 5,
    "expected_exception": null,
    "needs_review": false
  }},
  {{
    "function_name": "calculate_average",
    "arguments": [[]],
    "expected": null,
    "expected_exception": "ValueError",
    "needs_review": false
  }}
]

Submitted code:
```python
{corrected_code}
```
"""

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()

        # Remove Markdown fences if the AI includes them.
        content = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            content,
            flags=re.IGNORECASE,
        ).strip()

        tests = json.loads(content)

        if not isinstance(tests, list):
            raise ValueError("The AI response must be a JSON list.")

        required_fields = {
            "function_name",
            "arguments",
            "expected",
            "expected_exception",
            "needs_review",
        }

        for test in tests:

            if not isinstance(test, dict):
                raise ValueError("Each test must be a JSON object.")

            if not required_fields.issubset(test):
                raise ValueError("A test is missing required fields.")

            if not isinstance(test["function_name"], str):
                raise ValueError("A function name must be text.")

            if not re.fullmatch(r"[A-Za-z_]\w*", test["function_name"]):
                raise ValueError("The AI returned an invalid function name.")

            if not isinstance(test["arguments"], list):
                raise ValueError("Test arguments must be a JSON list.")

            if not isinstance(test["needs_review"], bool):
                raise ValueError("needs_review must be true or false.")

            # Validate expected exception names.
            exception_name = test["expected_exception"]

            if exception_name is not None:

                if not isinstance(exception_name, str):
                    raise ValueError("Expected exception must be text or null.")

                exception_type = getattr(builtins, exception_name, None)

                if (
                    not isinstance(exception_type, type)
                    or not issubclass(exception_type, Exception)
                ):
                    raise ValueError(
                        "The AI returned an unsupported exception name."
                    )

                if test["expected"] is not None:
                    raise ValueError(
                        "Expected result must be null when an exception is expected."
                    )

        return {
            "success": True,
            "tests": tests,
            "message": "Test suggestions generated successfully.",
        }

    except (json.JSONDecodeError, ValueError) as error:
        return {
            "success": False,
            "tests": [],
            "message": f"Could not parse the AI's test suggestions: {error}",
        }

    except Exception as error:
        return {
            "success": False,
            "tests": [],
            "message": f"Could not generate tests: {error}",
        }


# -----------------------------------------
# 3. MANUAL BEHAVIORAL TESTING
# -----------------------------------------

def test_function(
    corrected_code: str,
    function_name: str,
    arguments_text: str,
    expected_text: str,
    expected_exception: str = None,
) -> dict:
    """Run a behavioral test against corrected Python code."""

    if not corrected_code.strip():
        return {
            "passed": False,
            "output": "No corrected code to test."
        }

    if not re.fullmatch(r"[A-Za-z_]\w*", function_name):
        return {
            "passed": False,
            "output": "Enter a valid function name."
        }

    # Parse the arguments and expected result.
    try:
        arguments = json.loads(arguments_text)
        expected = json.loads(expected_text)

    except json.JSONDecodeError as error:
        return {
            "passed": False,
            "output": f"Invalid JSON in arguments or expected result: {error}",
        }

    if not isinstance(arguments, list):
        return {
            "passed": False,
            "output": "Arguments must be a JSON list, such as [2, 3].",
        }

    # Validate the expected exception.
    if expected_exception is not None:

        if not isinstance(expected_exception, str):
            return {
                "passed": False,
                "output": "Expected exception must be text.",
            }

        exception_type = getattr(builtins, expected_exception, None)

        if (
            not isinstance(exception_type, type)
            or not issubclass(exception_type, Exception)
        ):
            return {
                "passed": False,
                "output": "Unsupported expected exception.",
            }

        if expected is not None:
            return {
                "passed": False,
                "output": "Expected result must be null when an exception is expected.",
            }

    with tempfile.TemporaryDirectory() as temp_dir:

        folder = Path(temp_dir)
        code_file = folder / "submitted_code.py"
        test_file = folder / "run_test.py"

        code_file.write_text(corrected_code, encoding="utf-8")

        arguments_json = json.dumps(arguments)
        expected_json = json.dumps(expected)

        test_script = f"""
import sys
import json
import builtins
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import submitted_code

function = getattr(submitted_code, {function_name!r})
arguments = json.loads({arguments_json!r})
expected = json.loads({expected_json!r})
expected_exception = {expected_exception!r}

try:
    actual = function(*arguments)

except Exception as error:

    if expected_exception is not None:
        expected_type = getattr(builtins, expected_exception)

        if isinstance(error, expected_type):
            print(f"Expected exception: {{expected_exception}}")
            print(f"Actual exception: {{type(error).__name__}}")
            print("TEST PASSED")
            sys.exit(0)

    print(f"Unexpected exception: {{type(error).__name__}}: {{error}}")
    print("TEST FAILED")
    sys.exit(1)

if expected_exception is not None:
    print(f"Expected exception: {{expected_exception}}")
    print("No exception was raised.")
    print("TEST FAILED")
    sys.exit(1)

print(f"Actual result: {{actual!r}}")
print(f"Expected result: {{expected!r}}")

if actual != expected:
    print("TEST FAILED")
    sys.exit(1)

print("TEST PASSED")
"""

        test_file.write_text(test_script, encoding="utf-8")

        try:
            result = subprocess.run(
                [sys.executable, "-I", str(test_file)],
                capture_output=True,
                text=True,
                timeout=3,
                cwd=str(folder),
            )

            output = result.stdout + result.stderr

            return {
                "passed": result.returncode == 0,
                "output": output or "Test finished with no output.",
            }

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "output": "Test timed out after 3 seconds.",
            }


# -----------------------------------------
# 4. AUTOMATICALLY RUN AI-GENERATED TESTS
# -----------------------------------------

def run_generated_tests(corrected_code: str, tests: list) -> list:
    """Run AI-generated behavioral tests against corrected Python code."""

    results = []

    for index, test in enumerate(tests, start=1):

        function_name = test["function_name"]
        arguments = test["arguments"]
        expected = test["expected"]
        expected_exception = test["expected_exception"]

        try:
            result = test_function(
                corrected_code,
                function_name,
                json.dumps(arguments),
                json.dumps(expected),
                expected_exception,
            )

            results.append({
                "test_number": index,
                "function_name": function_name,
                "arguments": arguments,
                "expected": expected,
                "expected_exception": expected_exception,
                "passed": result["passed"],
                "output": result["output"],
            })

        except Exception as error:

            results.append({
                "test_number": index,
                "function_name": function_name,
                "arguments": arguments,
                "expected": expected,
                "expected_exception": expected_exception,
                "passed": False,
                "output": str(error),
            })

    return results

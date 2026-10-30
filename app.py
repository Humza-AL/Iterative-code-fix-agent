
import re

import streamlit as st

from agent import (
    fix_code,
    test_function,
    generate_tests,
    run_generated_tests,
)


# -----------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------

st.set_page_config(
    page_title="AI Code Fixer",
    page_icon="🛠️",
    layout="wide",
)

st.title("🛠️ AI Code Fixer")

st.write(
    "Paste your Python code below. "
    "The AI will suggest a correction and check its syntax."
)

user_code = st.text_area(
    "Your Python code",
    height=300,
    placeholder="Paste your Python code here...",
)


# -----------------------------------------
# INITIALIZE SESSION STATE
# -----------------------------------------

if "result" not in st.session_state:
    st.session_state["result"] = None

if "suggested_tests" not in st.session_state:
    st.session_state["suggested_tests"] = None

if "generated_test_results" not in st.session_state:
    st.session_state["generated_test_results"] = None


# -----------------------------------------
# FIX SUBMITTED CODE
# -----------------------------------------

if st.button("Fix My Code", type="primary"):

    if not user_code.strip():

        st.warning("Please paste some Python code first.")

        # Clear old results when no code is submitted.
        st.session_state["result"] = None
        st.session_state["suggested_tests"] = None
        st.session_state["generated_test_results"] = None

    else:

        with st.spinner("AI is reviewing your code..."):

            try:
                st.session_state["result"] = fix_code(user_code)

                # Clear previous test data.
                st.session_state["suggested_tests"] = None
                st.session_state["generated_test_results"] = None

            except Exception as error:

                st.error(f"Something went wrong: {error}")

                st.session_state["result"] = None
                st.session_state["suggested_tests"] = None
                st.session_state["generated_test_results"] = None


# -----------------------------------------
# DISPLAY AI RESULTS
# -----------------------------------------

result = st.session_state["result"]

if result is not None:

    st.subheader("Your submitted code")
    st.code(result["original_code"], language="python")

    st.subheader("Corrected Python code")

    if result["corrected_code"]:
        st.code(result["corrected_code"], language="python")
    else:
        st.warning("No recognizable Python code block was returned.")

    # -----------------------------------------
    # SYNTAX CHECK
    # -----------------------------------------

    st.subheader("Syntax check")

    if result["syntax_valid"]:
        st.success(result["syntax_message"])
    else:
        st.error(result["syntax_message"])

    # -----------------------------------------
    # AI EXPLANATION
    # -----------------------------------------

    st.subheader("AI's explanation")

    explanation = re.sub(
        r"```(?:python)?\s*.*?```",
        "",
        result["ai_response"],
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    ).strip()

    st.write(explanation or "No explanation was provided.")

    # -----------------------------------------
    # AI-GENERATED TEST SUGGESTIONS
    # -----------------------------------------

    st.divider()
    st.subheader("AI-generated test suggestions")

    st.write(
        "Let the AI suggest test cases for your corrected code. "
        "Review expected results before relying on them."
    )

    if not result["syntax_valid"] or not result["corrected_code"].strip():

        st.warning(
            "Valid corrected code is needed before generating tests."
        )

    elif st.button("Generate test cases"):

        with st.spinner("AI is thinking of useful tests..."):

            try:
                st.session_state["suggested_tests"] = generate_tests(
                    result["corrected_code"]
                )

                # Clear old execution results.
                st.session_state["generated_test_results"] = None

            except Exception as error:
                st.error(f"Could not generate tests: {error}")

    suggestions = st.session_state["suggested_tests"]

    if suggestions is not None:

        if suggestions["success"]:

            tests = suggestions["tests"]

            # Separate tests that need human review.
            runnable_tests = [
                test for test in tests
                if not test.get("needs_review", False)
            ]

            review_count = len(tests) - len(runnable_tests)

            if not tests:
                st.info("The AI didn't suggest any test cases.")

            else:

                st.write(
                    "Review these suggestions. The AI can make mistakes, "
                    "and unclear expected behavior needs your judgment."
                )

                # -----------------------------------------
                # DISPLAY TEST SUGGESTIONS
                # -----------------------------------------

                for index, test in enumerate(tests, start=1):

                    st.markdown(
                        f"**Test {index}: `{test['function_name']}`**"
                    )

                    expected_exception = test.get("expected_exception")

                    if expected_exception:
                        expected_display = (
                            f"Expected exception: {expected_exception}"
                        )
                    else:
                        expected_display = (
                            f"Expected result: {test['expected']}"
                        )

                    st.code(
                        f"Arguments: {test['arguments']}\n"
                        f"{expected_display}",
                        language="text",
                    )

                    if test.get("needs_review", False):
                        st.warning(
                            "Expected behavior is uncertain. "
                            "This test needs human review and "
                            "will not be executed automatically."
                        )

                # -----------------------------------------
                # TEST REVIEW SUMMARY
                # -----------------------------------------

                if review_count:
                    st.info(
                        f"{review_count} test(s) need human review "
                        "and will not be executed automatically."
                    )

                # -----------------------------------------
                # RUN ALL GENERATED TESTS
                # -----------------------------------------

                st.divider()

                if st.button(
                    "Run All Generated Tests",
                    disabled=not runnable_tests,
                ):

                    with st.spinner("Running generated tests..."):

                        try:
                            st.session_state["generated_test_results"] = (
                                run_generated_tests(
                                    result["corrected_code"],
                                    runnable_tests,
                                )
                            )

                        except Exception as error:
                            st.error(f"Could not run tests: {error}")

                # -----------------------------------------
                # DISPLAY GENERATED TEST RESULTS
                # -----------------------------------------

                test_results = st.session_state[
                    "generated_test_results"
                ]

                if test_results is not None:

                    st.subheader("Generated Test Results")

                    passed_count = sum(
                        1 for test in test_results if test["passed"]
                    )

                    failed_count = sum(
                        1 for test in test_results if not test["passed"]
                    )

                    st.write(f"Passed: {passed_count}")
                    st.write(f"Failed: {failed_count}")
                    st.write(f"Needs review: {review_count}")

                    for test in test_results:

                        st.markdown(
                            f"**Test {test['test_number']}: "
                            f"`{test['function_name']}`**"
                        )

                        if test["passed"]:
                            st.success("TEST PASSED")
                        else:
                            st.error("TEST FAILED")

                        st.code(test["output"])

        else:
            st.error(suggestions["message"])

    # -----------------------------------------
    # MANUAL BEHAVIORAL TEST
    # -----------------------------------------

    st.divider()
    st.subheader("Manual behavioral test")

    st.write(
        "You can still enter your own function, arguments, "
        "and expected result below."
    )

    function_name = st.text_input(
        "Function name",
        value="calculate_average",
        key="test_function_name",
    )

    arguments_text = st.text_input(
        "Arguments (JSON list)",
        value="[[1, 2, 3, 4]]",
        help=(
            "Example: [2, 3] passes two arguments. "
            "Use [[2, 4, 6]] to pass one list argument."
        ),
        key="test_arguments",
    )

    expected_text = st.text_input(
        "Expected result (JSON)",
        value="2.5",
        help='Examples: 5, 2.5, true, or "hello".',
        key="test_expected",
    )

    if not result["syntax_valid"]:

        st.warning("Fix the syntax errors before running a test.")

    elif not result["corrected_code"].strip():

        st.warning("There is no corrected code available to test.")

    elif st.button("Run behavioral test"):

        with st.spinner("Running your test..."):

            try:
                test_result = test_function(
                    result["corrected_code"],
                    function_name,
                    arguments_text,
                    expected_text,
                )

                if test_result["passed"]:
                    st.success("Test passed!")
                else:
                    st.error("Test failed!")

                st.code(test_result["output"])

            except Exception as error:
                st.error(f"Test execution failed: {error}")

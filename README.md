# Iterative Code Fix Agent

An AI-powered Python debugging application built with **LangChain, OpenAI, and Streamlit**. The application analyzes Python code, identifies potential bugs, suggests corrections, and generates behavioral tests to evaluate the corrected implementation.

Users can paste Python code directly into the application, review AI-generated corrections, and execute tests to verify the results.

## Features

- **AI-powered debugging:** Analyzes submitted Python code and identifies potential implementation issues.
- **Automatic code correction:** Generates a corrected version of the submitted code.
- **Syntax validation:** Uses Python's AST module to check whether corrected code is syntactically valid.
- **AI-generated test cases:** Generates behavioral tests covering normal inputs and edge cases.
- **Automated test execution:** Executes generated tests using Python subprocesses.
- **Exception testing:** Verifies whether functions raise expected exceptions for invalid inputs.
- **Manual behavioral testing:** Allows users to provide function arguments and expected results to test specific behavior.
- **Test-result reporting:** Displays actual results, expected results, and pass/fail status.
- **Human review:** Allows users to inspect generated test suggestions before relying on their expected behavior.

## ## Tech Stack

- **Python** – Application logic and test execution
- **LangChain** – LLM integration and application components
- **OpenAI API** – AI-powered code analysis, correction, and test generation
- **Streamlit** – Interactive web interface
- **Python AST** – Syntax validation
- **Python subprocess** – Behavioral test execution
- **python-dotenv** – Environment variable and API key management
## Project Structure

```text
Iterative Code Fix Agent/
├── app.py                  # Streamlit user interface
├── agent.py                # AI code correction and testing logic
├── tools.py                # Original file-based agent tools
├── requirements.txt        # Python dependencies
├── .gitignore              # Excludes secrets and generated files
└── README.md               # Project documentation
```

## How It Works

The application follows a code correction and testing workflow:

1. **User input:** The user submits Python code through the Streamlit interface.
2. **Code analysis:** The OpenAI language model analyzes the submitted implementation and identifies potential problems.
3. **Code correction:** The model generates corrected Python code and explains its changes.
4. **Syntax validation:** Python's AST module checks whether the corrected code is syntactically valid.
5. **Test generation:** The language model generates behavioral test cases, including expected results and exceptions.
6. **Test validation:** The application validates the generated test data before execution.
7. **Test execution:** Python executes the test cases in subprocesses and compares actual behavior against expected outcomes.
8. **Result reporting:** The application displays test results, including passed tests, failed tests, and suggestions requiring human review.

The application also supports manually defining test inputs and expected results.

## Example

Consider the following function, which contains an incorrect calculation:

```python
def calculate_average(numbers):
    return sum(numbers) / (len(numbers) + 1)
```

The AI can identify the incorrect denominator and generate a corrected implementation.

For example:

```python
def calculate_average(numbers):
    if not numbers:
        raise ValueError("numbers must contain at least one value")

    return sum(numbers) / len(numbers)
```

The application can then generate behavioral tests to evaluate the corrected implementation.

Example test cases:

| Input | Expected behavior |
|---|---|
| `[1, 2, 3, 4]` | `2.5` |
| `[-5]` | `-5.0` |
| `[-2, 0, 2]` | `0.0` |
| `[]` | `ValueError` |

The expected behavior for edge cases should be reviewed because AI-generated tests and expectations may not always reflect the intended requirements.

## Setup

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd "Iterative Code Fix Agent"
```

Replace `YOUR_REPOSITORY_URL` with your GitHub repository URL.

### 2. Create and activate a virtual environment

On Windows:

```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Create a `.env` file in the project directory:

```text
OPENAI_API_KEY=your_api_key_here
```

Replace the placeholder with your OpenAI API key.

Never commit your `.env` file or expose your API key publicly.

### 5. Run the application

```bash
streamlit run app.py
```

Streamlit will launch the application in your browser.

## Current Limitations

- The application currently focuses on Python code.
- AI-generated corrections and test expectations may be incorrect and require human review.
- Passing generated tests does not guarantee that the implementation is free of bugs.
- Syntax validation confirms valid Python syntax, not correct program behavior.
- Test coverage depends on the quality and variety of generated test cases.
- Test execution uses subprocesses and time limits but is not a secure sandbox. Only run trusted code in a controlled environment.

## Future Improvements

- Expand support for more complex debugging scenarios.
- Improve test generation and edge-case coverage.
- Add more robust error handling and reporting.
- Support larger codebases and multiple source files.
- Improve execution isolation and security.
- Add additional testing and debugging controls.

## Disclaimer

This is an educational project demonstrating AI-powered code correction, LLM integration, and automated behavioral testing. AI-generated code and test results should always be reviewed before use in production.

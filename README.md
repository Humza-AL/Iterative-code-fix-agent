# Iterative Code Fix Agent

An AI-powered Python debugging agent built with LangChain and OpenAI. The agent can inspect source files, identify bugs, modify code, execute tests, and use test results to guide its corrections.

## Features

- **AI-powered debugging:** Analyzes Python code and identifies implementation issues.
- **Tool calling:** Uses custom tools to read files, write code, and execute Python scripts.
- **Automated testing:** Runs a test suite to verify code changes.
- **Iterative corrections:** Uses test feedback to guide further fixes, within configured limits.
- **Controlled file modifications:** Restricts permitted code changes to designated project files.
- **Test-result reporting:** Displays the original code, corrected code, and actual test execution results.
- **Error handling:** Returns tool errors to the agent for inspection.

## Tech Stack

- Python
- LangChain
- OpenAI API
- `python-dotenv`
- Python `unittest`

## Project Structure

```text
Iterative Code Fix Agent/
├── agent.py                  # Agent logic and tool-calling loop
├── tools.py                  # File and Python execution tools
├── buggy_code.py             # Original example implementation
├── buggy_code_working.py     # File the agent attempts to repair
├── agent_tests.py            # Automated tests
├── .gitignore                # Excludes secrets and generated files
├── README.md                 # Project documentation
└── requirements.txt          # Python dependencies
```

## How It Works

1. The agent reads the target Python code and existing tests.
2. The language model analyzes the implementation and determines whether changes are needed.
3. When appropriate, the agent uses tools to modify the code.
4. The test suite runs after a code modification.
5. The agent receives the results and can use them to guide further corrections.
6. The program displays the original implementation, corrected implementation, and final test results.

The agent uses a configurable tool-round limit and a maximum of three writes to the target implementation.

## Example

The original implementation does not handle empty input:

```python
def calculate_average(numbers):
    return sum(numbers) / len(numbers)
```

The corrected implementation handles that edge case:

```python
def calculate_average(numbers):
    """Return the arithmetic mean of numbers, or 0 for an empty list."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
```

For this project, the chosen behavior for an empty list is to return `0`.

## Tests

The automated test suite covers:

| Input | Expected result |
|---|---:|
| `[1, 2, 3, 4]` | `2.5` |
| `[]` | `0` |
| `[-2, 1.5, 3.5]` | `1.0` |

Run the tests manually with:

```bash
python agent_tests.py
```

Run the agent with:

```bash
python agent.py
```

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

Replace the placeholder with your own API key. Never commit your `.env` file or expose your API key publicly.

### 5. Run the project

```bash
python agent.py
```

## Current Limitations

- The example focuses on a small Python function rather than a large codebase.
- Automated tests cover the specified examples, not every possible input or failure scenario.
- The agent's retry and tool-round limits restrict how many actions it can take.
- Executing Python code through a subprocess is not a security sandbox; this project should only run trusted code in a controlled environment.

## Future Improvements

- Expand test coverage for invalid input and additional edge cases.
- Add more robust retry and failure-reporting logic.
- Support additional debugging scenarios and multiple source files.
- Add logging and a user interface for monitoring agent activity.

## Disclaimer

This is an educational project demonstrating tool-using AI agents and automated debugging. Code generated or modified by an AI should always be reviewed before use in production.

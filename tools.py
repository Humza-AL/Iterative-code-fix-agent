from langchain_core.tools import tool

import subprocess
import sys
@tool
def read_file(file_path: str) -> str:
    """Read and return the contents of a file."""
    with open(file_path,"r") as file:
        return file.read()



from pathlib import Path


PROJECT_DIR = Path(__file__).parent.resolve()


@tool
def write_file(file_path: str, content: str) -> str:
    """Write text content to a file inside the project folder."""

    target_path = (PROJECT_DIR / file_path).resolve()

    if target_path != PROJECT_DIR and PROJECT_DIR not in target_path.parents:
        raise ValueError("File must be inside the project folder.")

    target_path.write_text(content, encoding="utf-8")

    return f"Successfully wrote to {file_path}"



@tool
def run_python(file_path: str) -> str:
    """Run a Python file in the project folder and return its output or error."""

    target_path = (PROJECT_DIR / file_path).resolve()

    if target_path != PROJECT_DIR and PROJECT_DIR not in target_path.parents:
        raise ValueError("File must be inside the project folder.")

    result = subprocess.run(
        [sys.executable, str(target_path)],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(PROJECT_DIR)
    )

    return (
        f"Exit code: {result.returncode}\n"
        f"Output:\n{result.stdout}\n"
        f"Errors:\n{result.stderr}"
    )



from tools import run_python

result = run_python.invoke({
    "file_path": "buggy_code.py"
})

print(result)
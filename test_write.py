
from tools import write_file

result = write_file.invoke({
    "file_path": "test_output.txt",
    "content": "Hello! My AI agent can write files."
})

print(result)
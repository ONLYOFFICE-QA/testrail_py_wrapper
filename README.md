# TestRail Wrapper

TestRail Wrapper is a tool for interacting with the
TestRail API which provides a set of methods for managing
projects, sets, sections, plans, runs and test cases in TestRail.

## Configuration

Create a configuration file `~/.testrail/testrail_config.json`.
The configuration file should include the following fields:

```json
{
  "url": "https://your-testrail-instance-url",
  "user": "your-username",
  "password": "your-password"
}
```

## Example Usage

Add a Result to a Test Case

```python
from testrail_py_wrapper import TestManager


test_manager = TestManager()

result = {
    "status_id": 1, # 1 - Passed, 2 - Blocked, 3 - Untested, 4 - Retest, 5 - Failed
    "comment": "Test passed successfully."
}


await test_manager.add_result_to_case(
    "Test Project", # Project name
    "8.2.0 (build:34)", # Plan name
    "All Values of Image Formats", # Suite name
    "Check supported <bmp> Image Format", # Case name
    result
)
```

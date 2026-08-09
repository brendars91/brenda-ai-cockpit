```markdown
---
name: grep_search
description: Skill for searching files using regular expressions with the `grep` command. Provides capabilities for pattern matching, file filtering, and result extraction.
version: 1.0.0
auto_generated: true
---

# grep_search

## Purpose

This skill provides an interface to the `grep` command-line utility, enabling the AI agent to search for specific patterns within files. It allows for complex searches using regular expressions, filtering results, and extracting relevant information from the matched lines. This skill is essential for tasks such as log analysis, code review, configuration file parsing, and data extraction.

## Usage

This skill is intended to be invoked by other skills or directly by the AI agent when pattern-based file searching is required.  The skill encapsulates the execution of the `grep` command and provides a structured interface for specifying search parameters and retrieving results.

## Actions

This skill exposes a single action: `search_files`.

### Action: `search_files`

**Description:** Searches files for a specified pattern using `grep`.

**Parameters:**

| Name          | Type    | Required | Description                                                                                                                                                                                                                                                                                                                                   |
|---------------|---------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `pattern`     | string  | Yes      | The regular expression pattern to search for.  Must be a valid regular expression recognized by `grep`.  Escaping of special characters may be necessary depending on the shell environment. See "Regular Expression Considerations" section for details.                                                                                                                                       |
| `files`       | string  | Yes      | A space-separated list of file paths to search within.  Supports globbing (e.g., `*.log`, `/var/log/*.log`). Relative paths are interpreted relative to the agent's current working directory. Use absolute paths for clarity and robustness.  See "File Path Handling" section for details.                                                                  |
| `options`     | string  | No       | Additional command-line options for `grep`.  Use with caution, as incorrect options can lead to unexpected behavior.  Commonly used options include: `-i` (case-insensitive search), `-v` (invert match), `-r` or `-R` (recursive search), `-l` (list file names only), `-n` (show line numbers), `-w` (match whole words only). See "Options Handling" for limitations. |
| `max_lines`   | integer | No       | Limits the number of lines returned from the grep output. This is important for preventing the agent from being overwhelmed by extremely large outputs and for managing resource usage. Defaults to 100. Must be a positive integer.                                                                                                                     |
| `context_lines` | integer | No       |  Displays `context_lines` lines of leading and trailing context around each match. Equivalent to the `-C` option in `grep`. Overrides `before_context_lines` and `after_context_lines` if set. Must be a non-negative integer.  Defaults to 0 (no context).                                                                                                |
| `before_context_lines` | integer | No       | Displays `before_context_lines` lines of leading context before each match. Equivalent to the `-B` option in `grep`. Only effective if `context_lines` is not set. Must be a non-negative integer. Defaults to 0 (no leading context).                                                                                                                      |
| `after_context_lines` | integer | No       | Displays `after_context_lines` lines of trailing context after each match. Equivalent to the `-A` option in `grep`. Only effective if `context_lines` is not set. Must be a non-negative integer. Defaults to 0 (no trailing context).                                                                                                                     |

**Returns:**

A dictionary containing the following keys:

| Name      | Type    | Description                                                                                                                                                                                                                                 |
|-----------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `success` | boolean | `true` if the `grep` command executed successfully (returned a zero exit code), `false` otherwise.                                                                                                                                  |
| `output`  | string  | The output of the `grep` command, limited to `max_lines` lines.  If the command fails, this will contain the error message from `stderr`. If `context_lines`, `before_context_lines`, or `after_context_lines` are set, the context lines are included in the output.  Lines are separated by newline characters (`\n`). |
| `error`   | string  |  Any error message generated by the execution of the `grep` command (from `stderr`). Empty string if no error occurred.                                                                                                                                                 |
| `return_code` | integer | The exit code of the `grep` command. 0 indicates success, non-zero indicates an error.                                                                                                                                                     |
| `files_searched` | list | A list of files that were actually searched by `grep`.  This is useful when using globbing to confirm which files were included in the search.                                                                                          |

**Example Usage:**

```python
# Example 1: Simple search for "error" in a log file.
response = grep_search.search_files(pattern="error", files="/var/log/syslog")
if response["success"]:
    print(response["output"])
else:
    print(f"Error: {response['error']}")

# Example 2: Case-insensitive search for "warning" in all .log files in the current directory.
response = grep_search.search_files(pattern="warning", files="*.log", options="-i")
if response["success"]:
    print(response["output"])
else:
    print(f"Error: {response['error']}")

# Example 3: Search for a specific IP address in a configuration file and include line numbers.
response = grep_search.search_files(pattern="192.168.1.100", files="/etc/network/interfaces", options="-n")
if response["success"]:
    print(response["output"])
else:
    print(f"Error: {response['error']}")

# Example 4: Limit the number of returned lines to 50.
response = grep_search.search_files(pattern="Exception", files="application.log", max_lines=50)

# Example 5:  Include 2 lines of context around each match.
response = grep_search.search_files(pattern="Critical Error", files="debug.log", context_lines=2)

# Example 6: Include 1 line of leading context.
response = grep_search.search_files(pattern="Login Failed", files="auth.log", before_context_lines=1)

# Example 7:  Include 1 line of trailing context.
response = grep_search.search_files(pattern="Logout Successful", files="auth.log", after_context_lines=1)
```

## Implementation Details

The `grep_search` skill executes the `grep` command using a system call. It captures both the standard output (`stdout`) and standard error (`stderr`) streams. The `success` flag is determined by the exit code of the `grep` command. The `output` field contains the contents of `stdout`, truncated to `max_lines` lines. The `error` field contains the contents of `stderr` if the command fails. The files that were searched by grep are determined by expanding any globs provided in the `files` argument and checking for file existence.

## Regular Expression Considerations

*   The `pattern` parameter must be a valid regular expression compatible with the `grep` implementation on the target system (typically POSIX Extended Regular Expressions).
*   Special characters in regular expressions (e.g., `.`, `*`, `?`, `+`, `^`, `$`, `[`, `]`, `\`, `|`, `(`, `)`) may need to be escaped with a backslash (`\`) to prevent them from being interpreted by the shell before being passed to `grep`.
*   Consider using raw strings (e.g., `r"pattern"`) in Python to avoid excessive escaping of backslashes.
*   If the `pattern` contains spaces or other shell metacharacters, it should be enclosed in single quotes to prevent shell interpretation.
*   For complex regular expressions, it is recommended to test them thoroughly before using them in the skill.

**Example:**

To search for the literal string "a.b", the `pattern` should be `a\.b` or `r"a\.b"`. To search for lines starting with the word "Error", the pattern should be `^Error`.

## File Path Handling

*   The `files` parameter should be a space-separated list of file paths.
*   Globbing (e.g., `*.log`, `/var/log/*.log`) is supported, allowing for searching multiple files with a single command.
*   Relative paths are interpreted relative to the agent's current working directory.
*   Absolute paths are recommended for clarity and to avoid ambiguity.
*   If a file path does not exist, `grep` will typically issue a warning message on `stderr`, which will be captured in the `error` field of the response. However, the `success` flag will still be `true` if `grep` was able to process other files in the list.
*   The skill expands any globs provided in the `files` argument using the system's globbing functionality.
*   The `files_searched` field in the return value lists the actual files that grep attempted to search.

**Example:**

To search all `.txt` files in the `/home/user/documents` directory, the `files` parameter should be `/home/user/documents/*.txt`.

## Options Handling

*   The `options` parameter allows for passing additional command-line options to `grep`.
*   Use this parameter with caution, as incorrect options can lead to unexpected behavior or security vulnerabilities.
*   The skill does not validate the options passed to `grep`. It is the responsibility of the calling skill or agent to ensure that the options are valid and safe.
*   Avoid options that could potentially cause `grep` to hang indefinitely or consume excessive resources.
*   Consider whitelisting specific options that are known to be safe and useful.

**Commonly Used Options:**

*   `-i`: Case-insensitive search.
*   `-v`: Invert match (show lines that do not match the pattern).
*   `-r` or `-R`: Recursive search (search within subdirectories). Be very careful when using this option as it can lead to an extremely large number of files being searched, potentially causing the agent to run out of time or resources. Limit the scope of the search as much as possible.
*   `-l`: List file names only (show only the names of files that contain the pattern).
*   `-n`: Show line numbers.
*   `-w`: Match whole words only.
*   `-c`: Print only a count of matching lines per file.

**Example:**

To perform a case-insensitive search and show line numbers, the `options` parameter should be `-i -n`.

## Error Handling

*   If the `grep` command fails (returns a non-zero exit code), the `success` flag will be `false`, and the `error` field will contain the error message from `stderr`.
*   The `return_code` field will contain the actual exit code of the `grep` command.
*   It is important to check the `success` flag and the `error` field after calling the `search_files` action to handle potential errors.

**Common Error Scenarios:**

*   Invalid regular expression: The `pattern` parameter is not a valid regular expression.
*   File not found: One or more of the specified files do not exist.
*   Permission denied: The agent does not have permission to read one or more of the specified files.
*   Invalid option: An invalid option is passed in the `options` parameter.
*   Grep not installed: The `grep` command is not installed on the system.  This will result in a "command not found" error.

## Security Considerations

*   Carefully validate and sanitize the `pattern` and `files` parameters to prevent command injection vulnerabilities. Avoid allowing user-supplied data to be directly inserted into these parameters without proper validation.
*   Limit the scope of the search to prevent the agent from accessing sensitive files. Use absolute paths and avoid using wildcard characters unnecessarily.
*   Be cautious when using the `-r` or `-R` option for recursive searching, as it can potentially expose the agent to a large number of files.
*   Monitor the resource usage of the `grep` command to prevent denial-of-service attacks. Use the `max_lines` parameter to limit the amount of output returned.
*   Consider running the `grep` command in a sandboxed environment to further isolate it from the rest of the system.
*   Avoid using options that could potentially execute arbitrary code (e.g., `-e` with a carefully crafted pattern).

## Best Practices

*   Use absolute paths for files whenever possible to avoid ambiguity and ensure that the correct files are being searched.
*   Test regular expressions thoroughly before using them in the skill.
*   Limit the scope of the search as much as possible to improve performance and reduce the risk of exposing sensitive information.
*   Use the `max_lines` parameter to prevent the agent from being overwhelmed by large outputs.
*   Check the `success` flag and the `error` field after calling the `search_files` action to handle potential errors.
*   Document the usage of the skill and provide examples of how to use it effectively.
*   Implement rate limiting to prevent the skill from being abused.
*   Monitor the skill's performance and resource usage to identify potential bottlenecks.

## Limitations

*   This skill relies on the availability of the `grep` command-line utility on the target system.
*   The skill does not provide any built-in regular expression validation.
*   The skill does not support advanced `grep` features such as binary file searching or custom output formatting.
*   Globbing is performed by the system shell, and the behavior may vary depending on the shell configuration.
*   The `max_lines` parameter limits the number of lines returned in the `output` field, but it does not limit the amount of data processed by the `grep` command. Grep will still process the entire file even if only a limited number of lines are returned. For extremely large files, consider other approaches like splitting the file into smaller chunks.
```
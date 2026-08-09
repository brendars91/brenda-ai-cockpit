```markdown
---
name: linter
description: Skill for performing static code analysis and identifying potential issues in source code. This includes enforcing coding style guidelines, detecting common errors, and suggesting improvements. It's designed for integration with CI/CD pipelines, IDEs, and automated code review processes. Supports multiple languages via configuration.
version: 1.0.0
auto_generated: false
---

# linter

## Purpose

This skill provides a robust and configurable linting capability, allowing the agent to analyze code snippets for style violations, potential bugs, and security vulnerabilities. It enables automated code quality checks, ensuring adherence to coding standards and best practices.

## Inputs

The skill requires the following inputs:

*   `code`: (string, required) The source code to be linted.
*   `language`: (string, required) The programming language of the code (e.g., "python", "javascript", "java", "go", "c++", "csharp", "typescript"). This is case-insensitive.
*   `config`: (string, optional) A string representing the linter configuration file.  The format depends on the linter being used (e.g., `.eslintrc.js` for ESLint, `pyproject.toml` for Flake8, `.clang-format` for clang-format). If omitted, a default configuration for the specified language will be used.  Provide the complete configuration file content as a string, not a file path.
*   `linter_name`: (string, optional) The name of the linter to use (e.g., "eslint", "flake8", "clang-format", "pylint"). If omitted, a default linter for the specified language will be used.  Supported linters are listed below. This allows overriding the default linter for a language.
*   `working_directory`: (string, optional) The directory to execute the linter in. This is important when the linter needs to access project-specific configuration files or dependencies. If not provided, the linter will execute in a temporary directory.
*   `fail_on_error`: (boolean, optional, default: true) Whether to raise an error if the linter finds any issues. If set to `false`, the linter will still report the findings but will not interrupt the process. This is useful for non-critical linting tasks.

## Outputs

The skill returns a JSON object with the following fields:

*   `status`: (string) "success" if the linting process completed successfully (even if issues were found), "error" if an error occurred during linting.
*   `report`: (string) A detailed report of any issues found by the linter, formatted as plain text. If no issues were found, the report will indicate that the code passed the linting process.  The specific format depends on the linter used.  It includes the line number, column number, error/warning code, and a description of the issue.
*   `error`: (string, optional) An error message if the `status` is "error". This provides details about why the linting process failed (e.g., invalid configuration, linter not found).
*   `linter_used`: (string) The name of the linter that was actually used.  This is useful when the `linter_name` input is omitted and the default linter is used.

## Supported Languages and Default Linters

The skill supports the following languages and uses the following default linters:

*   **Python:** `flake8`
*   **JavaScript:** `eslint`
*   **TypeScript:** `eslint`
*   **Java:** `checkstyle`
*   **Go:** `golangci-lint`
*   **C++:** `clang-format` (primarily for formatting, but can detect some issues) and `cppcheck` (for static analysis)
*   **C#:** `dotnet format` (for formatting) and `Roslynator` (for static analysis)
*   **PHP:** `phpcs`

These defaults can be overridden using the `linter_name` input.  You are responsible for ensuring the requested `linter_name` is installed and available in the execution environment.

## Actions

The skill performs the following actions:

1.  **Receives Inputs:**  Retrieves the code, language, and optional configuration from the agent.
2.  **Selects Linter:** Determines the appropriate linter to use based on the language and the optional `linter_name` input. If no `linter_name` is specified, the default linter for the language is selected.
3.  **Creates Temporary File:** Creates a temporary file with the provided code, using the appropriate file extension for the specified language.
4.  **Creates Configuration File (Optional):** If a `config` input is provided, creates a temporary configuration file with the specified content.  The file name is determined by the linter being used (e.g., `.eslintrc.js` for ESLint, `pyproject.toml` for Flake8). If no `config` is specified, the linter will use its default configuration or a predefined project-level configuration file (if one exists in the `working_directory`).
5.  **Executes Linter:** Executes the selected linter on the temporary file, passing in the temporary configuration file (if applicable) and the specified working directory.
6.  **Captures Output:** Captures the output of the linter (both standard output and standard error).
7.  **Parses Output:** Parses the linter's output to extract information about any issues found, including the line number, column number, error code, and description.
8.  **Generates Report:** Generates a detailed report of any issues found by the linter, including the line number, column number, error code, and description.
9.  **Returns Results:** Returns a JSON object containing the status, report, error (if any), and the name of the linter used.

## Error Handling

The skill handles the following errors:

*   **Invalid Language:** Returns an error if the specified language is not supported.
*   **Linter Not Found:** Returns an error if the specified linter is not found in the execution environment. This often happens if `linter_name` is specified but the linter isn't installed.
*   **Invalid Configuration:** Returns an error if the provided configuration file is invalid or contains syntax errors.  The linter's error message will be included in the `error` output.
*   **Linting Error:** Returns an error if the linter encounters an error during the linting process (e.g., a syntax error in the code that prevents the linter from parsing it).
*   **File System Errors:** Returns an error if there are problems creating temporary files or writing configuration files.

If `fail_on_error` is set to `true` (the default), any of these errors will cause the skill to return a `status` of "error". If `fail_on_error` is set to `false`, the skill will return a `status` of "success" even if errors occur, but the `report` will include the error messages.

## Examples

### Example 1: Linting Python code with Flake8 using the default configuration

```json
{
  "code": "def my_function(a,b):\n  return a+ b",
  "language": "python"
}
```

**Expected Output:**

```json
{
  "status": "success",
  "report": "my_file.py:2:1: E302 expected 2 blank lines, found 1\nmy_file.py:1:1: W291 trailing whitespace",
  "linter_used": "flake8"
}
```

### Example 2: Linting JavaScript code with ESLint using a custom configuration

```json
{
  "code": "function foo() {\n  console.log('Hello');\n}",
  "language": "javascript",
  "config": "module.exports = {\n  rules: {\n    'semi': ['error', 'always']\n  }\n};",
  "linter_name": "eslint"
}
```

**Expected Output:**

```json
{
  "status": "success",
  "report": "my_file.js:2:23: error  Missing semicolon  semi",
  "linter_used": "eslint"
}
```

### Example 3: Linting Go code with `golangci-lint` and failing on error

```json
{
  "code": "package main\n\nimport \"fmt\"\n\nfunc main() {\n\tx := 1\n\tfmt.Println(x)\n}",
  "language": "go"
}
```

**Expected Output:**

```json
{
  "status": "success",
  "report": "my_file.go:7:2: varcheck: `x` is unused (varcheck)\n",
  "linter_used": "golangci-lint"
}
```

### Example 4: Linting C++ code with `clang-format`

```json
{
    "code": "#include <iostream>\n\nint main() {\nint i = 0;\nstd::cout << i << std::endl;\nreturn 0;\n}",
    "language": "c++",
    "linter_name": "clang-format"
}
```

**Expected Output (formatted code snippet may vary depending on the default clang-format configuration):**

```json
{
  "status": "success",
  "report": "#include <iostream>\n\nint main() {\n  int i = 0;\n  std::cout << i << std::endl;\n  return 0;\n}",
  "linter_used": "clang-format"
}
```

### Example 5: Linting with `fail_on_error` set to `false`

```json
{
    "code": "def my_function(a,b):\n  return a+ b",
    "language": "python",
    "fail_on_error": false
}
```

**Expected Output:**

```json
{
    "status": "success",
    "report": "my_file.py:2:1: E302 expected 2 blank lines, found 1\nmy_file.py:1:1: W291 trailing whitespace",
    "linter_used": "flake8"
}
```

### Example 6: Specifying a working directory

```json
{
  "code": "print('hello')",
  "language": "python",
  "working_directory": "/path/to/project"
}
```

In this example, if the `/path/to/project` directory contains a `pyproject.toml` file with Flake8 configuration, that configuration will be used. Otherwise, Flake8's default configuration will be used.  The agent needs read access to the files in the working directory.

## Best Practices

*   **Specify the language accurately:**  The skill relies on the `language` input to determine the correct linter to use. Incorrect language identification can lead to unexpected results or errors.
*   **Provide a configuration file:** To enforce specific coding standards, provide a configuration file that customizes the linter's behavior. This ensures consistency across projects.  Use the `config` input.
*   **Handle errors gracefully:** Check the `status` output to determine if the linting process completed successfully. If an error occurred, examine the `error` output for details.
*   **Use a working directory when necessary:**  If the linter needs to access project-specific configuration files or dependencies, provide a `working_directory`. This is crucial for projects with custom linting rules or complex dependencies.
*   **Install required linters:** Ensure that the linters specified in the `linter_name` input are installed and available in the execution environment.
*   **Set `fail_on_error` appropriately:** If you want the agent to stop when linting errors are found, leave `fail_on_error` at its default value of `true`. If you want the agent to continue even if linting errors are found (e.g., for non-critical style checks), set `fail_on_error` to `false`.
*   **Escape special characters in configuration files:** Ensure that any special characters in the `config` string are properly escaped to avoid parsing errors.  This is especially important for JSON configuration files.

## Security Considerations

*   **Code Injection:** Be extremely careful when using this skill to lint code from untrusted sources.  A malicious code snippet could potentially exploit vulnerabilities in the linter itself. It is best to run this skill in a sandboxed environment.
*   **Configuration Injection:**  Similarly, a malicious configuration file could be used to compromise the linter.  Avoid using configuration files from untrusted sources.  Consider validating configuration files before passing them to the linter.
*   **File System Access:**  The `working_directory` input allows the linter to access files on the file system.  Ensure that the agent has appropriate permissions to access only the necessary files and directories. Avoid providing a `working_directory` if it is not required.
```
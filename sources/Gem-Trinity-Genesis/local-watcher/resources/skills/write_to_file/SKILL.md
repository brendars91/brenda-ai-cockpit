```markdown
---
name: write_to_file
description: Skill for writing content to a file. Supports creating new files or appending/overwriting existing ones. Handles various encoding scenarios and provides error handling.
version: 1.0.0
auto_generated: true
---

# write_to_file

## Purpose

This skill allows the AI agent to write content to files on the file system. It supports creating new files, overwriting existing files, and appending to existing files. The skill is designed to be robust, handling various edge cases such as file encoding, permission issues, and file existence checks.

## Usage

This skill is typically called by other skills or directly by the AI agent to persist data, save results of computations, or generate configuration files.

## Arguments

| Argument        | Type    | Description                                                                                                                    | Required | Default Value |
|-----------------|---------|--------------------------------------------------------------------------------------------------------------------------------|----------|---------------|
| `filepath`      | string  | The absolute or relative path to the file to be written to.                                                                      | Yes      | None          |
| `content`       | string  | The content to be written to the file.                                                                                           | Yes      | None          |
| `mode`          | string  | The file writing mode. Valid options are: `overwrite`, `append`, `create`. Defaults to `overwrite` if the file exists, `create` if it doesn't.| No       | `overwrite` if file exists, `create` if not |
| `encoding`      | string  | The character encoding to use when writing to the file. Common options include `utf-8`, `ascii`, `latin-1`.                     | No       | `utf-8`       |
| `create_parents`| boolean | If `true`, creates parent directories if they don't exist. If `false` and parent directories are missing, the operation fails.  | No       | `false`        |

### Argument Details

*   **filepath**: The `filepath` should be a valid path accessible by the AI agent. Absolute paths are recommended for clarity and to avoid ambiguity.

*   **content**: The `content` is the string data that will be written to the file. It can be any text, including JSON, XML, or other structured data.

*   **mode**: The `mode` argument controls how the file is written to.
    *   `overwrite`:  If the file exists, its contents are completely replaced with the new `content`. If the file doesn't exist, a new file is created.
    *   `append`: If the file exists, the new `content` is added to the end of the existing file. If the file doesn't exist, a new file is created.
    *   `create`: If the file exists, the operation fails with an error. If the file doesn't exist, a new file is created. This is useful when you specifically want to ensure that you are not accidentally overwriting an existing file.

*   **encoding**: The `encoding` specifies the character encoding to use when writing the file.  Using the correct encoding ensures that the file is readable and interpretable by other programs. Common encodings include `utf-8` (recommended for most cases), `ascii`, and `latin-1`.  If you're dealing with international characters or special symbols, `utf-8` is almost always the correct choice.

*   **create_parents**: The `create_parents` option enables the creation of any necessary parent directories in the `filepath`. If set to `true` and the specified path includes directories that do not exist, the skill will attempt to create those directories. If set to `false` and the parent directories do not exist, the file writing operation will fail.

## Return Value

The skill returns a JSON object with the following structure:

```json
{
  "success": boolean,
  "message": string,
  "filepath": string,
  "bytes_written": integer | null,
  "error": string | null
}
```

*   **success**: `true` if the file was written successfully, `false` otherwise.
*   **message**: A human-readable message indicating the result of the operation.
*   **filepath**: The path to the file that was written to.
*   **bytes_written**: The number of bytes written to the file. Returns `null` if the operation failed.
*   **error**:  An error message if the operation failed.  `null` if the operation was successful.

## Error Handling

The skill handles various error conditions, including:

*   **File Not Found**:  If the specified file path does not exist and `create_parents` is `false`, an error will be returned.
*   **Permission Denied**:  If the AI agent does not have sufficient permissions to write to the specified file or directory, an error will be returned.
*   **Invalid Encoding**:  If the specified encoding is invalid or unsupported, an error will be returned.
*   **File Already Exists (mode='create')**: If `mode` is set to `create` and the file already exists, an error will be returned.
*   **Disk Full**: If there is insufficient disk space to write the file, an error will be returned.

The `error` field in the return value will contain a descriptive error message in case of failure.

## Examples

### Example 1: Creating a new file

```json
{
  "filepath": "/tmp/my_new_file.txt",
  "content": "This is the content of my new file.",
  "mode": "create"
}
```

**Expected Response:**

```json
{
  "success": true,
  "message": "File created and written to successfully.",
  "filepath": "/tmp/my_new_file.txt",
  "bytes_written": 37,
  "error": null
}
```

### Example 2: Appending to an existing file

```json
{
  "filepath": "/tmp/existing_file.txt",
  "content": "This is some additional content.",
  "mode": "append"
}
```

**Expected Response (assuming the file exists and is writable):**

```json
{
  "success": true,
  "message": "File appended to successfully.",
  "filepath": "/tmp/existing_file.txt",
  "bytes_written": 31,
  "error": null
}
```

### Example 3: Overwriting an existing file

```json
{
  "filepath": "/tmp/existing_file.txt",
  "content": "This is the new content, overwriting the old.",
  "mode": "overwrite"
}
```

**Expected Response (assuming the file exists and is writable):**

```json
{
  "success": true,
  "message": "File overwritten successfully.",
  "filepath": "/tmp/existing_file.txt",
  "bytes_written": 41,
  "error": null
}
```

### Example 4: Creating a file with parent directories

```json
{
  "filepath": "/tmp/my_new_directory/another_directory/my_new_file.txt",
  "content": "This is the content of my new file.",
  "mode": "create",
  "create_parents": true
}
```

**Expected Response (assuming the parent directories don't exist and the AI agent has permissions to create them):**

```json
{
  "success": true,
  "message": "File created and written to successfully. Parent directories created.",
  "filepath": "/tmp/my_new_directory/another_directory/my_new_file.txt",
  "bytes_written": 37,
  "error": null
}
```

### Example 5: Handling an error (file already exists when mode is 'create')

```json
{
  "filepath": "/tmp/existing_file.txt",
  "content": "This should not be written.",
  "mode": "create"
}
```

**Expected Response (assuming the file already exists):**

```json
{
  "success": false,
  "message": "File creation failed.",
  "filepath": "/tmp/existing_file.txt",
  "bytes_written": null,
  "error": "File already exists."
}
```

### Example 6: Using a specific encoding

```json
{
  "filepath": "/tmp/unicode_file.txt",
  "content": "你好世界",
  "mode": "create",
  "encoding": "utf-8"
}
```

**Expected Response:**

```json
{
  "success": true,
  "message": "File created and written to successfully.",
  "filepath": "/tmp/unicode_file.txt",
  "bytes_written": 12,  // Assuming UTF-8 encoding, each Chinese character is 3 bytes
  "error": null
}
```

## Best Practices

*   **Use Absolute Paths**: Whenever possible, use absolute paths for the `filepath` argument to avoid ambiguity and ensure that the file is written to the intended location.
*   **Specify Encoding**:  Always specify the `encoding` argument, especially when dealing with non-ASCII characters.  `utf-8` is generally the safest choice.
*   **Check for Errors**: Always check the `success` field in the return value and handle any errors appropriately.  Inspect the `error` field for detailed error messages.
*   **Use `create_parents` with Caution**: While `create_parents` can be convenient, be careful when using it, as it can potentially create unexpected directory structures. Consider whether the AI agent should have the authority to create directories arbitrarily.
*   **Handle Permissions**:  Ensure that the AI agent has the necessary permissions to write to the specified file and directory.
*   **Avoid Race Conditions**:  If multiple agents or processes might be writing to the same file concurrently, consider implementing locking mechanisms to prevent race conditions and data corruption.  This skill does not provide built-in locking.
*   **Sanitize Input**: If the `content` is derived from user input or external sources, sanitize it to prevent potential security vulnerabilities, such as code injection.  This skill only writes the provided content and does not perform any automatic sanitization.
*   **Consider File Size Limits**: Be mindful of potential file size limits on the system. Writing extremely large files can lead to performance issues or disk space exhaustion.
*   **Use Meaningful File Names**: Employ clear and descriptive file names to enhance the auditability of the AI agent's actions.

## Security Considerations

*   **Path Traversal**:  Carefully validate the `filepath` argument to prevent path traversal vulnerabilities.  Ensure that the AI agent cannot write to files outside of its intended working directory. Consider using a whitelist of allowed directories.
*   **Overwriting System Files**:  Implement safeguards to prevent the AI agent from accidentally overwriting critical system files or configuration files.
*   **Log Sensitive Data**:  Avoid logging sensitive data, such as passwords or API keys, to files. Implement appropriate data masking or encryption techniques.
*   **Limit Agent Permissions**: Adhere to the principle of least privilege by granting the AI agent only the necessary file system permissions.
```
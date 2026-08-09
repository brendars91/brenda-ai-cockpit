```markdown
---
name: filesystem
description: Skill for interacting with the file system. Includes operations like reading, writing, creating, deleting, and listing files and directories.
version: 1.0.0
auto_generated: true
---

# filesystem

## Purpose
Provides a set of actions for interacting with the underlying file system, enabling the AI agent to manage files and directories.

## Usage
This skill is designed to be called by other skills or directly by the AI agent to perform file system operations. It offers functionalities for reading, writing, creating, deleting, listing, and checking the existence of files and directories.

## Actions

This skill exposes the following actions:

*   **read_file**: Reads the content of a file.
*   **write_file**: Writes content to a file.
*   **create_file**: Creates a new file.
*   **delete_file**: Deletes a file.
*   **create_directory**: Creates a new directory.
*   **delete_directory**: Deletes a directory.
*   **list_files**: Lists files and directories within a given directory.
*   **file_exists**: Checks if a file or directory exists.
*   **get_file_size**: Gets the size of a file in bytes.

## Action Details

### 1. read_file

**Description**: Reads the content of a file.

**Parameters**:

*   `filepath` (string, required): The absolute or relative path to the file to be read.

**Return Value**:

*   `content` (string): The content of the file.  Returns an empty string if the file does not exist or if an error occurs.
*   `success` (boolean): True if the read operation was successful, False otherwise.
*   `error` (string, optional):  An error message if the read operation failed.

**Example**:

```python
import os

def read_file(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return {"content": content, "success": True}
    except FileNotFoundError:
        return {"content": "", "success": False, "error": f"File not found: {filepath}"}
    except Exception as e:
        return {"content": "", "success": False, "error": str(e)}

# Example usage:
file_content = read_file("my_document.txt")
if file_content["success"]:
    print(f"File content: {file_content['content']}")
else:
    print(f"Error reading file: {file_content['error']}")

file_content = read_file("/path/to/nonexistent_file.txt")
if file_content["success"]:
    print(f"File content: {file_content['content']}") # This won't print because success is false
else:
    print(f"Error reading file: {file_content['error']}") # This will print the FileNotFoundError
```

**Best Practices**:

*   Always check the `success` flag before using the `content`.
*   Handle potential `FileNotFoundError` exceptions.
*   Consider adding a maximum file size limit to prevent reading excessively large files into memory.
*   Specify the character encoding (e.g., `utf-8`) when reading the file, especially for non-ASCII text.

### 2. write_file

**Description**: Writes content to a file.

**Parameters**:

*   `filepath` (string, required): The absolute or relative path to the file to be written to.
*   `content` (string, required): The content to be written to the file.
*   `append` (boolean, optional, default=False):  If True, the content is appended to the end of the file. If False, the file is overwritten.

**Return Value**:

*   `success` (boolean): True if the write operation was successful, False otherwise.
*   `error` (string, optional): An error message if the write operation failed.

**Example**:

```python
def write_file(filepath, content, append=False):
    try:
        mode = 'a' if append else 'w'
        with open(filepath, mode) as f:
            f.write(content)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Example usage:
write_result = write_file("output.txt", "Hello, world!")
if write_result["success"]:
    print("File written successfully.")
else:
    print(f"Error writing file: {write_result['error']}")

write_result = write_file("output.txt", " This is appended text.", append=True)
if write_result["success"]:
    print("File appended successfully.")
else:
    print(f"Error appending file: {write_result['error']}")
```

**Best Practices**:

*   Handle potential exceptions like `IOError` and `OSError`.
*   Consider adding a maximum file size limit to prevent writing excessively large files.
*   Specify the character encoding (e.g., `utf-8`) when writing to the file, especially for non-ASCII text.
*   Be mindful of file permissions when writing to files in protected directories.
*   Use appropriate locking mechanisms if multiple processes or threads might be writing to the same file concurrently.

### 3. create_file

**Description**: Creates a new file.

**Parameters**:

*   `filepath` (string, required): The absolute or relative path to the file to be created.

**Return Value**:

*   `success` (boolean): True if the file creation was successful, False otherwise.
*   `error` (string, optional): An error message if the file creation failed.

**Example**:

```python
import os

def create_file(filepath):
    try:
        open(filepath, 'x').close()  # 'x' mode creates the file, raising an error if it exists
        return {"success": True}
    except FileExistsError:
        return {"success": False, "error": f"File already exists: {filepath}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Example usage:
create_result = create_file("new_file.txt")
if create_result["success"]:
    print("File created successfully.")
else:
    print(f"Error creating file: {create_result['error']}")

create_result = create_file("new_file.txt") # Trying to create the same file again.
if create_result["success"]:
    print("File created successfully.")
else:
    print(f"Error creating file: {create_result['error']}") #This will print FileExistsError
```

**Best Practices**:

*   Handle potential exceptions like `FileExistsError` if the file already exists.
*   Check for sufficient permissions before attempting to create the file.
*   Consider creating intermediate directories if they don't exist.
*   Implement retry logic for transient errors like network issues.

### 4. delete_file

**Description**: Deletes a file.

**Parameters**:

*   `filepath` (string, required): The absolute or relative path to the file to be deleted.

**Return Value**:

*   `success` (boolean): True if the file deletion was successful, False otherwise.
*   `error` (string, optional): An error message if the file deletion failed.

**Example**:

```python
import os

def delete_file(filepath):
    try:
        os.remove(filepath)
        return {"success": True}
    except FileNotFoundError:
        return {"success": False, "error": f"File not found: {filepath}"}
    except PermissionError:
        return {"success": False, "error": f"Permission denied to delete: {filepath}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Example usage:
delete_result = delete_file("new_file.txt")
if delete_result["success"]:
    print("File deleted successfully.")
else:
    print(f"Error deleting file: {delete_result['error']}")

delete_result = delete_file("nonexistent_file.txt")
if delete_result["success"]:
    print("File deleted successfully.")
else:
    print(f"Error deleting file: {delete_result['error']}") # This will print FileNotFoundError
```

**Best Practices**:

*   Handle potential exceptions like `FileNotFoundError` and `PermissionError`.
*   Implement a confirmation mechanism or a trash/recycle bin for deleted files to prevent accidental data loss.
*   Log file deletions for auditing purposes.
*   Be extremely cautious when deleting files in critical system directories.

### 5. create_directory

**Description**: Creates a new directory.

**Parameters**:

*   `filepath` (string, required): The absolute or relative path to the directory to be created.
*   `parents` (boolean, optional, default=False): If True, create any missing parent directories as needed; no error if the directory already exists. If False, a `FileNotFoundError` is raised if the parent directory does not exist and the directory cannot be created.

**Return Value**:

*   `success` (boolean): True if the directory creation was successful, False otherwise.
*   `error` (string, optional): An error message if the directory creation failed.

**Example**:

```python
import os

def create_directory(filepath, parents=False):
    try:
        if parents:
            os.makedirs(filepath, exist_ok=True)
        else:
            os.mkdir(filepath)
        return {"success": True}
    except FileExistsError:
        return {"success": False, "error": f"Directory already exists: {filepath}"}
    except FileNotFoundError:
        return {"success": False, "error": f"Parent directory not found: {filepath}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Example usage:
create_result = create_directory("new_directory")
if create_result["success"]:
    print("Directory created successfully.")
else:
    print(f"Error creating directory: {create_result['error']}")

create_result = create_directory("path/to/new_directory", parents=True) # Create intermediate directories if they don't exist
if create_result["success"]:
    print("Directory created successfully.")
else:
    print(f"Error creating directory: {create_result['error']}")
```

**Best Practices**:

*   Handle potential exceptions like `FileExistsError` and `PermissionError`.
*   Check for sufficient permissions before attempting to create the directory.
*   Consider using `os.makedirs` with `exist_ok=True` to create intermediate directories if needed and prevent errors if the target directory already exists.
*   Implement retry logic for transient errors.

### 6. delete_directory

**Description**: Deletes a directory.

**Parameters**:

*   `filepath` (string, required): The absolute or relative path to the directory to be deleted.
*   `recursive` (boolean, optional, default=False): If True, recursively delete all files and subdirectories within the directory.  If False, the directory must be empty.

**Return Value**:

*   `success` (boolean): True if the directory deletion was successful, False otherwise.
*   `error` (string, optional): An error message if the directory deletion failed.

**Example**:

```python
import os
import shutil

def delete_directory(filepath, recursive=False):
    try:
        if recursive:
            shutil.rmtree(filepath)
        else:
            os.rmdir(filepath)
        return {"success": True}
    except FileNotFoundError:
        return {"success": False, "error": f"Directory not found: {filepath}"}
    except OSError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Example usage:
create_directory("test_dir")
write_file("test_dir/test_file.txt", "test content")
delete_result = delete_directory("test_dir", recursive=True)
if delete_result["success"]:
    print("Directory deleted successfully.")
else:
    print(f"Error deleting directory: {delete_result['error']}")

delete_result = delete_directory("nonexistent_directory", recursive=False)
if delete_result["success"]:
    print("Directory deleted successfully.")
else:
    print(f"Error deleting directory: {delete_result['error']}") # FileNotFoundError
```

**Best Practices**:

*   Handle potential exceptions like `FileNotFoundError`, `OSError`, and `PermissionError`.
*   **Be extremely cautious when using the `recursive` option, as it can lead to irreversible data loss.**  Implement a confirmation mechanism or a trash/recycle bin for deleted directories.
*   Log directory deletions for auditing purposes.
*   Ensure that the directory is not currently in use by any other processes before attempting to delete it.

### 7. list_files

**Description**: Lists files and directories within a given directory.

**Parameters**:

*   `filepath` (string, required): The absolute or relative path to the directory to list.
*   `include_hidden` (boolean, optional, default=False): If True, include hidden files and directories (starting with a dot). If False, exclude them.

**Return Value**:

*   `files` (list of strings): A list of filenames (including directories) within the specified directory.
*   `success` (boolean): True if the listing was successful, False otherwise.
*   `error` (string, optional): An error message if the listing failed.

**Example**:

```python
import os

def list_files(filepath, include_hidden=False):
    try:
        files = os.listdir(filepath)
        if not include_hidden:
            files = [f for f in files if not f.startswith('.')]
        return {"files": files, "success": True}
    except FileNotFoundError:
        return {"files": [], "success": False, "error": f"Directory not found: {filepath}"}
    except NotADirectoryError:
        return {"files": [], "success": False, "error": f"Not a directory: {filepath}"}
    except Exception as e:
        return {"files": [], "success": False, "error": str(e)}

# Example usage:
create_directory("test_dir")
write_file("test_dir/test_file.txt", "test content")
create_file("test_dir/.hidden_file.txt") # Create a hidden file

list_result = list_files("test_dir")
if list_result["success"]:
    print(f"Files in directory: {list_result['files']}") # ['test_file.txt']
else:
    print(f"Error listing files: {list_result['error']}")

list_result = list_files("test_dir", include_hidden=True)
if list_result["success"]:
    print(f"Files in directory: {list_result['files']}") # ['test_file.txt', '.hidden_file.txt']
else:
    print(f"Error listing files: {list_result['error']}")
```

**Best Practices**:

*   Handle potential exceptions like `FileNotFoundError` and `PermissionError`.
*   Provide options to filter the list based on file type, size, or modification date.
*   Consider returning absolute paths instead of just filenames.
*   Use pagination for large directories to avoid memory issues.

### 8. file_exists

**Description**: Checks if a file or directory exists.

**Parameters**:

*   `filepath` (string, required): The absolute or relative path to the file or directory to check.

**Return Value**:

*   `exists` (boolean): True if the file or directory exists, False otherwise.
*   `success` (boolean): Always True. Used for consistency with other file operations.
*   `error` (string, optional): Always None. Kept for consistency.

**Example**:

```python
import os

def file_exists(filepath):
    exists = os.path.exists(filepath)
    return {"exists": exists, "success": True}

# Example usage:
create_file("existing_file.txt")

exists_result = file_exists("existing_file.txt")
print(f"File exists: {exists_result['exists']}") # True

exists_result = file_exists("nonexistent_file.txt")
print(f"File exists: {exists_result['exists']}") # False
```

**Best Practices**:

*   Use `os.path.exists` for a simple existence check.
*   Consider using `os.path.isfile` or `os.path.isdir` if you need to differentiate between files and directories.
*   Handle potential exceptions if the path is malformed.

### 9. get_file_size

**Description**: Gets the size of a file in bytes.

**Parameters**:

*   `filepath` (string, required): The absolute or relative path to the file.

**Return Value**:

*   `size` (integer): The size of the file in bytes. Returns -1 if the file does not exist or an error occurs.
*   `success` (boolean): True if successful, False otherwise.
*   `error` (string, optional): An error message if the operation failed.

**Example**:

```python
import os

def get_file_size(filepath):
    try:
        size = os.path.getsize(filepath)
        return {"size": size, "success": True}
    except FileNotFoundError:
        return {"size": -1, "success": False, "error": f"File not found: {filepath}"}
    except OSError as e:
        return {"size": -1, "success": False, "error": str(e)}
    except Exception as e:
        return {"size": -1, "success": False, "error": str(e)}

# Example Usage:
write_file("test_file.txt", "This is some test content.")
file_size_result = get_file_size("test_file.txt")

if file_size_result["success"]:
    print(f"File size: {file_size_result['size']} bytes") # File size: 27 bytes
else:
    print(f"Error getting file size: {file_size_result['error']}")

file_size_result = get_file_size("nonexistent_file.txt")

if file_size_result["success"]:
    print(f"File size: {file_size_result['size']} bytes")
else:
    print(f"Error getting file size: {file_size_result['error']}") # FileNotFoundError
```

**Best Practices**:

*   Handle `FileNotFoundError` and other `OSError` exceptions.
*   Consider using `os.stat(filepath).st_size` for more detailed file information.
*   For large files, consider using a generator to read the file in chunks and calculate the size iteratively.

## General Best Practices

*   **Security:** Be extremely careful when handling file paths provided by external sources (e.g., user input).  Sanitize file paths to prevent directory traversal attacks and other security vulnerabilities. Avoid allowing absolute paths to be specified, and limit operations to a designated "sandbox" directory.
*   **Error Handling:**  Always check the `success` flag and handle potential errors gracefully. Provide informative error messages to the user or log them for debugging purposes.
*   **Resource Management:** Close files and release resources promptly after use to prevent resource leaks.
*   **Concurrency:** Use appropriate locking mechanisms if multiple processes or threads might be accessing the same files concurrently.
*   **Abstraction:**  Design the API to be as abstract and platform-independent as possible.
*   **Logging:** Implement logging to track file system operations for auditing and debugging.  Include details like the file path, operation type, user, and timestamp.
*   **Testing:**  Thoroughly test all file system operations, including edge cases and error conditions.  Use unit tests, integration tests, and end-to-end tests to ensure the reliability of the skill.

## Potential Improvements

*   Implement file locking mechanisms.
*   Add support for file permissions management (e.g., `chmod`).
*   Implement a file watching mechanism to detect changes to files and directories.
*   Add support for symbolic links.
*   Provide a method for getting file metadata (e.g., creation date, modification date, owner).
*   Implement file compression and decompression functionality.
```
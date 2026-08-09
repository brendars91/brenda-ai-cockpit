```markdown
---
name: sequential-thinking
description: Skill for breaking down complex tasks into ordered sequences of smaller, executable actions and reasoning through their dependencies.
version: 1.0.0
auto_generated: true
---

# sequential-thinking

## Purpose
This skill is designed to enable the AI agent to approach complex tasks in a structured and methodical manner. It provides the capability to:

*   Decompose high-level goals into smaller, manageable steps.
*   Order these steps based on dependencies and logical flow.
*   Reason through the potential outcomes and consequences of each step.
*   Adapt the sequence based on observed results or unexpected errors.
*   Maintain state and context across multiple steps.

## Usage
This skill is not directly executable. Instead, it serves as a foundation for other skills and the overall reasoning engine of the AI agent. It is used to plan and orchestrate the execution of other skills in a specific order. Think of it as a meta-skill; it provides the *how* and *why* for using other skills.

## Components

The `sequential-thinking` skill relies on the following internal components:

1.  **Task Decomposition Module:** This module is responsible for breaking down a complex goal into a set of smaller, actionable sub-tasks. This decomposition should be granular enough that each sub-task can be handled by a specific skill.

2.  **Dependency Analysis Module:**  This module identifies the dependencies between the sub-tasks. It determines which tasks must be completed before others can begin, and identifies tasks that can be performed in parallel.

3.  **Sequencing and Ordering Module:** This module takes the sub-tasks and their dependencies and creates an ordered sequence of steps to be executed. This sequence should optimize for efficiency and minimize the risk of errors.

4.  **Reasoning and Planning Module:** This module reasons about the potential outcomes of each step and adjusts the sequence as needed.  It anticipates potential errors and incorporates error-handling logic into the plan. This includes pre-flight checks (e.g., ensuring a file exists before attempting to read it).

5.  **State Management Module:** This module tracks the progress of the overall task and maintains state across multiple steps. This includes storing the results of previous steps, tracking the current step being executed, and handling any errors that occur. This will often involve temporary file storage via the `filesystem` skill.

## Actionable Steps and Examples

Here are some examples of how the `sequential-thinking` skill can be applied in different scenarios:

### Example 1: File Analysis and Reporting

**Goal:** Analyze a log file, extract relevant information, and generate a report.

**Decomposition:**

1.  Read the log file using the `filesystem` skill.
2.  Search for specific patterns using the `grep_search` skill.
3.  Parse the search results to extract relevant data.
4.  Format the extracted data into a report.
5.  Write the report to a file using the `filesystem` skill.

**Sequence:**

```
[
    {
        "step": 1,
        "action": "read_file",
        "skill": "filesystem",
        "parameters": {
            "filepath": "/path/to/log/file.log"
        },
        "output_variable": "log_content"
    },
    {
        "step": 2,
        "action": "search_patterns",
        "skill": "grep_search",
        "parameters": {
            "content": "${log_content}",
            "patterns": ["ERROR", "WARNING"],
            "context_lines": 5
        },
        "output_variable": "search_results"
    },
    {
        "step": 3,
        "action": "parse_search_results",
        "skill": "internal_parsing_module",  // Assuming an internal parsing skill exists
        "parameters": {
            "results": "${search_results}"
        },
        "output_variable": "parsed_data"
    },
    {
        "step": 4,
        "action": "format_report",
        "skill": "internal_formatting_module", // Assuming an internal formatting skill exists
        "parameters": {
            "data": "${parsed_data}"
        },
        "output_variable": "report_content"
    },
    {
        "step": 5,
        "action": "write_file",
        "skill": "filesystem",
        "parameters": {
            "filepath": "/path/to/report/report.txt",
            "content": "${report_content}"
        }
    }
]
```

**Reasoning and Planning:**

*   Before reading the log file, check if the file exists and is readable using the `filesystem` skill.
*   If the `grep_search` skill returns no results, handle the case gracefully (e.g., generate a report indicating no errors were found).
*   Implement error handling for each step to catch exceptions and prevent the process from crashing.

### Example 2: Vulnerability Scanning

**Goal:** Scan a target system for vulnerabilities using Nmap.

**Decomposition:**

1.  Run Nmap scan on the target system.
2.  Parse the Nmap output.
3.  Identify potential vulnerabilities based on the Nmap results.
4.  Generate a report of the identified vulnerabilities.

**Sequence:**

```
[
    {
        "step": 1,
        "action": "run_nmap_scan",
        "skill": "nmap_skill", // Assuming an Nmap integration skill exists
        "parameters": {
            "target": "target.example.com",
            "options": "-sV -p 1-1000"
        },
        "output_variable": "nmap_output"
    },
    {
        "step": 2,
        "action": "parse_nmap_output",
        "skill": "nmap_parser_skill", // Assuming an Nmap parsing skill exists
        "parameters": {
            "nmap_output": "${nmap_output}"
        },
        "output_variable": "parsed_nmap_data"
    },
    {
        "step": 3,
        "action": "identify_vulnerabilities",
        "skill": "vulnerability_identifier_skill", // Assuming a vulnerability identification skill exists
        "parameters": {
            "nmap_data": "${parsed_nmap_data}"
        },
        "output_variable": "vulnerability_list"
    },
    {
        "step": 4,
        "action": "generate_report",
        "skill": "report_generator_skill", // Assuming a report generation skill exists
        "parameters": {
            "vulnerabilities": "${vulnerability_list}"
        },
        "output_variable": "vulnerability_report"
    },
    {
        "step": 5,
        "action": "write_file",
        "skill": "filesystem",
        "parameters": {
            "filepath": "/path/to/vulnerability/report.txt",
            "content": "${vulnerability_report}"
        }
    }
]
```

**Reasoning and Planning:**

*   Before running the Nmap scan, verify network connectivity to the target system.
*   Implement error handling to gracefully handle cases where the Nmap scan fails or returns invalid output.
*   Use a vulnerability database to correlate Nmap results with known vulnerabilities.
*   Prioritize vulnerabilities based on severity and impact.

### Example 3:  Finding all files recursively matching a pattern and writing to a new file

**Goal**: Recursively search all files for a given pattern starting in a specified directory, and then write all the matched lines to a file.

**Decomposition**:

1. Recursively list all files in the specified directory via `filesystem`.
2. Iterate through each file, using `grep_search` to find the given pattern.
3. Collect any matching lines found by `grep_search` across all files.
4. Write the aggregate matching lines to a new file using `filesystem`.

**Sequence**:

```
[
    {
        "step": 1,
        "action": "list_files_recursively",
        "skill": "filesystem",
        "parameters": {
            "directory": "/path/to/search/directory",
            "recursive": true
        },
        "output_variable": "file_list"
    },
    {
       "step": 2,
       "action": "initialize_matches",
       "skill": "internal_variable_initialization", //Placeholder. Skill to set a variable.
       "parameters": {
           "variable_name": "aggregate_matches",
           "initial_value": ""
       }
    },
    {
        "step": 3,
        "action": "iterate_files",
        "skill": "internal_iteration_module", // Placeholder for an iteration skill
        "parameters": {
            "items": "${file_list}",
            "iterator_variable": "current_file",
            "sub_steps": [
                {
                    "step": 3.1,
                    "action": "search_in_file",
                    "skill": "grep_search",
                    "parameters": {
                        "filepath": "${current_file}",
                        "pattern": "target_pattern"
                    },
                    "output_variable": "file_matches"
                },
                {
                    "step": 3.2,
                    "action": "append_matches",
                    "skill": "internal_string_append", // Placeholder Skill to concat to an existing string variable.
                    "parameters": {
                        "base_string_variable": "aggregate_matches",
                        "append_string": "${file_matches}"
                    }
                }
            ]
        }
    },
    {
        "step": 4,
        "action": "write_aggregate_matches",
        "skill": "filesystem",
        "parameters": {
            "filepath": "/path/to/output/matches.txt",
            "content": "${aggregate_matches}"
        }
    }
]
```

**Reasoning and Planning**:

* Check for filesystem permission errors.
* Handle cases where a file is not found (e.g. a broken symbolic link).
* Handle possible large quantities of matching lines with streamed writing.

## Error Handling

The `sequential-thinking` skill should incorporate robust error handling mechanisms to ensure that the AI agent can gracefully handle unexpected situations. This includes:

*   **Error Detection:** Implement checks at each step to detect potential errors (e.g., file not found, invalid input, skill execution failure).
*   **Error Reporting:** Provide informative error messages that clearly describe the nature of the error and its location.
*   **Error Recovery:** Implement strategies for recovering from errors, such as:
    *   Retrying the failed step.
    *   Skipping the failed step and proceeding to the next step.
    *   Rolling back to a previous state.
    *   Terminating the process gracefully and reporting the error to the user.
*   **Logging:** Log all errors and warnings to a file for debugging and analysis.

## Best Practices

*   **Keep tasks small and focused:** Break down complex goals into small, manageable tasks that can be handled by individual skills.
*   **Define clear inputs and outputs:** Each step in the sequence should have clearly defined inputs and outputs.
*   **Use descriptive variable names:** Use meaningful variable names to improve code readability and maintainability.
*   **Implement error handling:** Always implement error handling to gracefully handle unexpected situations.
*   **Test thoroughly:** Test the sequence thoroughly to ensure that it works as expected in a variety of scenarios.
*   **Monitor performance:** Monitor the performance of the sequence to identify potential bottlenecks and optimize for efficiency.
*   **Document the sequence:** Document the purpose of each step in the sequence and any assumptions that are made.

## Dependencies

This skill has no direct dependencies on other skills, but it heavily relies on other skills to perform the actual actions.  Specifically, it expects the presence of skills like:

*   `filesystem`
*   `grep_search`
*   Custom skills for domain-specific tasks (e.g., `nmap_skill`, `report_generator_skill`)
*   Internal skills for variable management, iteration, and string manipulation.

The presence and correct functioning of these skills are crucial for the `sequential-thinking` skill to operate effectively. The `sequential-thinking` skill will attempt to call and orchestrate these other skills, so they must adhere to a well-defined API contract.
```
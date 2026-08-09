```markdown
---
name: abap-validator
description: Skill for validating ABAP code snippets against SAP's best practices, syntax rules, and security vulnerabilities. This skill uses the SAP Code Inspector or similar tools (either directly via RFC or through a proxy API) to perform static code analysis. Designed for integration within CI/CD pipelines, development environments, and automated code review processes in SAP environments.
version: 1.0.0
auto_generated: false
---

# abap-validator

## Purpose

This skill empowers the AI agent to validate ABAP code, ensuring code quality, adherence to SAP standards, and security compliance. It provides actions to submit code snippets, trigger validation processes, and retrieve detailed analysis reports. This allows for automated code review, early detection of potential issues, and overall improvement of ABAP code quality.

## Actions

### 1. `validate_abap_code`

**Description:** Submits ABAP code for validation and initiates the code inspection process.

**Parameters:**

*   `code`: (string, required) The ABAP code snippet to be validated.  Supports multi-line strings.
*   `check_variant`: (string, optional, default: "DEFAULT") The name of the Code Inspector check variant to be used.  Defines the scope and ruleset for the validation. Predefined check variants include "DEFAULT", "SECURITY", "PERFORMANCE", and custom variants configured in the SAP system.
*   `object_type`: (string, optional, default: "PROG") The type of ABAP object being validated.  Common values include "PROG" (Program), "CLAS" (Class), "FUGR" (Function Group), "INTF" (Interface), "TRAN" (Transaction).
*   `object_name`: (string, optional) The name of the ABAP object being validated.  This is useful for context and can be used to retrieve object-specific metadata.  If not provided, a generic name is used.
*   `rfc_destination`: (string, optional, default: "SAP_RFC") The RFC destination configured in the SAP system to connect to.  Must be pre-configured for secure communication. This parameter should default to a configured connection to the SAP system.
*   `suppress_findings`: (boolean, optional, default: false) If true, the validation process will attempt to suppress findings based on predefined rules or exemptions.  Use with caution.
*   `max_findings`: (integer, optional, default: 100)  Maximum number of findings to return. This prevents extremely large result sets, particularly for complex or problematic code.  A warning should be generated if the number of findings exceeds this limit.
*   `short_dump_on_error`: (boolean, optional, default: true) Whether to create an ABAP short dump in case of an error during validation. Useful for debugging.

**Returns:**

*   `validation_id`: (string) A unique identifier for the validation process. This ID is used to retrieve the validation report later.
*   `status`: (string) The status of the validation process (e.g., "QUEUED", "RUNNING", "COMPLETED", "ERROR").
*   `message`: (string, optional) A message providing additional information about the validation status.

**Example:**

```json
{
  "action": "validate_abap_code",
  "params": {
    "code": "REPORT z_test.\nWRITE: 'Hello, World!'.",
    "check_variant": "SECURITY",
    "object_type": "PROG",
    "object_name": "Z_TEST"
  }
}
```

**Error Handling:**

*   Returns an error if the provided `code` is empty or exceeds the maximum allowed length (e.g., 100,000 characters).
*   Returns an error if the specified `check_variant` does not exist in the SAP system.
*   Returns an error if the RFC connection to the SAP system fails.
*   Returns an error if the ABAP code contains syntax errors that prevent validation.

**Best Practices:**

*   Use specific `check_variant` values appropriate for the type of code being validated.  "SECURITY" for security-sensitive code, "PERFORMANCE" for performance-critical code.
*   Provide the `object_name` and `object_type` for better contextual analysis.
*   Monitor the `status` of the validation process and retry if necessary.
*   Implement error handling to gracefully handle validation failures.
*   Configure `rfc_destination` securely using established SAP security practices.
*   Consider using `suppress_findings` only after careful review of each suppressed finding and establishment of appropriate justification.

### 2. `get_validation_report`

**Description:** Retrieves the validation report for a specific validation ID.

**Parameters:**

*   `validation_id`: (string, required) The unique identifier for the validation process, returned by the `validate_abap_code` action.
*   `rfc_destination`: (string, optional, default: "SAP_RFC") The RFC destination configured in the SAP system to connect to.

**Returns:**

*   `status`: (string) The status of the validation process (e.g., "COMPLETED", "ERROR", "NOT_FOUND").
*   `findings`: (array of objects, optional) An array of findings, where each finding contains the following information:
    *   `message`: (string) A description of the finding.
    *   `category`: (string) The category of the finding (e.g., "Syntax Error", "Security Vulnerability", "Performance Issue", "Code Style").
    *   `priority`: (string) The priority of the finding (e.g., "High", "Medium", "Low").
    *   `line_number`: (integer, optional) The line number in the ABAP code where the finding occurs.
    *   `code_snippet`: (string, optional) The relevant code snippet where the finding occurs.
    *   `rule_id`: (string, optional) The ID of the Code Inspector rule that triggered the finding.
    *   `object_name`: (string, optional) The name of the object associated with the finding.
    *   `object_type`: (string, optional) The type of object associated with the finding.
*   `error_message`: (string, optional) An error message if the validation process failed.

**Example:**

```json
{
  "action": "get_validation_report",
  "params": {
    "validation_id": "1234567890"
  }
}
```

**Example Response (Success):**

```json
{
  "status": "COMPLETED",
  "findings": [
    {
      "message": "Avoid using SELECT * in productive code.",
      "category": "Performance Issue",
      "priority": "Medium",
      "line_number": 10,
      "code_snippet": "SELECT * FROM mara INTO TABLE @data(lt_mara).",
      "rule_id": "CI_PERFORMANCE_SELECT_STAR",
      "object_name": "Z_TEST",
      "object_type": "PROG"
    },
    {
      "message": "Potential SQL Injection vulnerability detected.",
      "category": "Security Vulnerability",
      "priority": "High",
      "line_number": 25,
      "code_snippet": "lv_where = |WHERE name = '{ iv_name }'|.",
      "rule_id": "CI_SECURITY_SQL_INJECTION",
      "object_name": "Z_TEST",
      "object_type": "PROG"
    }
  ]
}
```

**Example Response (Error):**

```json
{
  "status": "ERROR",
  "error_message": "Validation process failed with error: Invalid ABAP syntax."
}
```

**Example Response (Not Found):**

```json
{
  "status": "NOT_FOUND",
  "error_message": "Validation process with ID 1234567890 not found."
}
```

**Error Handling:**

*   Returns an error if the specified `validation_id` is not found.
*   Returns an error if the RFC connection to the SAP system fails.
*   Returns an error if the validation process failed.
*   Returns an empty `findings` array if no issues were found during validation.

**Best Practices:**

*   Check the `status` of the validation report before processing the `findings`.
*   Prioritize findings based on their `priority` and `category`.
*   Provide detailed information about the findings to developers to facilitate remediation.
*   Implement a mechanism to track resolved findings and prevent regressions.
*   Use a consistent approach for mapping `rule_id` values to more descriptive messages.
*   Implement a retry mechanism for transient errors.
*   Handle the `NOT_FOUND` status gracefully.

### 3. `list_check_variants`

**Description:** Retrieves a list of available Code Inspector check variants from the SAP system.

**Parameters:**

*   `rfc_destination`: (string, optional, default: "SAP_RFC") The RFC destination configured in the SAP system to connect to.

**Returns:**

*   `status`: (string) The status of the operation (e.g., "COMPLETED", "ERROR").
*   `check_variants`: (array of strings, optional) An array of Code Inspector check variant names.
*   `error_message`: (string, optional) An error message if the operation failed.

**Example:**

```json
{
  "action": "list_check_variants"
}
```

**Example Response (Success):**

```json
{
  "status": "COMPLETED",
  "check_variants": [
    "DEFAULT",
    "SECURITY",
    "PERFORMANCE",
    "CODE_QUALITY",
    "Z_CUSTOM_VARIANT"
  ]
}
```

**Example Response (Error):**

```json
{
  "status": "ERROR",
  "error_message": "Failed to retrieve check variants from SAP system."
}
```

**Error Handling:**

*   Returns an error if the RFC connection to the SAP system fails.
*   Returns an error if the check variants cannot be retrieved from the SAP system.
*   Returns an empty `check_variants` array if no check variants are available.

**Best Practices:**

*   Cache the list of check variants to reduce the number of calls to the SAP system.
*   Display the list of check variants to the user to allow them to select the appropriate variant for validation.
*   Handle the case where the list of check variants is empty.
*   Implement a retry mechanism for transient errors.

## Configuration

The `abap-validator` skill requires the following configuration:

*   **SAP RFC Destination:** A properly configured RFC destination in the SAP system is required to allow the AI agent to connect and communicate with the SAP system. The RFC destination must be configured with appropriate authorization to execute Code Inspector functions. The default RFC destination is "SAP_RFC", but this can be overridden in the action parameters.
*   **SAP User Authorization:** The SAP user associated with the RFC destination must have the necessary authorizations to execute Code Inspector checks (transaction SCI) and retrieve results.  This may require specific roles and authorization objects assigned to the user.
*   **Code Inspector Check Variants:**  Ensure the necessary Code Inspector check variants are configured in the SAP system.  This includes the standard variants (DEFAULT, SECURITY, PERFORMANCE) and any custom variants specific to the project.

## Security Considerations

*   **Secure RFC Communication:** Use secure RFC communication protocols (e.g., SNC) to encrypt data transmitted between the AI agent and the SAP system.
*   **Principle of Least Privilege:** Grant the SAP user associated with the RFC destination only the minimum necessary authorizations to perform Code Inspector checks.
*   **Input Validation:**  Validate all input parameters to prevent injection attacks.
*   **Output Sanitization:** Sanitize all output data to prevent cross-site scripting (XSS) attacks.
*   **Logging and Auditing:**  Implement comprehensive logging and auditing to track all validation activities.
*   **Data Masking:** Consider masking sensitive data in the code snippets and validation reports.

## Example Usage Scenario

1.  The AI agent receives a pull request containing ABAP code changes.
2.  The AI agent uses the `validate_abap_code` action to submit the ABAP code for validation, specifying the appropriate `check_variant`.
3.  The AI agent monitors the `status` of the validation process.
4.  Once the validation process is complete, the AI agent uses the `get_validation_report` action to retrieve the validation report.
5.  The AI agent analyzes the `findings` in the validation report and identifies any critical issues.
6.  The AI agent generates a comment on the pull request with a summary of the findings, including the `message`, `category`, `priority`, and `line_number` for each issue.
7.  The AI agent provides recommendations for resolving the identified issues.

## Integration with Other Skills

The `abap-validator` skill can be integrated with other skills to create more complex workflows. For example:

*   **`sap-connector`:** Used to retrieve ABAP code from the SAP system for validation.
*   **`ifrs-reporter`:**  Used to generate reports based on the validation findings, for example, a report on security vulnerabilities in the ABAP codebase.
*   **Issue Tracking:**  An issue tracking skill could be used to automatically create tickets for high-priority findings.
*   **Notification Skill:** A notification skill could be used to notify developers of new validation results.
```
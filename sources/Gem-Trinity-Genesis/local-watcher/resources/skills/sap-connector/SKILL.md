```markdown
---
name: sap-connector
description: Skill for interacting with SAP systems. Includes actions for retrieving data, executing transactions, and managing SAP objects. Designed for integration with SAP ECC and S/4HANA systems via SAP NetWeaver RFC (Remote Function Call) protocol and SAP BAPI (Business Application Programming Interface).
version: 1.0.0
auto_generated: false
---

# sap-connector

## Purpose

This skill provides a comprehensive set of actions for connecting to and interacting with SAP systems. It enables the AI agent to retrieve data, execute transactions, and manage SAP objects, facilitating automation of SAP-related business processes. It leverages the SAP NetWeaver RFC protocol and SAP BAPI for seamless integration with SAP ECC and S/4HANA systems.

## Target Audience

*   AI agents requiring access to SAP data and functionality.
*   Automation workflows involving SAP systems.
*   Processes that need to extract data from SAP or execute transactions within SAP.

## Core Functionalities

*   **Connection Management:** Establishes and maintains connections to SAP systems.
*   **Data Retrieval:** Retrieves data from SAP tables, views, and BAPIs.
*   **Transaction Execution:** Executes SAP transactions (including BAPIs and RFCs).
*   **Object Management:** Manages SAP objects (e.g., creating, updating, deleting).
*   **Error Handling:** Handles errors and exceptions returned by SAP.
*   **Authentication and Authorization:** Supports different authentication mechanisms for secure access.

## Architecture

The `sap-connector` skill utilizes the SAP NetWeaver RFC protocol and SAP BAPI interface to communicate with SAP systems. It typically relies on a dedicated library or SDK for handling the RFC protocol (e.g., `pyrfc` for Python).  The connection parameters (SAP system ID, client, username, password, language) are securely stored and managed.

## Actions

### 1. `connect`

**Description:** Establishes a connection to an SAP system.

**Parameters:**

*   `system_id` (string, required): The SAP system ID (e.g., "ABC").
*   `client` (string, required): The SAP client (e.g., "001").
*   `username` (string, required): The SAP username.
*   `password` (string, required): The SAP password.  **Important:**  Store and manage passwords securely using a vault or secrets management system.  Avoid hardcoding passwords in the agent's configuration.
*   `language` (string, optional, default: "EN"): The SAP language code (e.g., "DE" for German).
*   `ashost` (string, optional): Application server host. Either `ashost` or `msghost` and `r3name` must be specified.
*   `sysnr` (string, optional): System number of the application server. If `ashost` is specified, `sysnr` must also be specified.
*   `msghost` (string, optional): Message server host. Either `ashost` or `msghost` and `r3name` must be specified.
*   `r3name` (string, optional): SAP system ID of the application server. If `msghost` is specified, `r3name` must also be specified.
*   `group` (string, optional): Logon group to use for load balancing.
*   `pool_size` (integer, optional, default: 5): Number of connections to keep open in the pool.
*   `peak_connections` (integer, optional, default: 10): Maximum number of connections allowed in the pool.
*   `expiration_time` (integer, optional, default: 3600): Connection expiration time in seconds.

**Returns:**

*   `connection_id` (string): A unique identifier for the established connection. This ID is used in subsequent actions to reference the connection.
*   `status` (string): "success" or "failure".
*   `error_message` (string, optional): Error message if the connection failed.

**Example:**

```json
{
  "action": "connect",
  "parameters": {
    "system_id": "ABC",
    "client": "001",
    "username": "MY_USER",
    "password": "${secrets.SAP_PASSWORD}",  // Using a secrets management system
    "language": "EN"
  }
}
```

**Error Handling:**

*   Invalid credentials: Returns an error message indicating incorrect username or password.
*   Connection refused: Returns an error message indicating that the SAP system is unavailable or the network connection is down.
*   Invalid system ID or client: Returns an error message indicating invalid configuration.
*   Connection pool exhausted: Returns an error message if the maximum number of connections in the pool has been reached.

**Best Practices:**

*   **Secure Password Management:** Never hardcode passwords in the agent's configuration. Use a secrets management system to store and retrieve passwords securely.
*   **Connection Pooling:** Use connection pooling to improve performance and reduce the overhead of establishing new connections.
*   **Error Handling:** Implement robust error handling to gracefully handle connection failures and other errors.
*   **Logging:** Log connection attempts and errors for auditing and troubleshooting purposes.

### 2. `disconnect`

**Description:** Closes an existing connection to an SAP system.

**Parameters:**

*   `connection_id` (string, required): The ID of the connection to close, obtained from the `connect` action.

**Returns:**

*   `status` (string): "success" or "failure".
*   `error_message` (string, optional): Error message if the disconnection failed.

**Example:**

```json
{
  "action": "disconnect",
  "parameters": {
    "connection_id": "abc-123"
  }
}
```

**Error Handling:**

*   Invalid `connection_id`: Returns an error message indicating that the connection ID is invalid.
*   Connection already closed: Returns an error message indicating that the connection has already been closed.

### 3. `read_table`

**Description:** Reads data from an SAP table or view.

**Parameters:**

*   `connection_id` (string, required): The ID of the connection to use.
*   `table_name` (string, required): The name of the SAP table or view to read from.
*   `fields` (list of strings, required): A list of field names to retrieve.  Specify "*" to retrieve all fields.
*   `where_clause` (string, optional): An SQL WHERE clause to filter the data.  **Important:** Ensure proper escaping to prevent SQL injection vulnerabilities.  Consider using parameterized queries if the underlying library supports it.
*   `row_count` (integer, optional, default: 0):  Maximum number of rows to retrieve.  A value of 0 retrieves all rows that match the `where_clause`.
*   `skip_rows` (integer, optional, default: 0): Number of rows to skip from the beginning of the result set.

**Returns:**

*   `data` (list of dictionaries): A list of dictionaries, where each dictionary represents a row of data.  The keys of the dictionary are the field names specified in the `fields` parameter.
*   `status` (string): "success" or "failure".
*   `error_message` (string, optional): Error message if the read failed.

**Example:**

```json
{
  "action": "read_table",
  "parameters": {
    "connection_id": "abc-123",
    "table_name": "MARA",
    "fields": ["MATNR", "ERSDA", "MEINS"],
    "where_clause": "MTART = 'FERT'",
    "row_count": 10
  }
}
```

**Error Handling:**

*   Invalid `connection_id`: Returns an error message indicating that the connection ID is invalid.
*   Table or view not found: Returns an error message indicating that the specified table or view does not exist.
*   Invalid field name: Returns an error message indicating that one or more of the specified field names are invalid.
*   SQL syntax error: Returns an error message indicating an error in the `where_clause`.
*   Authorization error: Returns an error message indicating that the user does not have permission to read the table or view.

**Best Practices:**

*   **Specify Fields:**  Always specify the fields you need instead of using "*", as this reduces the amount of data transferred and improves performance.
*   **Use WHERE Clause:** Use a `where_clause` to filter the data as much as possible to reduce the amount of data retrieved.
*   **Limit Row Count:** Use `row_count` to limit the number of rows retrieved, especially for large tables.
*   **Parameterized Queries:**  If supported by the underlying SAP connector library, use parameterized queries to prevent SQL injection vulnerabilities.
*   **Data Type Considerations:** Be aware of the data types of the fields in the SAP table and handle them appropriately in your code.
*   **Character Encoding:** Ensure correct character encoding when interacting with SAP, especially when dealing with non-ASCII characters.

### 4. `call_bapi`

**Description:** Calls an SAP Business Application Programming Interface (BAPI).

**Parameters:**

*   `connection_id` (string, required): The ID of the connection to use.
*   `bapi_name` (string, required): The name of the BAPI to call (e.g., "BAPI_MATERIAL_GETDETAIL").
*   `parameters` (dictionary, optional): A dictionary of input parameters for the BAPI. The keys of the dictionary are the parameter names, and the values are the parameter values.
*   `import_parameters` (dictionary, optional): A dictionary of importing parameters for the BAPI (alternative way to pass parameters). Useful for complex BAPIs.
*   `table_parameters` (dictionary, optional):  A dictionary of table parameters for the BAPI. The keys are the table parameter names, and the values are lists of dictionaries, where each dictionary represents a row in the table.

**Returns:**

*   `data` (dictionary): A dictionary of output parameters returned by the BAPI. The keys of the dictionary are the parameter names, and the values are the parameter values. This will also contain table data.
*   `status` (string): "success" or "failure".
*   `error_message` (string, optional): Error message if the BAPI call failed.
*   `return_messages` (list of dictionaries, optional): List of messages returned from the BAPI's `RETURN` parameter. Each dictionary contains fields like `TYPE`, `ID`, `NUMBER`, `MESSAGE`. Useful for debugging.

**Example:**

```json
{
  "action": "call_bapi",
  "parameters": {
    "connection_id": "abc-123",
    "bapi_name": "BAPI_MATERIAL_GETDETAIL",
    "parameters": {
      "MATERIAL": "000000000000000001",
      "PLANT": "1000"
    }
  }
}
```

```json
{
  "action": "call_bapi",
  "parameters": {
    "connection_id": "abc-123",
    "bapi_name": "BAPI_SALESORDER_CREATEFROMDAT2",
    "import_parameters": {
      "SALESDOCUMENTIN": " ",
      "ORDER_HEADER_IN": {
        "DOC_TYPE": "OR",
        "SALES_ORG": "1000",
        "DISTR_CHAN": "10",
        "DIVISION": "00",
        "PMNTTRMS": "0001"
      }
    },
    "table_parameters": {
      "ORDER_ITEMS_IN": [
        {
          "ITM_NUMBER": "000010",
          "MATERIAL": "000000000000000001",
          "TARGET_QTY": "1",
          "TARGET_QU": "PC"
        }
      ]
    }
  }
}
```

**Error Handling:**

*   Invalid `connection_id`: Returns an error message indicating that the connection ID is invalid.
*   BAPI not found: Returns an error message indicating that the specified BAPI does not exist.
*   Invalid parameter name: Returns an error message indicating that one or more of the specified parameter names are invalid.
*   Data type mismatch: Returns an error message indicating that the data type of a parameter value does not match the expected data type.
*   Authorization error: Returns an error message indicating that the user does not have permission to call the BAPI.
*   BAPI-specific errors: BAPIs often return error messages in their `RETURN` parameter. Always check the `return_messages` list for errors and warnings.

**Best Practices:**

*   **Understand BAPI Parameters:** Carefully review the documentation for the BAPI you are calling to understand the required input and output parameters.
*   **Data Type Conversion:** Ensure that the data types of the parameter values match the expected data types in the BAPI.  You might need to perform data type conversions (e.g., string to integer, date to SAP date format).
*   **Error Handling:** Always check the `return_messages` list for errors and warnings returned by the BAPI.  Implement appropriate error handling based on the returned messages.
*   **Transaction Management:** For BAPIs that create or modify data, consider using transaction management to ensure data consistency.  Use BAPI_TRANSACTION_COMMIT or BAPI_TRANSACTION_ROLLBACK as needed.
*   **Buffering:** For frequently used BAPIs, consider implementing buffering to reduce the number of calls to the SAP system.
*   **Parameter Passing Styles:** Decide whether to use the combined `parameters` dictionary, or the more structured `import_parameters` and `table_parameters` dictionaries. The latter are typically preferred for complex BAPIs.

### 5. `execute_rfc`

**Description:** Executes a Remote Function Call (RFC) in SAP. This is a more general-purpose way to call SAP functions than using BAPIs.

**Parameters:**

*   `connection_id` (string, required): The ID of the connection to use.
*   `rfc_name` (string, required): The name of the RFC function module to call (e.g., "RFC_READ_TABLE").
*   `parameters` (dictionary, optional): A dictionary of input parameters for the RFC function module. The keys of the dictionary are the parameter names, and the values are the parameter values.

**Returns:**

*   `data` (dictionary): A dictionary of output parameters returned by the RFC function module. The keys of the dictionary are the parameter names, and the values are the parameter values.
*   `status` (string): "success" or "failure".
*   `error_message` (string, optional): Error message if the RFC call failed.

**Example:**

```json
{
  "action": "execute_rfc",
  "parameters": {
    "connection_id": "abc-123",
    "rfc_name": "RFC_READ_TABLE",
    "parameters": {
      "QUERY_TABLE": "MARA",
      "FIELDS": [
        {"FIELDNAME": "MATNR"},
        {"FIELDNAME": "ERSDA"},
        {"FIELDNAME": "MEINS"}
      ],
      "OPTIONS": [{"TEXT": "MTART = 'FERT'"}],
      "ROWCOUNT": 10
    }
  }
}
```

**Error Handling:**

*   Invalid `connection_id`: Returns an error message indicating that the connection ID is invalid.
*   RFC function module not found: Returns an error message indicating that the specified RFC function module does not exist.
*   Invalid parameter name: Returns an error message indicating that one or more of the specified parameter names are invalid.
*   Data type mismatch: Returns an error message indicating that the data type of a parameter value does not match the expected data type.
*   Authorization error: Returns an error message indicating that the user does not have permission to execute the RFC function module.

**Best Practices:**

*   **Understand RFC Parameters:** Carefully review the documentation for the RFC function module you are calling to understand the required input and output parameters. RFCs can be more complex than BAPIs and require a deep understanding of the SAP data model.
*   **Data Type Conversion:** Ensure that the data types of the parameter values match the expected data types in the RFC function module.
*   **Error Handling:** Implement robust error handling to gracefully handle RFC call failures.  Pay attention to the exceptions returned by the SAP system.
*   **Security Considerations:**  Be aware of the security implications of executing RFC function modules, especially those that modify data.  Ensure that the user has the necessary authorizations to execute the RFC function module.

## Example Usage

**Scenario:** Retrieve material master data from SAP based on a material number.

1.  **Connect to the SAP system:**

    ```json
    {
      "action": "connect",
      "parameters": {
        "system_id": "ABC",
        "client": "001",
        "username": "MY_USER",
        "password": "${secrets.SAP_PASSWORD}",
        "language": "EN"
      }
    }
    ```

2.  **Call the `BAPI_MATERIAL_GETDETAIL` BAPI:**

    ```json
    {
      "action": "call_bapi",
      "parameters": {
        "connection_id": "abc-123",
        "bapi_name": "BAPI_MATERIAL_GETDETAIL",
        "parameters": {
          "MATERIAL": "000000000000000001",
          "PLANT": "1000"
        }
      }
    }
    ```

3.  **Process the returned data:**  The `data` dictionary in the response will contain the material master data.

4.  **Disconnect from the SAP system:**

    ```json
    {
      "action": "disconnect",
      "parameters": {
        "connection_id": "abc-123"
      }
    }
    ```

## Security Considerations

*   **Password Management:**  Store and manage SAP passwords securely.  Use a vault or secrets management system to avoid hardcoding passwords in the agent's configuration.
*   **Authorization:**  Ensure that the SAP user account used by the agent has the necessary authorizations to access the required data and functionality.  Follow the principle of least privilege and grant only the necessary authorizations.
*   **Data Validation:**  Validate all input data to prevent SQL injection and other security vulnerabilities.
*   **Network Security:**  Secure the network connection between the agent and the SAP system.  Use encryption and firewalls to protect the data in transit.
*   **Auditing:**  Log all SAP interactions for auditing and security monitoring purposes.

## Dependencies

*   Requires a library or SDK for interacting with SAP systems via the RFC protocol (e.g., `pyrfc` for Python). This should be installed and configured appropriately.

## Configuration

The `sap-connector` skill requires the following configuration:

*   SAP system connection parameters (system ID, client, username, password, language).
*   Installation and configuration of the SAP RFC library or SDK.

These configuration parameters should be stored securely and managed centrally.

## Limitations

*   Complexity: Integrating with SAP systems can be complex and requires a good understanding of the SAP data model and business processes.
*   Performance: SAP interactions can be slow, especially for large data volumes. Consider using buffering and other optimization techniques to improve performance.
*   Security: SAP systems are critical business systems and require careful security considerations. Follow security best practices to protect the data and functionality.
*   Licensing: Ensure you have the necessary licenses to access SAP data and functionality.

## Future Enhancements

*   Support for additional SAP protocols and interfaces (e.g., OData, IDoc).
*   Integration with SAP Solution Manager for monitoring and alerting.
*   Support for more advanced SAP functionality (e.g., workflow automation, change management).
*   Improved error handling and diagnostics.
```
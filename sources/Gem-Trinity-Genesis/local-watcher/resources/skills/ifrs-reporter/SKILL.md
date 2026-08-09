```markdown
---
name: ifrs-reporter
description: |
  Skill for generating IFRS (International Financial Reporting Standards) compliant financial reports from SAP data.
  This includes extracting financial data, transforming it according to IFRS guidelines, and presenting it in a standardized report format.
  The skill is designed to automate the creation of key financial statements such as the Balance Sheet, Income Statement, Cash Flow Statement, and Statement of Changes in Equity, along with supporting notes disclosures. It leverages SAP's financial modules (e.g., FI, CO) and integrates with reporting tools or APIs to produce the final reports.
version: 1.0.0
auto_generated: false
---

# ifrs-reporter

## Purpose

This skill streamlines the process of generating IFRS-compliant financial reports directly from SAP data. It aims to reduce manual effort, improve accuracy, and ensure consistency in financial reporting, adhering to the latest IFRS standards. The skill can be used for periodic reporting (e.g., monthly, quarterly, annually) and ad-hoc financial analysis.

## Functionality

The `ifrs-reporter` skill provides the following core functionalities:

*   **Data Extraction:** Extracts relevant financial data from SAP, including GL account balances, transaction data, cost center information, and other financial data points.
*   **Data Transformation:** Transforms the extracted data according to IFRS principles. This includes currency conversions, adjustments for fair value accounting, impairment calculations, and other IFRS-specific adjustments.
*   **Report Generation:** Generates financial statements and supporting notes in a standardized format, compliant with IFRS disclosure requirements. This includes the Balance Sheet, Income Statement, Cash Flow Statement, Statement of Changes in Equity, and related disclosures.
*   **Validation:** Validates the generated financial reports against IFRS rules and internal accounting policies to ensure accuracy and completeness.
*   **Reporting Tools Integration:** Integrates with various reporting tools, such as SAP Analytics Cloud (SAC), SAP BusinessObjects, or custom reporting solutions, to deliver the final reports in a desired format.
*   **Audit Trail:** Maintains an audit trail of data extraction, transformation, and reporting steps to ensure transparency and traceability.

## Actions

The `ifrs-reporter` skill provides the following actions:

### 1. `extract_financial_data`

**Description:** Extracts financial data from SAP based on specified criteria.

**Input Parameters:**

*   `company_code` (string, required): The SAP company code for which to extract data. Example: "1000"
*   `fiscal_year` (string, required): The fiscal year for which to extract data. Example: "2023"
*   `reporting_period` (string, optional): The reporting period (e.g., month, quarter) for which to extract data. If not specified, data for the entire fiscal year is extracted. Example: "Q1"
*   `gl_accounts` (list of strings, optional): A list of GL accounts to extract data for. If not specified, data for all GL accounts is extracted. Example: `["100100", "200200"]`
*   `data_sources` (list of strings, optional): A list of SAP data sources to extract data from. Supported values: "FI" (Financial Accounting), "CO" (Controlling), "AA" (Asset Accounting). If not specified, data from all supported sources is extracted. Example: `["FI", "CO"]`
*   `output_format` (string, optional): The format in which to return the extracted data. Supported values: "CSV", "JSON", "DATAFRAME". Default: "JSON".

**Output:**

*   `data` (string or dataframe, depending on `output_format`): The extracted financial data.
*   `status` (string): Status of the operation ("success" or "failure").
*   `message` (string): A message describing the result of the operation.
*   `data_format` (string): The format of the data ("CSV", "JSON", "DATAFRAME").

**Example Usage:**

```python
# Python Example
{
    "action": "extract_financial_data",
    "parameters": {
        "company_code": "1000",
        "fiscal_year": "2023",
        "reporting_period": "Q1",
        "gl_accounts": ["100100", "200200"],
        "data_sources": ["FI", "CO"],
        "output_format": "JSON"
    }
}
```

**Error Handling:**

*   Returns an error message if any of the required input parameters are missing.
*   Returns an error message if the specified company code or fiscal year is invalid.
*   Returns an error message if there are issues connecting to the SAP system.

**Best Practices:**

*   Specify only the required GL accounts and data sources to minimize the amount of data extracted.
*   Use the `reporting_period` parameter to extract data for a specific period, rather than extracting data for the entire fiscal year.
*   Consider using the "DATAFRAME" output format for large datasets, as it can be more efficient for processing and analysis.

### 2. `transform_data_to_ifrs`

**Description:** Transforms extracted financial data to comply with IFRS principles.

**Input Parameters:**

*   `data` (string or dataframe, required): The financial data to transform. Must be in the same format as the output of the `extract_financial_data` action.
*   `data_format` (string, required): The format of the input data ("CSV", "JSON", "DATAFRAME").
*   `ifrs_version` (string, optional): The specific version of IFRS to comply with. Example: "IFRS 16". If not specified, the latest version of IFRS is used.
*   `currency` (string, optional): The reporting currency. Defaults to the company's local currency if not provided.  Example: "EUR".
*   `exchange_rate_provider` (string, optional):  Specifies the source of exchange rates if currency conversion is needed.  Values: "ECB" (European Central Bank), "SAP", "CUSTOM".  If "CUSTOM" is chosen, `exchange_rates` must be provided.
*   `exchange_rates` (dictionary, optional):  If `exchange_rate_provider` is set to "CUSTOM", provide a dictionary of currency pairs and exchange rates. Example: `{"USD_EUR": 0.85}`.

**Output:**

*   `transformed_data` (string or dataframe, depending on `data_format`): The transformed financial data.
*   `status` (string): Status of the operation ("success" or "failure").
*   `message` (string): A message describing the result of the operation.

**Example Usage:**

```python
# Python Example
{
    "action": "transform_data_to_ifrs",
    "parameters": {
        "data": "[{'GL_ACCOUNT': '100100', 'BALANCE': 100000}, {'GL_ACCOUNT': '200200', 'BALANCE': 50000}]",
        "data_format": "JSON",
        "ifrs_version": "IFRS 16",
        "currency": "EUR",
        "exchange_rate_provider": "ECB"
    }
}
```

**Error Handling:**

*   Returns an error message if the input data is not in the correct format.
*   Returns an error message if the specified IFRS version is not supported.
*   Returns an error message if currency conversion fails.
*   Returns an error if custom exchange rates are needed but not provided when `exchange_rate_provider` is "CUSTOM".
*   Returns an error if invalid `exchange_rate_provider` is selected.

**Best Practices:**

*   Specify the IFRS version to ensure compliance with the correct standards.
*   Provide the reporting currency to ensure that all financial data is converted to the same currency.
*   Thoroughly test the transformation logic to ensure that it is correctly applying IFRS principles.

### 3. `generate_financial_statements`

**Description:** Generates IFRS-compliant financial statements from the transformed data.

**Input Parameters:**

*   `transformed_data` (string or dataframe, required): The transformed financial data. Must be in the same format as the output of the `transform_data_to_ifrs` action.
*   `data_format` (string, required): The format of the input data ("CSV", "JSON", "DATAFRAME").
*   `report_type` (string, required): The type of financial statement to generate. Supported values: "Balance Sheet", "Income Statement", "Cash Flow Statement", "Statement of Changes in Equity", "Notes Disclosure".
*   `output_format` (string, optional): The format in which to return the generated financial statement. Supported values: "CSV", "JSON", "PDF", "HTML". Default: "PDF".
*   `template` (string, optional): The name of a pre-defined report template to use for formatting. This allows for customization of the report layout.  If none provided, defaults to a standard IFRS format.
*   `company_name` (string, optional): The name of the company for display in the reports. Defaults to "Company Name" if not provided.
*   `as_attachment` (boolean, optional): If set to true, returns the report file as a base64 encoded string for attachment.  Only applies to PDF and HTML output formats. Defaults to `false`.

**Output:**

*   `report` (string): The generated financial statement, format depends on the `output_format`. If `as_attachment` is true and output format is PDF or HTML, this contains the base64 encoded file.
*   `status` (string): Status of the operation ("success" or "failure").
*   `message` (string): A message describing the result of the operation.
*   `report_format` (string): The format of the report ("CSV", "JSON", "PDF", "HTML").
*   `attachment` (boolean): Indicates whether the report is an attachment (base64 encoded). Only true when `as_attachment` is true and output is PDF or HTML.

**Example Usage:**

```python
# Python Example
{
    "action": "generate_financial_statements",
    "parameters": {
        "transformed_data": "[{'ACCOUNT': 'ASSETS', 'AMOUNT': 1000000}, {'ACCOUNT': 'LIABILITIES', 'AMOUNT': 500000}]",
        "data_format": "JSON",
        "report_type": "Balance Sheet",
        "output_format": "PDF",
        "company_name": "Acme Corp"
    }
}
```

**Error Handling:**

*   Returns an error message if the input data is not in the correct format.
*   Returns an error message if the specified report type is not supported.
*   Returns an error message if the report generation fails.
*   Returns an error message if the specified template does not exist.

**Best Practices:**

*   Use a pre-defined report template to ensure consistency in the report layout.
*   Specify the company name to display in the reports.
*   Thoroughly review the generated financial statements to ensure accuracy and completeness.
*   Consider using the "PDF" output format for printable reports.  Use "HTML" for embedding into web applications.

### 4. `validate_ifrs_report`

**Description:** Validates the generated IFRS financial report against IFRS guidelines and internal policies.

**Input Parameters:**

*   `report` (string): The generated financial report.
*   `report_format` (string): The format of the report ("CSV", "JSON", "PDF", "HTML").
*   `validation_rules` (list of strings, optional): A list of validation rules to apply. If not specified, a default set of IFRS validation rules is used.  Example: `["rule_1", "rule_2"]`.
*   `company_policies` (string, optional): Path to a document or link to internal company policies relevant to the report. This allows custom validation based on company specific accounting practices.
*   `ifrs_version` (string, optional): The specific version of IFRS to validate against. Example: "IFRS 16". If not specified, the latest version of IFRS is used.

**Output:**

*   `validation_results` (list of dictionaries): A list of validation results, where each result contains the rule name, the result status ("pass" or "fail"), and a message describing the result.
*   `status` (string): Status of the operation ("success" or "failure").
*   `message` (string): A message describing the result of the operation.

**Example Usage:**

```python
# Python Example
{
    "action": "validate_ifrs_report",
    "parameters": {
        "report": "{'ASSETS': 1000000, 'LIABILITIES': 500000}",
        "report_format": "JSON",
        "validation_rules": ["Assets = Liabilities + Equity", "Revenue > 0"]
    }
}
```

**Error Handling:**

*   Returns an error message if the report is not in the correct format.
*   Returns an error message if the validation fails.
*   Returns an error message if a specified validation rule is invalid.

**Best Practices:**

*   Specify a list of validation rules to ensure that the report is thoroughly validated.
*   Review the validation results carefully to identify any potential errors or inconsistencies.
*   Keep the validation rules up-to-date with the latest IFRS standards.
*   Use internal company policies for a more customized validation.

### 5. `integrate_with_reporting_tool`

**Description:** Integrates the generated financial report with a specified reporting tool.

**Input Parameters:**

*   `report` (string): The generated financial report.
*   `report_format` (string): The format of the report ("CSV", "JSON", "PDF", "HTML").
*   `reporting_tool` (string, required): The name of the reporting tool to integrate with. Supported values: "SAP Analytics Cloud", "SAP BusinessObjects", "Custom API".
*   `tool_credentials` (dictionary, optional): Credentials for the reporting tool. Required if `reporting_tool` is "SAP Analytics Cloud", "SAP BusinessObjects", or "Custom API".  The dictionary structure depends on the `reporting_tool`.  Example for SAC: `{"username": "user", "password": "password", "url": "SAC URL"}`.
*   `destination` (string, optional): Specifies the destination location within the reporting tool where the report will be uploaded or published (e.g., story ID in SAC, folder path in BusinessObjects).  Required if `reporting_tool` is "SAP Analytics Cloud" or "SAP BusinessObjects".
*   `custom_api_endpoint` (string, optional):  If `reporting_tool` is "Custom API", the URL of the API endpoint.  Required if `reporting_tool` is "Custom API".

**Output:**

*   `integration_results` (dictionary): Results of the integration, including status and any relevant messages.
*   `status` (string): Status of the operation ("success" or "failure").
*   `message` (string): A message describing the result of the operation.

**Example Usage:**

```python
# Python Example
{
    "action": "integrate_with_reporting_tool",
    "parameters": {
        "report": "<PDF Report Data>",
        "report_format": "PDF",
        "reporting_tool": "SAP Analytics Cloud",
        "tool_credentials": {"username": "user", "password": "password", "url": "SAC URL"},
        "destination": "story_123"
    }
}
```

**Error Handling:**

*   Returns an error message if the reporting tool is not supported.
*   Returns an error message if the credentials for the reporting tool are invalid.
*   Returns an error message if the integration fails.
*   Returns an error if the custom API endpoint is missing when `reporting_tool` is "Custom API".

**Best Practices:**

*   Ensure that the credentials for the reporting tool are securely stored.
*   Test the integration thoroughly to ensure that the report is correctly integrated.
*   Monitor the integration process to identify and resolve any issues.
*   For "Custom API", ensure proper authentication and authorization are implemented at the API endpoint.

## Example Workflow

1.  The user initiates the reporting process by specifying the `company_code`, `fiscal_year`, and `reporting_period`.
2.  The `extract_financial_data` action extracts the relevant financial data from SAP.
3.  The `transform_data_to_ifrs` action transforms the extracted data to comply with IFRS principles.
4.  The `generate_financial_statements` action generates the desired financial statements (e.g., Balance Sheet, Income Statement).
5.  The `validate_ifrs_report` action validates the generated financial statements against IFRS guidelines and internal policies.
6.  The `integrate_with_reporting_tool` action integrates the validated financial statements with a reporting tool (e.g., SAP Analytics Cloud).
7.  The user can then access and view the financial reports in the reporting tool.

## Security Considerations

*   Securely store the credentials for accessing the SAP system and reporting tools.
*   Implement proper authorization and authentication mechanisms to prevent unauthorized access to financial data and reports.
*   Regularly review and update the validation rules to ensure compliance with the latest IFRS standards.
*   Sanitize and validate all input parameters to prevent injection attacks.

## Dependencies

*   SAP system with access to financial data.
*   Reporting tool (e.g., SAP Analytics Cloud, SAP BusinessObjects).
*   Libraries for data extraction, transformation, and reporting (e.g., pandas, numpy, requests).
*   Connection setup to SAP (via RFC or API).

## Limitations

*   The skill may not support all IFRS standards or all types of financial transactions.
*   The skill may require customization to meet specific reporting requirements.
*   The performance of the skill may be affected by the size and complexity of the financial data.
```
```markdown
---
name: email-campaign
description: Skill for managing and analyzing email marketing campaigns. Includes actions for creating campaigns, sending emails, tracking performance metrics (opens, clicks, bounces), and generating reports. Designed to integrate with email service providers (ESPs) via API.
version: 1.0.0
auto_generated: false
---

# email-campaign

## Purpose

This skill enables the AI agent to manage and analyze email marketing campaigns. It provides a set of actions for creating, sending, and monitoring campaigns through integration with an Email Service Provider (ESP) API. The skill also allows for generating reports based on campaign performance data.

## Usage

This skill is intended to be used by other skills or directly by the AI agent to automate email marketing tasks, analyze campaign performance, and optimize strategies. Before using this skill, ensure that the ESP API credentials are properly configured and stored securely.

## Actions

### 1. `create_campaign`

**Description:** Creates a new email campaign in the ESP.

**Parameters:**

*   `campaign_name` (string, required): The name of the campaign. Must be unique within the ESP.
*   `subject_line` (string, required): The subject line of the email.
*   `sender_name` (string, required): The name of the sender.
*   `sender_email` (string, required): The email address of the sender. Must be a verified sender within the ESP.
*   `reply_to_email` (string, optional): The email address to which replies should be sent. If not provided, defaults to `sender_email`.
*   `template_id` (string, required): The ID of the email template to use. This template must exist in the ESP.  The template should support dynamic content insertion, if personalization is required.
*   `list_id` (string, required): The ID of the recipient list to use. This list must exist in the ESP.
*   `segment_id` (string, optional): The ID of a segment within the recipient list to target. If not provided, the entire list is targeted.
*   `is_transactional` (boolean, optional):  Indicates if the email is transactional (e.g., password reset). Defaults to `false`. Transactional emails are often handled differently by ESPs in terms of deliverability and opt-out rules.
*   `tags` (list of strings, optional): A list of tags to associate with the campaign.  Useful for categorization and reporting within the ESP.

**Returns:**

*   `campaign_id` (string): The ID of the newly created campaign.
*   `status` (string): The status of the campaign creation (e.g., "created", "error").
*   `error_message` (string, optional):  An error message if the campaign creation failed.

**Example:**

```python
campaign_details = {
    "campaign_name": "Summer Sale 2024",
    "subject_line": "🔥 Summer Sale is Here! Up to 70% Off!",
    "sender_name": "Acme Corp",
    "sender_email": "sales@acmecorp.com",
    "reply_to_email": "support@acmecorp.com",
    "template_id": "summer_sale_template_123",
    "list_id": "customer_list_456",
    "segment_id": "vip_customers_789",
    "tags": ["summer", "sale", "promotion"]
}

result = email_campaign.create_campaign(**campaign_details)

if result["status"] == "created":
    print(f"Campaign created successfully with ID: {result['campaign_id']}")
else:
    print(f"Error creating campaign: {result['error_message']}")
```

**Edge Cases:**

*   The `campaign_name` must be unique within the ESP.  The action should check for existing campaigns with the same name and return an error if a duplicate is found.
*   The `template_id` and `list_id` must correspond to existing templates and lists in the ESP.  The action should validate these IDs against the ESP and return an error if they are invalid.
*   The `sender_email` must be a verified sender within the ESP.  The action should verify the sender email and return an error if it is not verified.
*   If the API call to the ESP fails (e.g., due to network issues or API rate limits), the action should retry the call a few times before returning an error.  Implement exponential backoff for retries.
*   If `segment_id` is provided, ensure the segment exists within the specified `list_id`.

**Best Practices:**

*   Use descriptive campaign names for easy identification.
*   Use A/B testing to optimize subject lines and email content. Consider building an A/B test action within this skill.
*   Segment your audience to personalize your messaging.
*   Add tags to your campaigns for better reporting and analysis.

### 2. `send_campaign`

**Description:** Sends an email campaign to the specified recipient list or segment.

**Parameters:**

*   `campaign_id` (string, required): The ID of the campaign to send.
*   `send_time` (datetime string, optional): The date and time to send the campaign.  If not provided, the campaign is sent immediately.  The format should be ISO 8601 (e.g., "2024-07-15T10:00:00Z").  ESPs typically use UTC time.
*   `batch_size` (integer, optional): The number of emails to send in each batch.  Defaults to 100.  Adjust this value based on ESP API rate limits.
*   `max_retries` (integer, optional): The maximum number of times to retry sending an email if it fails. Defaults to 3.

**Returns:**

*   `status` (string): The status of the campaign sending (e.g., "queued", "sending", "sent", "error").
*   `start_time` (datetime string): The actual start time of sending (ISO 8601 format).
*   `end_time` (datetime string, optional): The actual end time of sending (ISO 8601 format). Only returned when the status is "sent".
*   `error_message` (string, optional): An error message if the campaign sending failed.

**Example:**

```python
send_details = {
    "campaign_id": "summer_sale_campaign_123",
    "send_time": "2024-07-01T09:00:00Z"  # July 1st, 9:00 AM UTC
}

result = email_campaign.send_campaign(**send_details)

if result["status"] == "queued":
    print(f"Campaign sending queued successfully. Start time: {result['start_time']}")
elif result["status"] == "sent":
    print(f"Campaign sent successfully. End time: {result['end_time']}")
else:
    print(f"Error sending campaign: {result['error_message']}")
```

**Edge Cases:**

*   The `campaign_id` must correspond to an existing campaign in the ESP.  The action should validate the campaign ID against the ESP and return an error if it is invalid.
*   If `send_time` is in the past, the action should either return an error or schedule the campaign to be sent immediately, depending on the desired behavior.  The behavior should be configurable.
*   ESP API rate limits must be handled gracefully.  Use the `batch_size` parameter to control the number of emails sent in each batch and implement retry logic with exponential backoff.
*   Handle potential errors during the sending process, such as temporary ESP outages or invalid recipient email addresses.  Log these errors and retry sending the affected emails if appropriate.

**Best Practices:**

*   Schedule campaigns in advance to optimize sending times.
*   Monitor campaign performance closely after sending.
*   Use throttling mechanisms to avoid overwhelming the ESP API.
*   Implement proper error handling and logging.

### 3. `get_campaign_metrics`

**Description:** Retrieves performance metrics for a specific email campaign.

**Parameters:**

*   `campaign_id` (string, required): The ID of the campaign to retrieve metrics for.
*   `start_date` (date string, optional): The start date for the metric retrieval. If not provided, defaults to the campaign creation date. Format should be YYYY-MM-DD.
*   `end_date` (date string, optional): The end date for the metric retrieval. If not provided, defaults to the current date. Format should be YYYY-MM-DD.
*   `metrics` (list of strings, optional): A list of metrics to retrieve.  If not provided, retrieves all available metrics. Valid metrics include: `opens`, `clicks`, `bounces`, `unsubscribes`, `spam_complaints`, `deliveries`.

**Returns:**

*   `campaign_id` (string): The ID of the campaign.
*   `start_date` (date string): The start date for the metric retrieval.
*   `end_date` (date string): The end date for the metric retrieval.
*   `metrics` (dictionary): A dictionary of metrics, where the keys are the metric names and the values are the corresponding counts or rates.  Example: `{"opens": 1234, "clicks": 567, "bounces": 123}`.
*   `status` (string): The status of the metric retrieval (e.g., "success", "error").
*   `error_message` (string, optional): An error message if the metric retrieval failed.

**Example:**

```python
metrics_details = {
    "campaign_id": "summer_sale_campaign_123",
    "start_date": "2024-06-01",
    "end_date": "2024-06-30",
    "metrics": ["opens", "clicks", "bounces"]
}

result = email_campaign.get_campaign_metrics(**metrics_details)

if result["status"] == "success":
    print(f"Campaign metrics for campaign ID {result['campaign_id']} from {result['start_date']} to {result['end_date']}:")
    for metric, value in result["metrics"].items():
        print(f"  {metric}: {value}")
else:
    print(f"Error retrieving campaign metrics: {result['error_message']}")
```

**Edge Cases:**

*   The `campaign_id` must correspond to an existing campaign in the ESP.  The action should validate the campaign ID against the ESP and return an error if it is invalid.
*   The `start_date` and `end_date` must be valid dates and `start_date` must be before `end_date`. Return an error if this is not the case.
*   If the ESP API does not support retrieving specific metrics, the action should retrieve all available metrics and filter them based on the `metrics` parameter.
*   Handle potential errors during the metric retrieval process, such as temporary ESP outages or invalid date ranges.  Log these errors and retry the retrieval if appropriate.

**Best Practices:**

*   Retrieve metrics regularly to monitor campaign performance and identify areas for improvement.
*   Use the `start_date` and `end_date` parameters to retrieve metrics for specific time periods.
*   Store retrieved metrics in a database for historical analysis.

### 4. `generate_report`

**Description:** Generates a report based on the performance metrics of one or more email campaigns.

**Parameters:**

*   `campaign_ids` (list of strings, required): A list of campaign IDs to include in the report.
*   `start_date` (date string, optional): The start date for the metric retrieval. If not provided, defaults to the earliest campaign creation date. Format should be YYYY-MM-DD.
*   `end_date` (date string, optional): The end date for the metric retrieval. If not provided, defaults to the current date. Format should be YYYY-MM-DD.
*   `report_type` (string, optional): The type of report to generate.  Valid values include: "summary", "detailed", "comparison". Defaults to "summary".
    *   "summary":  Provides overall metrics for all campaigns combined.
    *   "detailed": Provides metrics for each campaign individually.
    *   "comparison": Provides a side-by-side comparison of metrics for all campaigns.
*   `format` (string, optional): The format of the report. Valid values include: "text", "csv", "json".  Defaults to "text".
*    `output_file` (string, optional): The file path to save the report to. If not provided, the report is returned as a string.

**Returns:**

*   `report_content` (string): The content of the report, in the specified format.
*   `file_path` (string, optional): The path to the generated report file. Only returned if `output_file` is specified.
*   `status` (string): The status of the report generation (e.g., "success", "error").
*   `error_message` (string, optional): An error message if the report generation failed.

**Example:**

```python
report_details = {
    "campaign_ids": ["summer_sale_campaign_123", "winter_sale_campaign_456"],
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "report_type": "comparison",
    "format": "csv",
    "output_file": "email_campaign_report.csv"
}

result = email_campaign.generate_report(**report_details)

if result["status"] == "success":
    if "file_path" in result:
        print(f"Report generated successfully and saved to: {result['file_path']}")
    else:
        print(f"Report generated successfully. Content:\n{result['report_content']}")
else:
    print(f"Error generating report: {result['error_message']}")
```

**Edge Cases:**

*   The `campaign_ids` must correspond to existing campaigns in the ESP. The action should validate the campaign IDs against the ESP and return an error if any are invalid.
*   If no campaigns are found for the specified date range, the action should return an empty report or an error message, depending on the desired behavior.
*   Ensure that the `report_type` and `format` parameters are valid.  Return an error if they are not.
*   Handle potential errors during the report generation process, such as insufficient data or invalid output file paths. Log these errors and retry the generation if appropriate.
*   For large datasets, consider using pagination or streaming to avoid memory issues.

**Best Practices:**

*   Generate reports regularly to track campaign performance and identify trends.
*   Use different report types to gain different insights into your campaigns.
*   Export reports in various formats for further analysis.
*   Use the `output_file` parameter to save reports for later use.

### 5. `list_campaigns`

**Description:** Retrieves a list of all email campaigns from the ESP. Allows filtering by status and date range.

**Parameters:**

*   `status` (string, optional): Filter campaigns by their status. Possible values include: "draft", "queued", "sending", "sent", "error". If not provided, all campaigns are returned.
*   `start_date` (date string, optional): Filter campaigns created after this date. Format: YYYY-MM-DD.
*   `end_date` (date string, optional): Filter campaigns created before this date. Format: YYYY-MM-DD.
*   `limit` (integer, optional): The maximum number of campaigns to return. Defaults to 100.
*   `offset` (integer, optional): The number of campaigns to skip. Used for pagination. Defaults to 0.

**Returns:**

*   `campaigns` (list of dictionaries): A list of campaign objects. Each campaign object contains the following keys: `campaign_id`, `campaign_name`, `status`, `creation_date`, `subject_line`, `sender_name`, `sender_email`.
*   `total_count` (integer): The total number of campaigns matching the filter criteria (regardless of `limit` and `offset`).
*   `status` (string): The status of the retrieval (e.g., "success", "error").
*   `error_message` (string, optional): An error message if the retrieval failed.

**Example:**

```python
list_params = {
    "status": "sent",
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "limit": 20,
    "offset": 0
}

result = email_campaign.list_campaigns(**list_params)

if result["status"] == "success":
    print(f"Found {result['total_count']} sent campaigns between 2024-01-01 and 2024-06-30.")
    for campaign in result["campaigns"]:
        print(f"  Campaign ID: {campaign['campaign_id']}, Name: {campaign['campaign_name']}, Subject: {campaign['subject_line']}")
else:
    print(f"Error listing campaigns: {result['error_message']}")
```

**Edge Cases:**

*   If no campaigns match the filter criteria, the action should return an empty list of campaigns and a `total_count` of 0.
*   The `status` parameter should be validated against the ESP's supported status values. Return an error if an invalid status is provided.
*   Handle API rate limits by implementing pagination using the `limit` and `offset` parameters.

**Best Practices:**

*   Use the `status` parameter to filter campaigns by their current status.
*   Use the `start_date` and `end_date` parameters to filter campaigns by their creation date.
*   Implement pagination to retrieve large numbers of campaigns.

## Configuration

This skill requires configuration to connect to an Email Service Provider (ESP) API. The following configuration parameters must be provided:

*   `esp_api_key` (string, required): The API key for the ESP.  Store securely (e.g., in environment variables or a secrets manager).
*   `esp_api_url` (string, required): The base URL for the ESP API.
*   `esp_provider` (string, required): The name of the ESP provider (e.g., "Mailchimp", "SendGrid", "Amazon SES").  This is used to determine the correct API calls and data formats.
*    `rate_limit_requests_per_minute` (integer, optional): The maximum number of API requests that can be made per minute. Defaults to 60. This value depends on the specific ESP being used.

The configuration parameters can be set via environment variables, a configuration file, or directly in the code. It is recommended to store sensitive information (e.g., API keys) in a secure location.

## Error Handling

This skill implements robust error handling to gracefully handle unexpected situations. The following types of errors are handled:

*   **API errors:** Errors returned by the ESP API (e.g., invalid API key, invalid request parameters, rate limits).
*   **Network errors:** Errors that occur during network communication (e.g., connection timeouts, DNS resolution failures).
*   **Data validation errors:** Errors that occur when validating input data (e.g., invalid email address, invalid date format).
*   **File system errors:** Errors that occur when interacting with the file system (e.g., file not found, permission denied).

When an error occurs, the skill logs the error message and returns an appropriate error status to the caller. The caller can then handle the error and take appropriate action. Retries with exponential backoff are used for transient errors (e.g., network errors, temporary ESP outages).

## Dependencies

This skill depends on the following libraries:

*   `requests`: For making HTTP requests to the ESP API.
*   `datetime`: For working with dates and times.
*   `json`: For working with JSON data.

These libraries must be installed before using this skill. You can install them using pip:

```bash
pip install requests datetime json
```

Furthermore, a helper module to interface with the specific ESP will be necessary.  For example, `mailchimp_client.py`, `sendgrid_client.py`, etc.  These modules should handle authentication, rate limiting, and data transformation to and from the ESP's API.

## Security Considerations

*   Store API keys securely. Avoid hardcoding API keys in the code. Use environment variables or a secrets manager instead.
*   Validate all input data to prevent injection attacks.
*   Implement proper authentication and authorization to restrict access to the skill.
*   Log all API requests and responses for auditing purposes.
*   Regularly update the skill's dependencies to address security vulnerabilities.
*   Be mindful of data privacy regulations (e.g., GDPR) when handling email addresses and other personal data.  Ensure you have appropriate consent before sending emails.
*   Implement rate limiting to protect against abuse and prevent exceeding ESP API rate limits.

## Future Enhancements

*   Add support for more ESPs.
*   Implement A/B testing functionality.
*   Add support for managing email templates and recipient lists.
*   Implement advanced segmentation options.
*   Integrate with other marketing automation tools.
*   Add real-time campaign monitoring capabilities.
*   Implement predictive analytics to forecast campaign performance.
```
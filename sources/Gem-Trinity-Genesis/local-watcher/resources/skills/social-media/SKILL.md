```markdown
---
name: social-media
description: Skill for interacting with social media platforms to manage accounts, create and schedule posts, analyze performance metrics, and engage with audiences. Supports multiple platforms via API and provides robust error handling and reporting.
version: 1.0.0
auto_generated: false
---

# social-media

## Purpose

This skill enables the AI agent to manage social media presence, analyze performance, and engage with audiences across various platforms. It provides a comprehensive set of actions for creating, scheduling, and publishing posts, monitoring brand mentions, analyzing engagement metrics, and responding to comments and messages.

## Supported Platforms

*   **X (formerly Twitter):** Account management, tweet posting, trend analysis, direct messaging.
*   **Facebook:** Page management, post creation and scheduling, ad campaign analysis, group engagement.
*   **Instagram:** Post and story creation, hashtag analysis, audience insights, direct messaging.
*   **LinkedIn:** Profile management, post publishing, connection requests, group discussions.
*   **YouTube:** Video uploads, playlist management, comment moderation, analytics tracking.
*   (Future support for TikTok, Pinterest, etc. can be added through modular design.)

## Actions

### 1. `create_post`

**Description:** Creates and schedules a social media post.

**Parameters:**

*   `platform` (string, required): The target social media platform (e.g., "X", "Facebook", "Instagram", "LinkedIn", "YouTube").
*   `account_id` (string, required): The ID of the social media account to post from.
*   `content` (string, required): The text or caption of the post.  Maximum length is platform dependent (e.g., X: 280 characters).  Consider using `shorten_text` skill to ensure the content is below the allowed limit.
*   `media_url` (string, optional): URL of an image or video to include in the post.  Supported file types and size limits vary by platform. Handle errors with platform specific limits gracefully (e.g., image size exceeds limit).
*   `scheduled_time` (datetime string, optional): The date and time to schedule the post.  If not provided, the post will be published immediately.  Format should be ISO 8601 (e.g., "2024-10-27T10:00:00Z").
*   `options` (dict, optional): A dictionary of platform-specific options. Examples:
    *   X: `{"poll_options": ["Yes", "No"], "duration_minutes": 1440}` for creating a poll.
    *   Facebook: `{"target_audience": "marketing_professionals"}` for targeted posts.
    *   Instagram: `{"location": "New York City"}` for geotagging.
    *   YouTube: `{"privacy_status": "private", "tags": ["marketing", "analysis"]}`
*   `shorten_links` (boolean, optional): Whether to automatically shorten any links in the `content` using a link shortening service. Defaults to `true`.

**Returns:**

*   `post_id` (string): The ID of the created post.
*   `status` (string): "scheduled" or "published".
*   `platform` (string): The platform where the post was created.

**Error Handling:**

*   Raises `ValueError` if required parameters are missing.
*   Raises `PlatformNotSupportedError` if the specified platform is not supported.
*   Raises `AuthenticationError` if authentication fails for the specified account.
*   Raises `ContentValidationError` if the content violates platform guidelines (e.g., exceeding character limits, containing prohibited content).
*   Raises `MediaValidationError` if the media file is invalid (e.g., unsupported format, excessive size).
*   Raises `SchedulingError` if scheduling fails (e.g., invalid scheduled time).
*   Logs errors to the error tracking system.

**Code Example (Python):**

```python
import datetime

def create_post(platform, account_id, content, media_url=None, scheduled_time=None, options=None, shorten_links=True):
    """Creates and schedules a social media post."""
    if not platform or not account_id or not content:
        raise ValueError("Platform, account_id, and content are required.")

    # Platform-specific authentication and API calls would go here.
    # Mock implementation for demonstration:
    print(f"Creating post on {platform} for account {account_id}")
    print(f"Content: {content}")
    if media_url:
        print(f"Media URL: {media_url}")
    if scheduled_time:
        print(f"Scheduled time: {scheduled_time}")
    if options:
        print(f"Options: {options}")

    post_id = "post_" + str(hash(content + str(datetime.datetime.now()))) # Mock post ID
    status = "scheduled" if scheduled_time else "published"

    return {
        "post_id": post_id,
        "status": status,
        "platform": platform
    }

# Example usage:
try:
    post_details = create_post(
        platform="X",
        account_id="my_x_account",
        content="Check out our latest marketing analysis!",
        media_url="https://example.com/image.jpg",
        scheduled_time="2024-10-28T12:00:00Z",
        options={"poll_options": ["Yes", "No"], "duration_minutes": 1440}
    )
    print(f"Post created: {post_details}")
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

**Best Practices:**

*   Implement robust error handling to gracefully handle API errors and platform-specific limitations.
*   Use a configuration file or environment variables to store API keys and account credentials securely.
*   Implement rate limiting to avoid exceeding API usage limits.
*   Sanitize user input to prevent cross-site scripting (XSS) vulnerabilities.
*   Log all actions and errors for auditing and debugging purposes.
*   Provide clear and informative error messages to the user.
*   Use a dedicated library for handling date and time formatting to ensure consistency across different platforms.

### 2. `get_account_metrics`

**Description:** Retrieves performance metrics for a social media account.

**Parameters:**

*   `platform` (string, required): The social media platform (e.g., "X", "Facebook", "Instagram", "LinkedIn", "YouTube").
*   `account_id` (string, required): The ID of the social media account.
*   `start_date` (date string, required): The start date for the metrics period (ISO 8601 format: "YYYY-MM-DD").
*   `end_date` (date string, required): The end date for the metrics period (ISO 8601 format: "YYYY-MM-DD").
*   `metrics` (list of strings, optional): A list of specific metrics to retrieve. If not provided, all available metrics will be returned.  Examples: `["followers", "impressions", "engagement_rate"]`.  The available metrics are platform-specific (see below).

**Available Metrics (Platform Specific):**

*   **X:** `["followers", "impressions", "engagements", "retweets", "likes", "replies", "profile_visits"]`
*   **Facebook:** `["page_likes", "reach", "impressions", "engagement", "video_views"]`
*   **Instagram:** `["followers", "reach", "impressions", "profile_visits", "website_clicks"]`
*   **LinkedIn:** `["followers", "impressions", "clicks", "engagement"]`
*   **YouTube:** `["views", "watch_time", "subscribers", "likes", "dislikes", "comments"]`

**Returns:**

*   `metrics_data` (dict): A dictionary containing the requested metrics and their values for the specified period. The keys of the dictionary are the metric names.  Values are typically numeric (integers or floats).  Dates may be present in some metrics (e.g., daily followers count).

**Error Handling:**

*   Raises `ValueError` if required parameters are missing.
*   Raises `PlatformNotSupportedError` if the specified platform is not supported.
*   Raises `AuthenticationError` if authentication fails for the specified account.
*   Raises `InvalidDateRangeError` if the start date is after the end date.
*   Raises `MetricNotAvailableError` if a requested metric is not available for the specified platform.
*   Logs errors to the error tracking system.

**Code Example (Python):**

```python
import datetime

def get_account_metrics(platform, account_id, start_date, end_date, metrics=None):
    """Retrieves performance metrics for a social media account."""
    if not platform or not account_id or not start_date or not end_date:
        raise ValueError("Platform, account_id, start_date, and end_date are required.")

    try:
        datetime.datetime.strptime(start_date, '%Y-%m-%d')
        datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date format.  Use YYYY-MM-DD.")

    if start_date > end_date:
        raise ValueError("Start date cannot be after end date.")

    # Platform-specific API calls would go here.
    # Mock implementation for demonstration:
    print(f"Getting metrics for {platform} account {account_id}")
    print(f"Start date: {start_date}, End date: {end_date}")
    if metrics:
        print(f"Requested metrics: {metrics}")

    # Mock metrics data
    metrics_data = {
        "followers": 12345,
        "impressions": 67890,
        "engagement_rate": 0.05,
    }

    if metrics:
       filtered_metrics = {k: v for k, v in metrics_data.items() if k in metrics}
       return filtered_metrics

    return metrics_data

# Example usage:
try:
    metrics = get_account_metrics(
        platform="X",
        account_id="my_x_account",
        start_date="2024-01-01",
        end_date="2024-01-31",
        metrics=["followers", "impressions"]
    )
    print(f"Metrics: {metrics}")
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

**Best Practices:**

*   Cache API responses to reduce the number of API calls and improve performance.
*   Use a dedicated library for handling date and time calculations.
*   Implement pagination to handle large datasets.
*   Normalize metrics data across different platforms for easier analysis.
*   Validate the metrics data against expected ranges to detect anomalies.

### 3. `monitor_mentions`

**Description:** Monitors social media platforms for mentions of a specific keyword or brand.

**Parameters:**

*   `platform` (string, required): The social media platform (e.g., "X", "Facebook", "Instagram", "LinkedIn", "YouTube").
*   `keywords` (list of strings, required): A list of keywords or phrases to monitor.
*   `start_date` (date string, optional): The start date for monitoring (ISO 8601 format: "YYYY-MM-DD"). If not provided, monitoring starts immediately.
*   `end_date` (date string, optional): The end date for monitoring (ISO 8601 format: "YYYY-MM-DD"). If not provided, monitoring continues indefinitely.
*   `options` (dict, optional): Platform specific options, for example:
    *   X: `{"exclude_retweets": true}` to exclude retweets from results
    *   Facebook: `{"group_ids": ["group1", "group2"]}` to only monitor specific groups

**Returns:**

*   `mentions` (list of dicts): A list of dictionaries, where each dictionary represents a mention. Each dictionary contains the following keys:
    *   `platform` (string): The platform where the mention occurred.
    *   `content` (string): The text of the mention.
    *   `author` (string): The author of the mention (username or page name).
    *   `url` (string): The URL of the mention.
    *   `timestamp` (datetime string): The date and time of the mention (ISO 8601 format).
    *   `sentiment` (string, optional): The sentiment of the mention ("positive", "negative", or "neutral").  Sentiment analysis requires additional NLP capabilities.

**Error Handling:**

*   Raises `ValueError` if required parameters are missing.
*   Raises `PlatformNotSupportedError` if the specified platform is not supported.
*   Raises `AuthenticationError` if authentication fails.
*   Raises `RateLimitError` if the API rate limit is exceeded.
*   Logs errors to the error tracking system.

**Code Example (Python):**

```python
import datetime

def monitor_mentions(platform, keywords, start_date=None, end_date=None, options=None):
    """Monitors social media platforms for mentions of a specific keyword or brand."""
    if not platform or not keywords:
        raise ValueError("Platform and keywords are required.")

    # Platform-specific API calls would go here.
    # Mock implementation for demonstration:
    print(f"Monitoring {platform} for keywords: {keywords}")
    if start_date:
        print(f"Start date: {start_date}")
    if end_date:
        print(f"End date: {end_date}")
    if options:
        print(f"Options: {options}")

    # Mock mentions data
    mentions = [
        {
            "platform": platform,
            "content": f"Great article about {keywords[0]}!",
            "author": "user123",
            "url": "https://example.com/mention1",
            "timestamp": datetime.datetime.now().isoformat(),
            "sentiment": "positive"
        },
        {
            "platform": platform,
            "content": f"I'm not a fan of {keywords[0]}...",
            "author": "another_user",
            "url": "https://example.com/mention2",
            "timestamp": datetime.datetime.now().isoformat(),
            "sentiment": "negative"
        }
    ]

    return mentions

# Example usage:
try:
    mentions = monitor_mentions(
        platform="X",
        keywords=["marketing_analysis_agent"],
        start_date="2024-10-27",
        end_date="2024-10-28",
        options={"exclude_retweets": True}
    )
    print(f"Mentions: {mentions}")
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

**Best Practices:**

*   Use a robust NLP library for sentiment analysis.
*   Filter out irrelevant mentions using advanced filtering techniques.
*   Implement real-time monitoring using webhooks or streaming APIs.
*   Prioritize mentions based on influence and sentiment.
*   Store mentions in a database for historical analysis.
*   Consider handling edge cases in keyword matching (e.g., misspellings, variations in phrasing).  Fuzzy matching or semantic similarity techniques can improve accuracy.

### 4. `engage_with_mention`

**Description:** Responds to a social media mention.

**Parameters:**

*   `platform` (string, required): The social media platform (e.g., "X", "Facebook", "Instagram", "LinkedIn", "YouTube").
*   `mention_url` (string, required): The URL of the mention.
*   `response_text` (string, required): The text of the response.
*   `account_id` (string, optional): The social media account used to respond. If omitted, attempts to find a default account.

**Returns:**

*   `status` (string): "success" or "failed".
*   `response_url` (string, optional): The URL of the response, if successful.

**Error Handling:**

*   Raises `ValueError` if required parameters are missing.
*   Raises `PlatformNotSupportedError` if the specified platform is not supported.
*   Raises `AuthenticationError` if authentication fails.
*   Raises `MentionNotFoundError` if the mention URL is invalid or not found.
*   Raises `RateLimitError` if the API rate limit is exceeded.
*   Logs errors to the error tracking system.

**Code Example (Python):**

```python
def engage_with_mention(platform, mention_url, response_text, account_id=None):
    """Responds to a social media mention."""
    if not platform or not mention_url or not response_text:
        raise ValueError("Platform, mention_url, and response_text are required.")

    # Platform-specific API calls would go here.
    # Mock implementation for demonstration:
    print(f"Engaging with mention on {platform} at {mention_url}")
    print(f"Response text: {response_text}")
    if account_id:
       print(f"Responding as {account_id}")
    else:
       print(f"Responding as default account")


    # Mock response
    status = "success"
    response_url = "https://example.com/response"

    return {
        "status": status,
        "response_url": response_url
    }

# Example usage:
try:
    response = engage_with_mention(
        platform="X",
        mention_url="https://x.com/user123/status/1234567890",
        response_text="Thanks for your feedback!",
        account_id="marketing_x_account"
    )
    print(f"Response: {response}")
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

**Best Practices:**

*   Implement a content moderation policy to ensure that responses are appropriate and compliant.
*   Use a consistent tone and voice in responses.
*   Personalize responses to individual users whenever possible.
*   Track the effectiveness of responses by monitoring engagement metrics.
*   Avoid automated responses to sensitive or critical issues.

### 5. `get_trending_topics`

**Description:** Retrieves trending topics for a specific platform and location.

**Parameters:**

*   `platform` (string, required): The social media platform (currently only supports "X").
*   `location` (string, optional): The location to retrieve trending topics for (e.g., "Worldwide", "New York", "London"). If not provided, defaults to worldwide.

**Returns:**

*   `trending_topics` (list of strings): A list of trending topics.

**Error Handling:**

*   Raises `ValueError` if required parameters are missing.
*   Raises `PlatformNotSupportedError` if the specified platform is not supported.
*   Raises `LocationNotSupportedError` if the specified location is not supported.
*   Raises `AuthenticationError` if authentication fails.
*   Raises `RateLimitError` if the API rate limit is exceeded.

**Code Example (Python):**

```python
def get_trending_topics(platform, location="Worldwide"):
    """Retrieves trending topics for a specific platform and location."""
    if not platform:
        raise ValueError("Platform is required.")

    if platform != "X":
        raise PlatformNotSupportedError(f"Platform {platform} is not supported. Only X is supported.")


    # Platform-specific API calls would go here.
    # Mock implementation for demonstration:
    print(f"Getting trending topics on {platform} in {location}")

    # Mock trending topics data
    trending_topics = [
        "AI Marketing",
        "Data Analysis",
        "Machine Learning"
    ]

    return trending_topics

# Example usage:
try:
    trending_topics = get_trending_topics(platform="X", location="Worldwide")
    print(f"Trending topics: {trending_topics}")
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

**Best Practices:**

*   Cache trending topics to reduce the number of API calls.
*   Use trending topics to inform content creation and engagement strategies.
*   Monitor trending topics for potential crises or opportunities.
*   Consider the relevance and appropriateness of trending topics before incorporating them into content.

## Custom Exceptions

```python
class PlatformNotSupportedError(Exception):
    """Raised when the specified platform is not supported."""
    pass

class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass

class ContentValidationError(Exception):
    """Raised when content violates platform guidelines."""
    pass

class MediaValidationError(Exception):
    """Raised when the media file is invalid."""
    pass

class SchedulingError(Exception):
    """Raised when scheduling fails."""
    pass

class InvalidDateRangeError(Exception):
    """Raised when the date range is invalid."""
    pass

class MetricNotAvailableError(Exception):
    """Raised when a requested metric is not available."""
    pass

class MentionNotFoundError(Exception):
    """Raised when the mention URL is invalid or not found."""
    pass

class RateLimitError(Exception):
    """Raised when the API rate limit is exceeded."""
    pass

class LocationNotSupportedError(Exception):
    """Raised when the specified location is not supported."""
    pass
```

## Configuration

The skill requires the following configuration:

*   API keys and access tokens for each supported social media platform.
*   Account IDs for each social media account to be managed.
*   Optional: A link shortening service API key (e.g., Bitly).
*   Optional: An NLP service API key for sentiment analysis.

These configurations should be stored securely, for example, in environment variables or a secure configuration file. The agent should be configured to load these values when the skill is initialized.  Example environment variables:

```
X_API_KEY=your_x_api_key
X_API_SECRET=your_x_api_secret
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
INSTAGRAM_ACCOUNT_ID=your_instagram_account_id
```

## Security Considerations

*   Store API keys and access tokens securely.  Never hardcode them directly into the code.
*   Implement rate limiting to prevent abuse and avoid exceeding API limits.
*   Sanitize user input to prevent cross-site scripting (XSS) and other vulnerabilities.
*   Regularly review and update security configurations.
*   Implement access control mechanisms to restrict access to sensitive data and functions.
```
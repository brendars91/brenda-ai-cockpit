```markdown
---
name: sap-knowledge-base
description: Provides access to SAP's knowledge base and help documentation to answer questions related to SAP systems, modules, transactions, and functionalities. Use this skill to retrieve accurate and up-to-date information about SAP configurations, troubleshooting steps, best practices, and related topics. Prioritize official SAP documentation and community resources before summarizing or offering opinions. Focus on providing direct answers and links to relevant resources to avoid hallucination.
license: Complete terms in LICENSE.txt
---

# SAP Knowledge Base Skill

## Overview

This skill enables the AI agent to query and retrieve information from SAP's extensive knowledge base. It facilitates answering user questions about SAP systems, modules (e.g., FI, MM, SD), transactions (e.g., SE38, SU01, VA01), and associated functionalities. This includes access to official SAP documentation, SAP Notes, SAP Community Wiki, and other relevant resources.

**Keywords:** SAP, ERP, documentation, help, SAP Notes, SAP Community, configuration, troubleshooting, transactions, modules, S/4HANA, ABAP, Fiori, Basis, security, implementation, integration

## Input Parameters

The skill accepts a single input parameter:

*   **`query` (string, required):** A natural language query describing the information needed from the SAP knowledge base. This should be a clear and concise question or request. Examples:
    *   "How to create a purchase order in SAP MM?"
    *   "What is the transaction code to create a new user in SAP?"
    *   "How to configure automatic payment processing in SAP FI?"
    *   "Troubleshooting steps for a failed IDoc in SAP PI/PO."
    *   "S/4HANA migration best practices for Finance module."
    *   "What are the security considerations for implementing SAP Fiori?"
    *   "How to implement Single Sign-On (SSO) with SAP NetWeaver?"
    *   "Explain the difference between SAP ECC and S/4HANA."

## Output

The skill returns a JSON object containing the following fields:

*   **`results` (array):** An array of search results from the SAP knowledge base, ranked by relevance. Each result object contains:
    *   **`title` (string):** The title of the SAP documentation or resource.
    *   **`url` (string):** A direct link to the resource on the SAP website. Always prefer links to `help.sap.com` or `support.sap.com` when available.
    *   **`snippet` (string):** A brief excerpt from the resource that provides context to the search query. Focus on providing the most relevant snippet to answer the user’s question.

*   **`summary` (string, optional):** A concise summary of the key information found in the search results. This should be a short answer to the user's query, referencing the source documents in the `results` array. Include citations to the documents where the information was found.
    *   This field is only populated if the agent can confidently synthesize a coherent and accurate answer from the top search results. If the results are ambiguous or contradictory, leave this field empty.

## Implementation Details

The skill leverages a combination of techniques to access and process the SAP knowledge base, including:

1.  **Web Search with Targeted Queries:** Uses a search engine (e.g., Google, DuckDuckGo) to search specifically within the SAP domains (`help.sap.com`, `support.sap.com`, `community.sap.com`) using targeted keywords and search operators (e.g., `site:help.sap.com "purchase order"`, `site:support.sap.com "SAP Note"`, `site:community.sap.com "S/4HANA migration"`).
2.  **SAP Note Lookup:** Directly queries the SAP Support Portal for relevant SAP Notes based on keywords and error messages.  This requires access to the SAP Support Portal via API or scraping (with appropriate rate limiting).
3.  **SAP Community API:** Utilizes the SAP Community API (if available) to search for forum posts, blogs, and wiki pages related to the user's query.
4.  **Document Parsing:** Parses the HTML content of the retrieved web pages and SAP Notes to extract relevant information, including text, code examples, and configuration steps.  Utilize libraries such as BeautifulSoup (Python) or Jsoup (Java) for robust HTML parsing.
5.  **Text Summarization (Optional):** Employs a text summarization model (e.g., BART, T5) to generate a concise summary of the key information from the search results. This step is optional and should only be performed if the results are highly relevant and the summary can be generated accurately.
6.  **Result Ranking:** Ranks the search results based on relevance, using a combination of factors such as keyword matching, domain authority, and user engagement (e.g., number of views, comments).

## Code Examples

**Python Example (Conceptual):**

```python
import requests
from bs4 import BeautifulSoup
import json

def search_sap_knowledge_base(query):
    """
    Searches the SAP knowledge base using web search and SAP Note lookup.
    """

    # 1. Web Search (Example using Google)
    search_query = f'site:help.sap.com OR site:support.sap.com OR site:community.sap.com "{query}"'
    search_url = f"https://www.google.com/search?q={search_query}"  # Replace with appropriate search API

    try:
        response = requests.get(search_url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, "html.parser")
        search_results = []
        for g in soup.find_all('div', class_='g'): #Adapt based on your search engine's HTML
            anchors = g.find_all('a')
            if anchors:
                link = anchors[0]['href']
                title = g.find('h3').text if g.find('h3') else "No Title"
                snippet = g.find('div', {'class':'VwiC3b'}).text if g.find('div', {'class':'VwiC3b'}) else "No Snippet"
                search_results.append({"title": title, "url": link, "snippet": snippet})
    except requests.exceptions.RequestException as e:
        print(f"Error during web search: {e}")
        search_results = []

    # 2. SAP Note Lookup (Conceptual - Requires SAP Support Portal Access)
    #   - Implement logic to authenticate and query the SAP Support Portal API
    #   - Example:  SAP Note API endpoint: https://support.sap.com/en/my-support/knowledge-base.html (replace with actual API endpoint if available)
    #   - Parse the response and extract relevant information (title, URL, snippet)
    sap_note_results = [] # Placeholder for SAP Note results

    # 3. Combine and Rank Results
    all_results = search_results + sap_note_results
    # Implement logic to rank the results based on relevance (e.g., keyword matching, domain authority)
    ranked_results = all_results  # Placeholder for ranked results

    # 4. Generate Summary (Optional)
    summary = ""
    # Implement logic to generate a summary from the top-ranked results using a text summarization model.

    return json.dumps({"results": ranked_results, "summary": summary})

# Example usage:
query = "How to configure FIORI launchpad"
result = search_sap_knowledge_base(query)
print(result)

```

**Important Considerations:**

*   **Authentication:** Accessing the SAP Support Portal and SAP Community API (if available) may require authentication. Implement appropriate authentication mechanisms to ensure authorized access.
*   **Rate Limiting:** Be mindful of rate limits imposed by the search engines and SAP APIs. Implement appropriate delays and error handling to avoid being blocked.
*   **Error Handling:** Implement robust error handling to gracefully handle exceptions such as network errors, API errors, and parsing errors.
*   **HTML Structure Changes:** The HTML structure of the SAP websites may change over time. Monitor for changes and update the parsing logic accordingly.
*   **Security:** Sanitize user input to prevent injection attacks. Be cautious when handling sensitive data such as SAP credentials.
*   **Licensing:** Respect the licensing terms of the SAP documentation and APIs.

## Best Practices

*   **Prioritize Official SAP Documentation:** When possible, prioritize results from `help.sap.com` and `support.sap.com` over community-generated content.
*   **Focus on Specific Information:** Encourage users to provide specific and detailed queries to improve the accuracy of the search results.
*   **Verify Information:** Always verify the information retrieved from the SAP knowledge base against the user's specific SAP system and configuration. SAP documentation often covers multiple versions and configurations.
*   **Provide Context:** When presenting search results, provide context by including relevant snippets and explanations.
*   **Avoid Hallucination:** Refrain from generating answers or opinions if the search results are ambiguous or contradictory. Instead, present the relevant search results and encourage the user to consult the official SAP documentation.
*   **Regularly Update the Skill:** The SAP knowledge base is constantly evolving. Regularly update the skill to incorporate new information and changes to the SAP websites and APIs.

## Edge Cases

*   **Vague Queries:** Handle vague queries by providing a list of potential topics and asking the user to clarify their request. For example, if the user asks "How do I use SAP?", the skill could respond with a list of common SAP modules and functionalities, asking the user to specify which one they are interested in.
*   **Non-English Queries:** While SAP documentation is available in multiple languages, the skill should primarily focus on English content for now. Future enhancements could include multilingual support.  When a non-English query is received, translate to English, then proceed.
*   **Outdated Information:** The SAP knowledge base may contain outdated information. Clearly indicate the publication date of the search results and warn the user to verify the information against their specific SAP system version.
*   **Missing Documentation:** In rare cases, documentation may be missing for certain SAP functionalities.  In such instances, suggest the user consult the SAP Community forums or contact SAP Support directly.
*   **Custom Development:** The SAP knowledge base primarily covers standard SAP functionalities. For questions related to custom ABAP code or configurations, suggest the user consult their internal SAP development team.

## Troubleshooting

*   **No Search Results:** If no search results are found, try broadening the search query or using alternative keywords.
*   **Irrelevant Search Results:** If the search results are irrelevant, refine the search query to be more specific.
*   **API Errors:** If API errors occur, check the SAP Support Portal and SAP Community API documentation for troubleshooting tips.
*   **Parsing Errors:** If parsing errors occur, inspect the HTML content of the SAP websites and update the parsing logic accordingly.

By following these guidelines and best practices, the `sap-knowledge-base` skill can be effectively used to answer user questions about SAP systems and provide access to valuable SAP documentation.
```
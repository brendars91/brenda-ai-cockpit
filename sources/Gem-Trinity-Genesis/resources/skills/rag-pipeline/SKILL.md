```markdown
---
name: rag-pipeline
description: Implements a Retrieval-Augmented Generation (RAG) pipeline to answer user queries using a given knowledge base. This skill retrieves relevant information from a knowledge base, combines it with the user query, and generates a comprehensive and informative answer. Use this skill when the user needs information that resides within a document store or knowledge base and when they need it presented in a coherent, natural language format.
license: Complete terms in LICENSE.txt
---

# RAG Pipeline Skill

This skill implements a Retrieval-Augmented Generation (RAG) pipeline. It allows the agent to answer user queries by retrieving relevant information from a knowledge base and generating an answer based on both the query and the retrieved context.

## Core Functionality

The skill performs the following steps:

1.  **Query Embedding:** Embeds the user's query into a vector space.
2.  **Knowledge Base Retrieval:** Searches the knowledge base for documents that are semantically similar to the query embedding.  This typically involves using a vector database (e.g., ChromaDB, Pinecone) to perform a nearest neighbor search.
3.  **Contextualization:** Combines the retrieved documents with the original user query.  This usually involves creating a prompt that includes both the query and the retrieved context.
4.  **Answer Generation:** Uses a Large Language Model (LLM) to generate an answer based on the combined query and context.
5.  **Response Formatting:** Formats the generated answer for the user, ensuring clarity and coherence.

## Input Parameters

The skill requires the following input parameters:

*   `query` (string): The user's question or request.
*   `knowledge_base` (string, required if vector store URI is not provided): The name of the knowledge base to use for retrieval.  This could refer to a pre-configured knowledge base or trigger another skill to prepare the knowledge base. Alternatively, supply the Vector Store URI (see below).
*   `vector_store_uri` (string, required if knowledge_base name is not provided): The URI for the vector store containing the embedded knowledge base.  This allows direct access to a pre-built vector database without needing to specify the knowledge base name. Examples: `"chromadb:///my_chroma_db"`, `"pinecone://index_name"`.  If both `knowledge_base` and `vector_store_uri` are provided, the `vector_store_uri` takes precedence.
*   `top_k` (integer, optional, default=4): The number of documents to retrieve from the knowledge base.  Increasing `top_k` can improve answer accuracy but also increase latency and cost.
*   `llm_model` (string, optional, default="gpt-3.5-turbo"): The name of the Large Language Model (LLM) to use for answer generation.  Examples: `"gpt-4"`, `"claude-v1.3"`.
*   `prompt_template` (string, optional): A custom prompt template to use for combining the query and retrieved context.  If not provided, a default template will be used (see "Default Prompt Template" section below).
*   `return_source_documents` (boolean, optional, default=False):  Whether to return the source documents used to generate the answer.  If set to `True`, the response will include the text content of the retrieved documents.
*   `metadata_filters` (dict, optional): A dictionary of metadata filters to apply to the knowledge base retrieval process.  This allows for more precise filtering of documents based on metadata fields (e.g., `{"category": "technical", "author": "John Doe"}`).
*   `search_type` (string, optional, default="similarity"): The type of search to perform on the vector database. Options include "similarity" (default), "mmr" (Maximal Marginal Relevance). MMR aims to maximize diversity among retrieved documents.
*   `mmr_k` (int, optional): The number of documents to pass into MMR algorithm to select top_k documents from. Only applicable when search_type is "mmr".  If not provided when search_type is "mmr", a reasonable default will be used (typically 10).
*   `chain_type` (string, optional, default="stuff"): The type of document combining chain to use. Options include "stuff", "map_reduce", "refine", "map_rerank". 'stuff' is simplest but limited by context size. 'map_reduce' is good for very long documents but can lose context. 'refine' iteratively refines the answer. 'map_rerank' reranks documents based on their relevance to the query and each other.
*   `max_tokens_limit` (int, optional): Maximum token limit for the LLM. If using 'stuff' chain, be sure to include enough margin for the model to respond. Defaults to LLM provider's defaults, or can be adjusted to fit budget and latency requirements.

## Output Parameters

The skill returns the following output parameters:

*   `answer` (string): The generated answer to the user's query.
*   `source_documents` (list of strings, optional): A list of the source documents used to generate the answer.  This is only returned if `return_source_documents` is set to `True`. Each string represents the text content of a source document.
*   `debug_info` (dict, optional): A dictionary containing debugging information, such as the retrieved documents, the generated prompt, and the LLM's raw output.  This can be useful for troubleshooting and improving the RAG pipeline.

## Default Prompt Template

The skill uses the following default prompt template:

```
Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Helpful Answer:
```

You can customize this template by providing your own `prompt_template` parameter.  The template must include placeholders for `{context}` and `{question}`.

## Error Handling

The skill handles the following error conditions:

*   **Knowledge Base Not Found:** If the specified `knowledge_base` does not exist, the skill will return an error message.
*   **Vector Store Connection Error:** If the skill cannot connect to the vector store specified by `vector_store_uri`, it will return an error message.
*   **LLM API Error:** If the LLM API returns an error, the skill will return an error message.
*   **Invalid Input Parameters:** If the skill receives invalid input parameters (e.g., invalid `top_k` value), it will return an error message.

## Code Examples

Here are some code examples showing how to use the `rag-pipeline` skill:

**Example 1: Simple Query**

```json
{
  "skill": "rag-pipeline",
  "input": {
    "query": "What are the main benefits of using Anthropic's Claude model?",
    "knowledge_base": "anthropic-claude-documentation"
  }
}
```

**Example 2: Using a Vector Store URI**

```json
{
  "skill": "rag-pipeline",
  "input": {
    "query": "What are the main benefits of using Anthropic's Claude model?",
    "vector_store_uri": "chromadb:///my_anthropic_kb"
  }
}
```

**Example 3: Retrieving More Documents**

```json
{
  "skill": "rag-pipeline",
  "input": {
    "query": "What are the main benefits of using Anthropic's Claude model?",
    "knowledge_base": "anthropic-claude-documentation",
    "top_k": 10
  }
}
```

**Example 4: Using a Custom Prompt Template**

```json
{
  "skill": "rag-pipeline",
  "input": {
    "query": "What are the main benefits of using Anthropic's Claude model?",
    "knowledge_base": "anthropic-claude-documentation",
    "prompt_template": "Based on the following documentation snippets, answer the question: {question}\n\n{context}\n\nAnswer:"
  }
}
```

**Example 5: Using Metadata Filters**

```json
{
  "skill": "rag-pipeline",
  "input": {
    "query": "What is the recommended way to deploy a new version of the application?",
    "knowledge_base": "deployment-documentation",
    "metadata_filters": {"environment": "production"}
  }
}
```

**Example 6: Retrieving Source Documents**

```json
{
  "skill": "rag-pipeline",
  "input": {
    "query": "What is the capital of France?",
    "knowledge_base": "world-facts",
    "return_source_documents": true
  }
}
```

**Example 7: Using MMR Search Type**

```json
{
  "skill": "rag-pipeline",
  "input": {
    "query": "Tell me about machine learning algorithms.",
    "knowledge_base": "ml-knowledge-base",
    "search_type": "mmr",
    "top_k": 5,
    "mmr_k": 10
  }
}
```

**Example 8: Using Map Reduce Chain Type**

```json
{
  "skill": "rag-pipeline",
  "input": {
    "query": "Summarize the key points of this very long document.",
    "knowledge_base": "long-document-kb",
    "chain_type": "map_reduce"
  }
}
```

## Best Practices

*   **Choose the Right Knowledge Base:** Select a knowledge base that is relevant to the user's query.  Using an irrelevant knowledge base will result in inaccurate or irrelevant answers.
*   **Optimize `top_k`:** Experiment with different values of `top_k` to find the optimal balance between answer accuracy and latency.
*   **Customize the Prompt Template:** If the default prompt template is not producing satisfactory results, customize it to better suit the specific knowledge base and query type.
*   **Use Metadata Filters:** Use metadata filters to narrow down the search and improve the accuracy of the retrieved documents.
*   **Monitor Performance:** Monitor the performance of the RAG pipeline (e.g., latency, accuracy) and make adjustments as needed.
*   **Implement Error Handling:** Implement robust error handling to gracefully handle any errors that may occur during the RAG pipeline execution.
*   **Context Window Awareness**: Be mindful of the LLM's context window size. When using the "stuff" chain_type, ensure that the combined length of the query and retrieved documents does not exceed the model's limit. Consider using "map_reduce" or "refine" for larger contexts.
*   **Experiment with `search_type`**: "similarity" is a good default, but "mmr" can be helpful when the knowledge base contains redundant information.
*   **Reranking**: Consider implementing a separate reranking step (e.g., using a cross-encoder model) after the initial retrieval to further improve the quality of the retrieved documents, especially when dealing with noisy or heterogeneous knowledge bases. This step is typically external to the RAG pipeline skill itself but can significantly improve performance.

## Security Considerations

*   **Access Control:** Ensure that access to the knowledge base and vector store is properly controlled to prevent unauthorized access to sensitive information.
*   **Input Validation:** Validate all input parameters to prevent injection attacks and other security vulnerabilities.
*   **Data Sanitization:** Sanitize the retrieved documents to remove any potentially malicious code or scripts.
*   **Rate Limiting:** Implement rate limiting to prevent abuse of the LLM API and other resources.

## Dependencies

This skill depends on the following:

*   A vector database (e.g., ChromaDB, Pinecone).
*   A Large Language Model (LLM) API (e.g., OpenAI, Anthropic).
*   The Langchain library

## Integration with SAP_Dev_Tutor_Agent

This `rag-pipeline` skill integrates seamlessly with the `SAP_Dev_Tutor_Agent` by providing a mechanism to access and leverage SAP-related knowledge. The agent can use this skill to answer user questions about SAP development, configuration, and best practices by querying a dedicated SAP knowledge base. The `sap-knowledge-base` skill (as defined in the project context) can be used to manage and update the SAP knowledge base used by this RAG pipeline. This ensures that the agent has access to the latest information and can provide accurate and relevant answers to SAP-related queries. By combining these two skills, the `SAP_Dev_Tutor_Agent` becomes a powerful tool for SAP developers and administrators.
```
import os
import boto3
from strands import tool

@tool(name="rag_clause_retrieval")
def rag_clause_retrieval(query: str, policy_id: str = None) -> str:
    """
    Retrieves the most relevant policy clauses from the knowledge base using RAG.

    Core Feature:
        ✅ Pure RAG-based clause retrieval (no summarization, no rewriting)

    Args:
        query: Natural language query requesting a clause, rule, exclusion, or condition.
        policy_id: Optional filter to retrieve clauses belonging to a specific policy.

    Returns:
        A formatted string containing the top retrieved clauses.
    """

    region = os.environ.get("AWS_REGION", "us-east-1")
    kb_id = os.environ.get("POLICY_KNOWLEDGE_BASE_ID") or os.environ.get("KNOWLEDGE_BASE_ID")
    client = boto3.client("bedrock-agent-runtime", region_name=region)

    retrieval_config = {
        "managedSearchConfiguration": {
            "numberOfResults": 5
        }
    }

    # Add optional policy-level filter
    if policy_id:
        retrieval_config["managedSearchConfiguration"]["filter"] = {
            "equals": {"key": "policy_id", "value": policy_id}
        }

    try:
        response = client.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={"text": query},
            retrievalConfiguration=retrieval_config
        )

        results = []
        for r in response.get("retrievalResults", []):
            clause = r.get("content", {}).get("text", "")
            doc_id = r.get("document", {}).get("id", "UnknownDoc")
            score = r.get("score", None)

            if clause:
                results.append(
                    f"📄 **Document:** {doc_id}\n"
                    f"🔍 **Score:** {score}\n"
                    f"📝 **Clause:**\n{clause}"
                )

        return "\n\n---\n\n".join(results) if results else "No matching clauses found."

    except Exception as e:
        return f"Error during clause retrieval: {str(e)}"

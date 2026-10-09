import os
import boto3
from strands import tool

@tool(name="vehicle_insurance_recommendation")
def vehicle_insurance_recommendation(query: str, customer_id: str) -> str:
    """
    Handles vehicle-related insurance queries using the unstructured knowledge base.
    
    This tool retrieves relevant insurance documents, policies, add-ons, and 
    recommendations from the knowledge base for a given customer or vehicle context.
    
    Args:
        query: A question about vehicle insurance, policies, add-ons, or recommendations.
        customer_id: Customer or vehicle identifier to filter relevant documents.
    
    Returns:
        A formatted string response with recommendations or relevant information
        from the knowledge base.
    """
    
    region = os.environ.get("AWS_REGION", "us-east-1")
    kb_id = os.environ.get("KNOWLEDGE_BASE_ID")
    bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=region)
    
    try:
        retrieve_response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=kb_id,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "managedSearchConfiguration": {
                    "numberOfResults": 5
                }
            }
        )
        
        # Format the response for better readability
        results = []
        for result in retrieve_response.get('retrievalResults', []):
            content = result.get('content', {}).get('text', '')
            if content:
                results.append(content)
        
        return "\n\n".join(results) if results else "No relevant information found."
    
    except Exception as e:
        return f"Error in vehicle insurance assistant: {str(e)}"
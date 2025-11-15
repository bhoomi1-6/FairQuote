import logging
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from strands import Agent
from strands.multiagent import Swarm

# Load environment variables
load_dotenv()

from src.config.init_model import bedrock_model

# Configure logging
logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the underwriting agentic service.
    Orchestrates the multi-agent workflow for insurance underwriting.
    """
    
    logger.info("Starting underwriting agentic service...")
    
    # Create specialized agents
    intake_agent = Agent(
        name="intake_agent",
        system_prompt="You are the Intelligent Intake Agent. Drive a natural conversation to collect all required driver and vehicle details. Detect inconsistencies. Use DVLA tool for vehicle data lookup. Extract data from uploaded documents via OCR. Once data collection is complete and validated, output a structured JSON of user profile."
    )
    
    pricing_agent = Agent(
        name="pricing_agent",
        system_prompt="You are the Pricing Agent. Compute risk score via risk_model tool. Calculate premium via premium_calculator tool. Retrieve risk reasoning from RAG tool to fetch risk snippets. Generate personalized recommendations. Produce a structured output with premium, risk_score, explanation, breakdown, and recommendations."
    )
    
    policy_agent = Agent(
        name="policy_generator",
        system_prompt="You are the Policy Agent. Use RAG to fetch relevant policy clauses. Assemble a complete insurance policy document. Use LLM to generate plain-English summaries. Maintain structure with Definitions, Coverage, Exclusions, Limits, and Conditions. Output PDF-ready markdown."
    )
    
    # Create the swarm with all agents
    swarm = Swarm(
        agents=[intake_agent, pricing_agent, policy_agent],
        entry_point=intake_agent,  # Start with intake
        max_handoffs=20,
        max_iterations=20,
        execution_timeout=900.0,  # 15 minutes
        node_timeout=300.0,       # 5 minutes per agent
        repetitive_handoff_detection_window=8,
        repetitive_handoff_min_unique_agents=3
    )
    
    logger.info("Swarm created successfully")
    
    # Define the task
    task = "Collect vehicle and driver info, compute insurance premium, and generate a policy document with recommendations."
    logger.info(f"Executing task: {task}")
    
    # Execute the swarm
    result = swarm(task)
    
    # Display results
    logger.info("=" * 80)
    logger.info("EXECUTION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Status: {result.status}")
    logger.info(f"Node history: {[node.node_id for node in result.node_history]}")
    logger.info(f"Final output:\n{result}")
    
    return result


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running service: {e}", exc_info=True)
        sys.exit(1)

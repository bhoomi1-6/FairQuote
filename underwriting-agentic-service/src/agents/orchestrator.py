import logging
from strands import Agent
from strands.multiagent import Swarm
from src.config import bedrock_model
from src.agents import IntakeAgent, PricingAgent, PolicyAgent

# ------------------------
# Logging setup
# ------------------------
logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)



# ------------------------
# Create the swarm
# ------------------------
swarm = Swarm(
    [IntakeAgent, PricingAgent, PolicyAgent],
    entry_point=IntakeAgent,  # Start with intake
    max_handoffs=20,
    max_iterations=20,
    execution_timeout=900.0,  # 15 minutes
    node_timeout=300.0,       # 5 minutes per agent
    repetitive_handoff_detection_window=8,
    repetitive_handoff_min_unique_agents=3
)

# ------------------------
# Execute the swarm on a task
# ------------------------
task = "Collect vehicle and driver info, compute insurance premium, and generate a policy document with recommendations."
result = swarm(task)

# ------------------------
# Inspect the result
# ------------------------
print(f"Status: {result.status}")
print(f"Node history: {[node.node_id for node in result.node_history]}")
print(f"Final output: {result}")

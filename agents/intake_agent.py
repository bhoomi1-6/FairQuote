from strands import Agent, tool, message

class IntakeAgent(Agent):

    name = "intake_agent"
    description = "Conversational front door: collects user data, validates, enriches via tools"

    tools = ["ocr_tool", "dvla_lookup", "validation_tool"]

    instructions = """
    You are the Intelligent Intake Agent.
    Objectives:
    - Drive a natural conversation to collect all required driver + vehicle details.
    - Detect inconsistencies.
    - Use DVLA tool for vehicle data lookup.
    - Extract data from uploaded documents via OCR.
    - Once data collection is complete and validated, output a structured JSON of user profile.

    Rules:
    - Use function calling whenever data is requested from tools.
    - Ask only 1 question at a time.
    - When input is complete, emit event: `intake.completed`.
    """

    @message(trigger="intake.completed")
    def send_payload(self, intake_data):
        self.emit("pricing.requested", intake_data)

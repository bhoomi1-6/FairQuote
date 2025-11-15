from strands import tool

@tool(name="dvla_lookup")
def dvla_lookup(registration: str):
    """
    Returns mock DVLA vehicle data from dvla_mock.json.
    """

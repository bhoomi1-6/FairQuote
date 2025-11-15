from strands import tool

@tool(name="ocr_tool")
def ocr_tool(image_bytes: bytes):
    """
    Extracts text from driving license or ID.
    Returns JSON of extracted fields.
    """

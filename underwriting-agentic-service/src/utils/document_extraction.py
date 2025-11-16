
import requests

import os

headers = {
    'Authorization': 'Bearer ' + os.getenv("LANDING_AI_API_KEY"),
}
url = 'https://api.va.landing.ai/v1/ade/parse'

# Set the model (optional)
data = {
    'model': 'dpt-2-latest'
}
async def extract_document(uploaded_file) -> dict:
    """
    Extracts text from user documents.
    Returns JSON of extracted fields.
    """
    # Streamlit uploaded_file is already a file-like object
    files = {'document': uploaded_file}

    response = requests.post(url, files=files, data=data, headers=headers)
    return response.json()  


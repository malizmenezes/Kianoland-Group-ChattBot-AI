from google.cloud import dialogflow
import os
from dotenv import load_dotenv

load_dotenv()

def detect_intent(text, project_id=None, session_id="default", language_code="id"):
    project_id = project_id or os.getenv("DIALOGFLOW_PROJECT_ID")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result.fulfillment_text

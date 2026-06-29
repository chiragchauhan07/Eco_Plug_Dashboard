from google import genai
from google.genai import types

try:
    client = genai.Client(api_key="dummy")
    contents = [
        types.Content(role="user", parts=[types.Part.from_text(text="Hi")])
    ]
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents
    )
except Exception as e:
    import traceback
    traceback.print_exc()

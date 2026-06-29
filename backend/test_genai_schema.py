from google.genai import types
import pydantic

class X(pydantic.BaseModel):
    name: str

try:
    config = types.GenerateContentConfig(response_schema=X)
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()

import os

from google.adk.models.lite_llm import LiteLlm

llm_model = LiteLlm(
    model=os.getenv("LLM_MODEL"),
    api_base=os.getenv("LLM_API_BASE"),
    api_key=os.getenv("LLM_API_KEY")
)
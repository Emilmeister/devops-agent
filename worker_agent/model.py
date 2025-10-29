from google.adk.models.lite_llm import LiteLlm
from worker_agent.settings import settings

llm_model = LiteLlm(
    model=settings.llm_model,
    api_base=settings.llm_api_base,
    api_key=settings.llm_api_key
)
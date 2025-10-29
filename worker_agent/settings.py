from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_model: str
    llm_api_base: str
    llm_api_key: str
    log_level: str
    db_adk_url: str
    db_a2a_url: str
    agent_name: str
    agent_description: str
    agent_url: str
    agent_version: str
    enable_phoenix: str
    phoenix_project_name: str
    phoenix_endpoint: str
    mcp_url: str
    port: str



settings = Settings()
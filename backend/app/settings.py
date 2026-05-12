from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    config_path: str = "/app/config/demo_data.yaml"

    model_config = {"env_prefix": "DEMO_"}


settings = Settings()

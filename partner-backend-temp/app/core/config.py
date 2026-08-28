from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    database_url: str = Field(..., validation_alias='DATABASE_URL')
    jwt_secret_key: str = Field(..., validation_alias='JWT_SECRET_KEY')
    jwt_algorithm: str = Field('HS256', validation_alias='JWT_ALGORITHM')
    access_token_expire_minutes: int = Field(60, validation_alias='ACCESS_TOKEN_EXPIRE_MINUTES')

    model_config = SettingsConfigDict(env_file='.env', case_sensitive=True, extra='ignore')

settings = Settings()

from pydantic_settings import BaseSettings

# ensure that all these variables exist in the environment.
# if not, populate with default value listed or throw error (if not listed)
# or point to .env file 
class Settings(BaseSettings):
    db_hostname: str
    db_port: str
    db_pw: str
    db_name: str
    db_user: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"

settings = Settings()

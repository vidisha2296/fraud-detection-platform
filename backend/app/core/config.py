# from pydantic_settings import BaseSettings, SettingsConfigDict

# class Settings(BaseSettings):
#     app_name: str = "Fraud Detection Platform"
#     debug: bool = True
#     port: int = 8000

#     # Postgres
#     postgres_user: str = "postgres"
#     postgres_password: str = "postgres"
#     postgres_db: str = "fraud_db"
#     postgres_host: str = "localhost"
#     postgres_port: int = 5432

#     # Redis
#     redis_host: str = "localhost"
#     redis_port: int = 6379
#     redis_db: int = 0

#     # Security
#     api_key: str = "changeme123"

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         extra="allow"  # <--- THIS fixes extra fields error
#     )

# settings = Settings()


# # app/core/config.py
# from pydantic_settings import BaseSettings, SettingsConfigDict
# from pydantic import Field
# class Settings(BaseSettings):
#     # FastAPI / General
#     APP_NAME: str = Field(..., env="APP_NAME")
#     DEBUG: bool
#     PORT: int

#     # Postgres
#     POSTGRES_USER: str
#     POSTGRES_PASSWORD: str
#     POSTGRES_DB: str
#     POSTGRES_HOST: str
#     POSTGRES_PORT: int
#     DATABASE_URL: str

#     # Redis
#     REDIS_HOST: str
#     REDIS_PORT: int
#     REDIS_DB: int
#     REDIS_URL: str

#     # Security
#     API_KEY: str

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         extra="allow"  # allow extra keys in .env
#     )

# settings = Settings()


# from pydantic_settings import BaseSettings
# from pydantic import PostgresDsn, RedisDsn, Field
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn, Field


class Settings(BaseSettings):
    # FastAPI
    app_name: str = Field("Fraud Detection Platform", env="APP_NAME")
    debug: bool = Field(True, env="DEBUG")
    port: int = Field(8000, env="PORT")

    # Postgres
    postgres_user: str = Field(..., env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
    postgres_db: str = Field(..., env="POSTGRES_DB")
    postgres_host: str = Field(..., env="POSTGRES_HOST")
    postgres_port: int = Field(..., env="POSTGRES_PORT")
    database_url: PostgresDsn | None = None

    # Redis
    redis_host: str = Field(..., env="REDIS_HOST")
    redis_port: int = Field(..., env="REDIS_PORT")
    redis_db: int = Field(..., env="REDIS_DB")
    redis_url: RedisDsn | None = None

    # Security
    api_key: str = Field(..., env="API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    def assemble_urls(self):
        self.database_url = (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
        self.redis_url = f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

# Create a settings instance
settings = Settings()
settings.assemble_urls()

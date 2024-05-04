from typing import List, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: Literal["DEV", "TEST", "PROD"]
    LOG_LEVEL: Literal["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]

    API_KEY: str

    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    TEST_DB_HOST: str
    TEST_DB_PORT: str
    TEST_DB_NAME: str
    TEST_DB_USER: str
    TEST_DB_PASS: str

    @property
    def TEST_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"

    PROD_DB_HOST: str
    PROD_DB_PORT: str
    PROD_DB_NAME: str
    PROD_DB_USER: str
    PROD_DB_PASS: str

    @property
    def PROD_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.PROD_DB_USER}:{self.PROD_DB_PASS}@{self.PROD_DB_HOST}:{self.PROD_DB_PORT}/{self.PROD_DB_NAME}"

    SENTRY_DSN: str

    TOKEN_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    PASSWORD_HASH_NAME: str
    PASSWORD_HASH_ITERATIONS: int
    PASSWORD_SALT_SEPARATOR: str

    CORS_ORIGINS: List[str]
    CORS_HEADERS: List[str]
    CORS_METHODS: List[str]
    CORS_CREDENTIALS: bool

    MIN_USERNAME_LENGTH: int
    MAX_USERNAME_LENGTH: int

    MIN_PASSWORD_LENGTH: int
    MAX_PASSWORD_LENGTH: int

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.MODE == "DEV" or self.MODE == "TEST":
            self.SECURE_COOKIE = False
            self.HTTPONLY_COOKIE = False
            self.SAMESITE_COOKIE = "Lax"
        elif self.MODE == "PROD":
            self.SECURE_COOKIE = True
            self.HTTPONLY_COOKIE = True
            self.SAMESITE_COOKIE = "Lax"


settings: Settings = Settings()  # noqa

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str = Field(default="localhost", description="MySQL 데이터베이스 호스트")
    DB_PORT: int = Field(default=3306, description="MySQL 데이터베이스 포트")
    DB_USER: str = Field(default="user", description="MySQL 데이터베이스 사용자")
    DB_PASSWORD: str = Field(
        default="password", description="MySQL 데이터베이스 비밀번호"
    )
    DB_NAME: str = Field(default="wanted_db", description="MySQL 데이터베이스 이름")

    DB_POOL_SIZE: int = Field(default=4, description="데이터베이스 커넥션 풀 크기")
    DB_MAX_OVERFLOW: int = Field(
        default=12, description="데이터베이스 커넥션 풀 최대 오버플로우"
    )
    DB_POOL_TIMEOUT: int = Field(
        default=30, description="데이터베이스 커넥션 풀 타임아웃"
    )

    DEBUG: bool = Field(default=False, description="디버그 모드")
    DEFAULT_LANGUAGE: str = Field(default="ko", description="기본 언어")

    @property
    def base_database_url(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/"

    @property
    def database_url(self) -> str:
        return f"{self.base_database_url}{self.DB_NAME}"

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("+aiomysql", "+mysqldb")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

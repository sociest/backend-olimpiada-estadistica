from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = ""
    db_user: str = ""
    db_password: str = ""
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = ""
    app_env: str = "development"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_bucket_materiales: str = ""
    supabase_bucket_perfiles: str = ""
    port: int = 8000
    cloudflare_secret_key: str = ""
    
    brevo_api_key: str = ""
    brevo_base_url: str = "https://api.brevo.com/v3"
    brevo_sender_name: str = ""
    brevo_sender_email: str = ""
    brevo_reply_to: str = ""
    brevo_enabled: int = 1
    brevo_webhook_secret: str = ""
    
    mailing_batch_size: int = 15
    mailing_interval_minutes: int = 20
    mailing_max_retries: int = 3
    mailing_timeout_seconds: int = 30
    
    scheduler_timezone: str = "America/La_Paz"
    mailing_enabled: int = 1
    scheduler_enabled: int = 1
    temp_cleanup_dir: str = "tmp"
    temp_cleanup_interval_hours: int = 24
    
    first_admin_username: str = ""
    first_admin_email: str = ""
    first_admin_password: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    log_level: str = "DEBUG"
    def get_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

settings = Settings()

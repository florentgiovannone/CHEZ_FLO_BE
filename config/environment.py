import os

# On Railway: use internal DATABASE_URL (fast). Locally with `railway run`: use DATABASE_PUBLIC_URL
# RAILWAY_ENVIRONMENT is only set when running on Railway's infrastructure
if os.getenv("RAILWAY_ENVIRONMENT"):
    db_URI = os.getenv("DATABASE_URL", "postgresql://localhost:5432/log_db")
else:
    db_URI = os.getenv("DATABASE_PUBLIC_URL") or os.getenv(
        "DATABASE_URL", "postgresql://localhost:5432/log_db"
    )

SECRET = os.getenv("SECRET", "t3cbPSmNgXn-bZ0wGxR8n0fpMC0")

if db_URI and db_URI.startswith("postgres://"):
    db_URI = db_URI.replace("postgres://", "postgresql://", 1)

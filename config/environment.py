import os

db_URI = os.getenv("DATABASE_URL", "postgresql://localhost:5432/log_db")
SECRET = os.getenv("SECRET", "t3cbPSmNgXn-bZ0wGxR8n0fpMC0")

if db_URI and db_URI.startswith("postgres://"):
    db_URI = db_URI.replace("postgres://", "postgresql://", 1)

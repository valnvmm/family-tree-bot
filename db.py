import os
import psycopg2
from psycopg2.extras import RealDictCursor

# ---------------------------------------------------------
# Database connection
# ---------------------------------------------------------

def get_db():
    """
    Returns a PostgreSQL connection using Railway environment variables.
    Uses RealDictCursor so rows behave like dicts.
    Automatically logs errors if connection fails.
    """

    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        print("[DB] ERROR: DATABASE_URL environment variable not found.")
        return None

    try:
        conn = psycopg2.connect(
            dbname=os.getenv("PGDATABASE"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            host=os.getenv("PGHOST"),
            port=os.getenv("PGPORT"),
            cursor_factory=RealDictCursor,
            sslmode="require"
        )
        print("[DB] Connected to PostgreSQL successfully.")
        return conn

    except Exception as e:
        print(f"[DB] Connection FAILED: {e}")
        return None


# ---------------------------------------------------------
# Utility query function
# ---------------------------------------------------------

def query(sql, params=None, fetch=False):
    """
    Executes a query on the database.
    `fetch=True` returns rows.
    """

    conn = get_db()
    if conn is None:
        print("[DB] Query aborted because no database connection.")
        return None

    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())

            if fetch:
                result = cur.fetchall()
                conn.commit()
                return result

            conn.commit()
            return True

    except Exception as e:
        print(f"[DB] Query ERROR: {e}")
        return None

    finally:
        conn.close()

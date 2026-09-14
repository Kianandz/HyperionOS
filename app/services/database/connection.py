import pymysql
import psycopg2
import pymssql


def test_db_connection(
    db_type: str, host: str, port: int, user: str, password: str, database: str = ""
):
    try:
        if db_type == "mysql":
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database if database else None,
                connect_timeout=5,
            )
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES;")
            databases = [row[0] for row in cursor.fetchall()]
            conn.close()

        elif db_type == "postgres":
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=database if database else "postgres",
                connect_timeout=5,
            )
            cursor = conn.cursor()
            cursor.execute(
                "SELECT datname FROM pg_database WHERE datistemplate = false;"
            )
            databases = [row[0] for row in cursor.fetchall()]
            conn.close()

        elif db_type == "mssql":
            conn = pymssql.connect(
                server=host,
                port=port,
                user=user,
                password=password,
                database=database if database else "master",
                login_timeout=5,
            )
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sys.databases;")
            databases = [row[0] for row in cursor.fetchall()]
            conn.close()

        else:
            return {"status": "error", "message": "Database type not supported!"}

        return {
            "status": "success",
            "message": f"Connected to {db_type.upper()} server!",
            "databases": databases,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

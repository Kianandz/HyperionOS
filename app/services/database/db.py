import pymysql


def get_database_structure(
    db_type: str, host: str, port: int, user: str, password: str, database: str
):
    try:
        conn = pymysql.connect(
            host=host, port=port, user=user, password=password, database=database
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLE STATUS;")
        tables = [
            {
                "name": row[0],
                "engine": row[1],
                "rows": row[4],
                "size_kb": round((row[6] or 0) / 1024, 2),
            }
            for row in cursor.fetchall()
        ]
        conn.close()
        return {"status": "success", "tables": tables}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_all_databases(db_type: str, host: str, port: int, user: str, password: str):
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password)
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES;")

        system_dbs = ("information_schema", "performance_schema", "mysql", "sys")
        databases = [row[0] for row in cursor.fetchall() if row[0] not in system_dbs]

        conn.close()
        return {"status": "success", "databases": databases}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def create_database(
    db_type: str, host: str, port: int, user: str, password: str, db_name: str
):
    try:
        conn = pymysql.connect(
            host=host, port=port, user=user, password=password, autocommit=True
        )
        cursor = conn.cursor()
        safe_db = db_name.replace("`", "")
        cursor.execute(f"CREATE DATABASE `{safe_db}`;")
        conn.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

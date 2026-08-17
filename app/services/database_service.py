import pymysql
import psycopg2
import pymssql

def test_db_connection(db_type: str, host: str, port: int, user: str, password: str, database: str = ""):

    """Testing koneksi ke Database Remote."""

    try:

        if db_type == "mysql":

            conn = pymysql.connect(

                host=host, port=port, user=user, password=password,

                database=database if database else None, connect_timeout=5

            )

            cursor = conn.cursor()

            cursor.execute("SHOW DATABASES;")

            databases = [row[0] for row in cursor.fetchall()]

            conn.close()


        elif db_type == "postgres":

            conn = psycopg2.connect(

                host=host, port=port, user=user, password=password,

                dbname=database if database else "postgres", connect_timeout=5

            )

            cursor = conn.cursor()

            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")

            databases = [row[0] for row in cursor.fetchall()]

            conn.close()

        elif db_type == "mssql":

            conn = pymssql.connect(

                server=host, port=port, user=user, password=password,

                database=database if database else "master", login_timeout=5

            )
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sys.databases;")

            databases = [row[0] for row in cursor.fetchall()]

            conn.close()

        else:

            return {"status": "error", "message": "Database type tidak didukung"}

        return {

            "status": "success",

            "message": f"Berhasil terkoneksi ke {db_type.upper()} server!",

            "databases": databases

        }

    except Exception as e:

        return {"status": "error", "message": str(e)}
    

def execute_custom_query(db_type: str, host: str, port: int, user: str, password: str, database: str, query: str):

    """Eksekusi query SQL dinamis (SELECT, INSERT, UPDATE, DELETE, CREATE, DLL)."""

    conn = None

    try:

        if db_type == "mysql":

            conn = pymysql.connect(

                host=host, port=port, user=user, password=password,

                database=database, connect_timeout=5, autocommit=True

            )

            cursor = conn.cursor(pymysql.cursors.DictCursor)

        elif db_type == "postgres":

            conn = psycopg2.connect(

                host=host, port=port, user=user, password=password,

                dbname=database, connect_timeout=5

            )

            conn.autocommit = True

            cursor = conn.cursor()

        elif db_type == "mssql":

            conn = pymssql.connect(

                server=host, port=port, user=user, password=password,

                database=database, login_timeout=5, as_dict=True

            )
            cursor = conn.cursor()

        else:

            return {"status": "error", "message": "Database type tidak didukung"}
        
        cursor.execute(query)

        if cursor.description:

            if db_type == "postgres":

                columns = [desc[0] for desc in cursor.description]

                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

            else:

                rows = cursor.fetchall()
            
            conn.close()

            return {

                "status": "success",

                "type": "select",

                "columns": [desc[0] for desc in cursor.description],
                
                "data": rows,

                "row_count": len(rows)

            }
        
        else:

            affected_rows = cursor.rowcount

            conn.close()

            return {

                "status": "success",

                "type": "mutation",

                "message": f"Query berhasil dieksekusi! ({affected_rows} baris terpengaruh)",

                "affected_rows": affected_rows

            }

    except Exception as e:

        if conn:

            conn.close()
            
        return {"status": "error", "message": str(e)}
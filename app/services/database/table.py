import pymysql
import json


def get_table_structure(
    db_type: str,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    table: str,
):
    try:
        conn = pymysql.connect(
            host=host, port=port, user=user, password=password, database=database
        )
        cursor = conn.cursor()
        cursor.execute(f"SHOW FULL COLUMNS FROM `{table}`;")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        return {"status": "success", "columns": columns, "rows": rows}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def create_table(
    db_type: str,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    table_name: str,
    columns_json: str,
):
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            autocommit=True,
        )
        cursor = conn.cursor()
        safe_tbl = table_name.replace("`", "")

        cols = json.loads(columns_json)
        col_defs = []
        pk_col = None

        for col in cols:
            name = col["name"].replace("`", "")
            ctype = col["type"].upper()
            length = col.get("length", "").strip()
            is_ai = col.get("ai", False)
            is_pk = col.get("pk", False)

            if ctype == "VARCHAR" and not length:
                length = "255"

            cdef = f"`{name}` {ctype}"
            if length:
                cdef += f"({length})"
            if is_ai:
                cdef += " AUTO_INCREMENT"
            if is_pk:
                pk_col = name

            col_defs.append(cdef)

        if pk_col:
            col_defs.append(f"PRIMARY KEY (`{pk_col}`)")

        query = f"CREATE TABLE `{safe_tbl}` ({', '.join(col_defs)});"
        cursor.execute(query)
        conn.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def add_table_column(
    db_type: str,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    table: str,
    col_data: dict,
):
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            autocommit=True,
        )
        cursor = conn.cursor()

        name = col_data["name"].replace("`", "")
        ctype = col_data["type"].upper()
        length = col_data.get("length", "").strip()
        is_ai = col_data.get("ai", False)

        if ctype == "VARCHAR" and not length:
            length = "255"

        cdef = f"`{name}` {ctype}"
        if length:
            cdef += f"({length})"
        if is_ai:
            cdef += " AUTO_INCREMENT"

        query = f"ALTER TABLE `{table}` ADD COLUMN {cdef};"
        cursor.execute(query)
        conn.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def execute_batch_structure_action(
    db_type: str,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    table: str,
    action: str,
    columns: list,
):
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            autocommit=True,
        )
        cursor = conn.cursor()

        if action == "delete":
            drop_clauses = ", ".join([f"DROP COLUMN `{col}`" for col in columns])
            query = f"ALTER TABLE `{table}` {drop_clauses};"
            cursor.execute(query)

        elif action == "duplicate":
            cols_placeholder = ",".join([f"'{col}'" for col in columns])
            cursor.execute(
                f"SHOW FULL COLUMNS FROM `{table}` WHERE Field IN ({cols_placeholder})"
            )
            col_defs = cursor.fetchall()

            add_clauses = []
            for row in col_defs:
                col_name = row[0]
                col_type = row[1]
                col_null = "NULL" if row[3] == "YES" else "NOT NULL"
                col_default = f"DEFAULT '{row[4]}'" if row[4] is not None else ""
                col_extra = row[6]

                if "auto_increment" in col_extra.lower():
                    col_extra = col_extra.lower().replace("auto_increment", "")

                new_col_name = f"{col_name}_copy"
                add_clauses.append(
                    f"ADD COLUMN `{new_col_name}` {col_type} {col_null} {col_default} {col_extra}"
                )

            query = f"ALTER TABLE `{table}` {', '.join(add_clauses)};"
            cursor.execute(query)

        conn.close()
        return {"status": "success", "affected_columns": len(columns)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def drop_table(
    db_type: str,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    table: str,
):
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            autocommit=True,
        )
        cursor = conn.cursor()

        safe_tbl = table.replace("`", "")
        cursor.execute(f"DROP TABLE `{safe_tbl}`;")
        conn.close()

        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

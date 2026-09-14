import pymysql


def execute_batch_action(
    db_type: str,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    table: str,
    action: str,
    primary_key: str,
    row_ids: list,
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

        ids_placeholder = ",".join([f"'{rid}'" for rid in row_ids])

        if action == "delete":
            query = (
                f"DELETE FROM `{table}` WHERE `{primary_key}` IN ({ids_placeholder});"
            )
            cursor.execute(query)
        elif action == "duplicate":
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            columns = [row[0] for row in cursor.fetchall()]

            if primary_key in columns:
                columns.remove(primary_key)

            cols_str = ", ".join([f"`{col}`" for col in columns])

            query = f"INSERT INTO `{table}` ({cols_str}) SELECT {cols_str} FROM `{table}` WHERE `{primary_key}` IN ({ids_placeholder});"
            cursor.execute(query)

        affected = cursor.rowcount
        conn.close()
        return {"status": "success", "affected_rows": affected}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def update_row(
    db_type: str,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    table: str,
    primary_key: str,
    pk_value: str,
    update_data: dict,
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

        set_clause = ", ".join([f"`{k}` = %s" for k in update_data.keys()])
        values = list(update_data.values())
        values.append(pk_value)

        query = f"UPDATE `{table}` SET {set_clause} WHERE `{primary_key}` = %s;"
        cursor.execute(query, values)
        affected = cursor.rowcount
        conn.close()
        return {"status": "success", "affected_rows": affected}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def insert_row(
    db_type: str,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    table: str,
    insert_data: dict,
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

        cols = ", ".join([f"`{k}`" for k in insert_data.keys()])
        placeholders = ", ".join(["%s"] * len(insert_data))
        values = list(insert_data.values())

        query = f"INSERT INTO `{table}` ({cols}) VALUES ({placeholders});"
        cursor.execute(query, values)
        affected = cursor.rowcount
        conn.close()

        return {"status": "success", "affected_rows": affected}
    except Exception as e:
        return {"status": "error", "message": str(e)}

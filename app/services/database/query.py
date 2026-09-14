import pymysql
import datetime
import decimal


def execute_raw_sql(
    db_type: str,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    query: str,
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
        cursor.execute(query)

        if cursor.description:
            columns = [desc[0] for desc in cursor.description]

            raw_rows = cursor.fetchall()
            rows = []
            for row in raw_rows:
                new_row = []
                for cell in row:
                    if isinstance(
                        cell,
                        (
                            datetime.datetime,
                            datetime.date,
                            datetime.timedelta,
                            decimal.Decimal,
                        ),
                    ):
                        new_row.append(str(cell))
                    else:
                        new_row.append(cell)
                rows.append(new_row)

            conn.close()
            return {"status": "success", "columns": columns, "rows": rows}

        affected = cursor.rowcount
        conn.close()
        return {"status": "success", "affected_rows": affected}

    except Exception as e:
        return {"status": "error", "message": str(e)}

import subprocess
import shutil
import pymysql
import psycopg2
import pymssql
import datetime
import json
import decimal

def test_db_connection(db_type: str, host: str, port: int, user: str, password: str, database: str = ""):
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
            return {"status": "error", "message": "Database type not supported!"}

        return {
            "status": "success",
            "message": f"Connected to {db_type.upper()} server!",
            "databases": databases
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def execute_raw_sql(db_type: str, host: str, port: int, user: str, password: str, database: str, query: str):
    try:
        conn = pymysql.connect(
            host=host, port=port, user=user, password=password, 
            database=database, autocommit=True
        )
        cursor = conn.cursor()
        cursor.execute(query)

        # Jika query menghasilkan data (SELECT, SHOW, EXPLAIN)
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch data dan konversi datetime/date jadi string biar Jinja tojson ga nangis
            raw_rows = cursor.fetchall()
            rows = []
            for row in raw_rows:
                new_row = []
                for cell in row:
                    if isinstance(cell, (datetime.datetime, datetime.date, datetime.timedelta, decimal.Decimal)):
                        new_row.append(str(cell))
                    else:
                        new_row.append(cell)
                rows.append(new_row)
                
            conn.close()
            return {"status": "success", "columns": columns, "rows": rows}
        
        # Jika query aksi (INSERT, UPDATE, DELETE, ALTER)
        affected = cursor.rowcount
        conn.close()
        return {"status": "success", "affected_rows": affected}

    except Exception as e:
        return {"status": "error", "message": str(e)}

def check_mysql_installed() -> bool:
    """Mengecek apakah service/binary MySQL ada di server lokal"""
    return shutil.which("mysql") is not None or shutil.which("mysqld") is not None

def install_local_mysql():
    """Menginstall MySQL server di OS Linux lokal (Debian/Ubuntu atau Arch)"""
    try:
        # Detect Package Manager
        if shutil.which("apt"):
            pkg_mgr = "debian"
        elif shutil.which("pacman"):
            pkg_mgr = "arch"
        else:
            return {"status": "error", "message": "OS kagak didukung! Cuma bisa Debian/Ubuntu atau Arch."}

        # Eksekusi sesuai OS
        if pkg_mgr == "debian":
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "mysql-server"], check=True)
            service_name = "mysql"
        elif pkg_mgr == "arch":
            # Di Arch biasanya pake MariaDB (drop-in replacement resmi MySQL)
            subprocess.run(["sudo", "pacman", "-Sy", "--noconfirm", "mariadb"], check=True)
            
            # Khusus Arch/MariaDB, wajib inisialisasi datadir dulu kalau baru install
            subprocess.run(["sudo", "mariadb-install-db", "--user=mysql", "--basedir=/usr", "--datadir=/var/lib/mysql"], check=True)
            service_name = "mariadb"

        # Start & Enable Service
        subprocess.run(["sudo", "systemctl", "start", service_name], check=True)
        subprocess.run(["sudo", "systemctl", "enable", service_name], check=True)

        return {"status": "success", "message": f"MySQL/MariaDB berhasil diinstall di {pkg_mgr.capitalize()}!"}

    except Exception as e:
        return {"status": "error", "message": f"Gagal install MySQL: {str(e)}"}

def get_database_structure(db_type: str, host: str, port: int, user: str, password: str, database: str):
    """Mengambil list tabel beserta statistik row count"""
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLE STATUS;")
        tables = [{"name": row[0], "engine": row[1], "rows": row[4], "size_kb": round((row[6] or 0) / 1024, 2)} for row in cursor.fetchall()]
        conn.close()
        return {"status": "success", "tables": tables}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def execute_batch_action(db_type: str, host: str, port: int, user: str, password: str, database: str, table: str, action: str, primary_key: str, row_ids: list):
    """Menangani batch CRUD seperti Delete & Duplicate berdasarkan ID pilihan"""
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, autocommit=True)
        cursor = conn.cursor()
        
        ids_placeholder = ",".join([f"'{rid}'" for rid in row_ids])
        
        if action == "delete":
            query = f"DELETE FROM `{table}` WHERE `{primary_key}` IN ({ids_placeholder});"
            cursor.execute(query)
        elif action == "duplicate":
            # Ambil semua nama kolom di tabel ini
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            columns = [row[0] for row in cursor.fetchall()]
            
            # Buang primary key dari list kolom biar dapet ID baru (Auto Increment)
            if primary_key in columns:
                columns.remove(primary_key)
                
            cols_str = ", ".join([f"`{col}`" for col in columns])
            
            # Insert data tanpa kolom primary key
            query = f"INSERT INTO `{table}` ({cols_str}) SELECT {cols_str} FROM `{table}` WHERE `{primary_key}` IN ({ids_placeholder});"
            cursor.execute(query)
            
        affected = cursor.rowcount
        conn.close()
        return {"status": "success", "affected_rows": affected}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_all_databases(db_type: str, host: str, port: int, user: str, password: str):
    """Mengambil daftar semua database di server MySQL/MariaDB"""
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password)
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES;")
        
        # Filter DB bawaan sistem MySQL
        system_dbs = ('information_schema', 'performance_schema', 'mysql', 'sys')
        databases = [row[0] for row in cursor.fetchall() if row[0] not in system_dbs]
        
        conn.close()
        return {"status": "success", "databases": databases}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def update_row(db_type: str, host: str, port: int, user: str, password: str, database: str, table: str, primary_key: str, pk_value: str, update_data: dict):
    """Update spesifik 1 baris data dinamis"""
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, autocommit=True)
        cursor = conn.cursor()
        
        # Susun SET query dinamis (col1=%s, col2=%s)
        set_clause = ", ".join([f"`{k}` = %s" for k in update_data.keys()])
        values = list(update_data.values())
        values.append(pk_value) # Masukin value ID di paling akhir buat WHERE
        
        query = f"UPDATE `{table}` SET {set_clause} WHERE `{primary_key}` = %s;"
        cursor.execute(query, values)
        affected = cursor.rowcount
        conn.close()
        return {"status": "success", "affected_rows": affected}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_table_structure(db_type: str, host: str, port: int, user: str, password: str, database: str, table: str):
    """Ambil skema/struktur kolom tabel (SHOW FULL COLUMNS)"""
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
        cursor = conn.cursor()
        cursor.execute(f"SHOW FULL COLUMNS FROM `{table}`;")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        return {"status": "success", "columns": columns, "rows": rows}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_database(db_type: str, host: str, port: int, user: str, password: str, db_name: str):
    """Bikin database baru (MySQL/MariaDB)"""
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, autocommit=True)
        cursor = conn.cursor()
        safe_db = db_name.replace('`', '')
        cursor.execute(f"CREATE DATABASE `{safe_db}`;")
        conn.close()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_table(db_type: str, host: str, port: int, user: str, password: str, database: str, table_name: str, columns_json: str):
    """Bikin tabel baru dengan struktur kolom dinamis dari UI"""
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, autocommit=True)
        cursor = conn.cursor()
        safe_tbl = table_name.replace('`', '')
        
        cols = json.loads(columns_json)
        col_defs = []
        pk_col = None
        
        for col in cols:
            name = col['name'].replace('`', '')
            ctype = col['type'].upper()
            length = col.get('length', '').strip()
            is_ai = col.get('ai', False)
            is_pk = col.get('pk', False)
            
            # Fallback otomatis kalau VARCHAR kosong biar gak kena syntax error MariaDB
            if ctype == 'VARCHAR' and not length:
                length = '255'
            
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

def add_table_column(db_type: str, host: str, port: int, user: str, password: str, database: str, table: str, col_data: dict):
    """Menambahkan kolom baru ke tabel yang sudah ada"""
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, autocommit=True)
        cursor = conn.cursor()
        
        name = col_data['name'].replace('`', '')
        ctype = col_data['type'].upper()
        length = col_data.get('length', '').strip()
        is_ai = col_data.get('ai', False)
        
        if ctype == 'VARCHAR' and not length:
            length = '255'
            
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

def execute_batch_structure_action(db_type: str, host: str, port: int, user: str, password: str, database: str, table: str, action: str, columns: list):
    """Menangani batch Duplicate & Delete pada KOLOM/FIELD struktur tabel"""
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, autocommit=True)
        cursor = conn.cursor()
        
        if action == "delete":
            # Bikin syntax: ALTER TABLE tabel DROP COLUMN a, DROP COLUMN b;
            drop_clauses = ", ".join([f"DROP COLUMN `{col}`" for col in columns])
            query = f"ALTER TABLE `{table}` {drop_clauses};"
            cursor.execute(query)
            
        elif action == "duplicate":
            # Ambil detail tipe datanya dulu biar copy-annya akurat
            cols_placeholder = ",".join([f"'{col}'" for col in columns])
            cursor.execute(f"SHOW FULL COLUMNS FROM `{table}` WHERE Field IN ({cols_placeholder})")
            col_defs = cursor.fetchall()
            
            add_clauses = []
            for row in col_defs:
                col_name = row[0]
                col_type = row[1]
                col_null = "NULL" if row[3] == "YES" else "NOT NULL"
                col_default = f"DEFAULT '{row[4]}'" if row[4] is not None else ""
                col_extra = row[6] # auto_increment dsb
                
                # Buang auto_increment dari kolom duplikat biar gak error duplicate key
                if "auto_increment" in col_extra.lower():
                    col_extra = col_extra.lower().replace("auto_increment", "")
                    
                new_col_name = f"{col_name}_copy"
                add_clauses.append(f"ADD COLUMN `{new_col_name}` {col_type} {col_null} {col_default} {col_extra}")
                
            query = f"ALTER TABLE `{table}` {', '.join(add_clauses)};"
            cursor.execute(query)
            
        conn.close()
        return {"status": "success", "affected_columns": len(columns)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def drop_table(db_type: str, host: str, port: int, user: str, password: str, database: str, table: str):
    """Menghapus tabel beserta seluruh datanya (DROP TABLE)"""
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, autocommit=True)
        cursor = conn.cursor()
        
        safe_tbl = table.replace('`', '')
        cursor.execute(f"DROP TABLE `{safe_tbl}`;")
        conn.close()
        
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def insert_row(db_type: str, host: str, port: int, user: str, password: str, database: str, table: str, insert_data: dict):
    """Insert 1 baris data baru secara dinamis"""
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database, autocommit=True)
        cursor = conn.cursor()
        
        # Susun nama kolom dan placeholder (%s) untuk mencegah SQL Injection
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
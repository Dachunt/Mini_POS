#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inicializar la base de datos MySQL para Mini POS.

Requisitos:
- MySQL/MariaDB corriendo en localhost:3306
- Usuario root sin contraseña (o ajusta las credenciales)

Uso:
    python init_db.py
"""

import subprocess
import sys
import os
from pathlib import Path

def init_database_with_mysql_cli():
    """Ejecutar schema.sql usando comando mysql directamente"""
    
    script_dir = Path(__file__).parent
    schema_file = script_dir / "database" / "schema.sql"
    
    if not schema_file.exists():
        print(f"ERROR: Schema file not found: {schema_file}")
        return False
    
    print(f"[*] Initializing database...")
    print(f"    Schema: {schema_file}")
    print()
    
    try:
        # Intentar ejecutar mysql < schema.sql
        with open(schema_file, 'r', encoding='utf-8') as f:
            result = subprocess.run(
                ["mysql", "-u", "root"],
                stdin=f,
                capture_output=True,
                text=True,
                timeout=30
            )
        
        if result.returncode != 0:
            print(f"ERROR executing SQL:")
            print(result.stderr)
            return False
        
        print("[+] Database initialized successfully")
        print()
        print("[*] Verifying tables created:")
        
        # Verificar que se crearon las tablas
        verify_result = subprocess.run(
            ["mysql", "-u", "root", "-e", "USE pos_inventario; SHOW TABLES;"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if verify_result.returncode == 0:
            print(verify_result.stdout)
        
        return True
        
    except FileNotFoundError:
        print("ERROR: mysql command not found in PATH")
        print()
        print("[!] Solutions:")
        print("    1. Add MySQL to Windows PATH:")
        print("       - Usually at: C:\\Program Files\\MySQL\\MySQL Server X.X\\bin")
        print()
        print("    2. Or run manually:")
        print("       mysql -u root < database/schema.sql")
        print()
        print("    3. Or use MySQL Workbench to run the script")
        return False
        
    except subprocess.TimeoutExpired:
        print("ERROR: Operation timed out")
        return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def init_database_with_pymysql():
    """Alternativa: Usar PyMySQL para crear la BD si mysql CLI falla"""
    
    script_dir = Path(__file__).parent
    schema_file = script_dir / "database" / "schema.sql"
    
    if not schema_file.exists():
        print(f"ERROR: Schema file not found: {schema_file}")
        return False
    
    try:
        import pymysql
        
        print("[*] Using PyMySQL to initialize...")
        
        # Leer el contenido del schema
        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Conectar a MySQL sin especificar BD (para crearla)
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        
        # Ejecutar cada comando del script
        for statement in sql_content.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                print(f"    [+] {statement[:50]}...")
                cursor.execute(statement)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("[+] Database initialized successfully")
        return True
        
    except ImportError:
        print("ERROR: PyMySQL not installed")
        print("    Install with: pip install pymysql")
        return False
        
    except Exception as e:
        error_msg = str(e)
        if "Access denied" in error_msg:
            print(f"ERROR: Connection denied")
            print()
            print("[!] Verify that:")
            print("    1. MySQL is running")
            print("    2. root user exists (no password)")
            print("    3. You can connect with: mysql -u root")
        else:
            print(f"ERROR: {e}")
        return False

def main():
    """Función principal"""
    
    # Configurar encoding UTF-8 para Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("=" * 60)
    print("Mini POS - Database Initializer")
    print("=" * 60)
    print()
    
    # Intentar primero con mysql CLI
    print("Attempting with mysql command...")
    if init_database_with_mysql_cli():
        return 0
    
    print()
    print("Attempting with PyMySQL...")
    if init_database_with_pymysql():
        return 0
    
    print()
    print("ERROR: Could not initialize database")
    print()
    print("[!] Options:")
    print("    1. Install MySQL Community Server")
    print("    2. Or run manually:")
    print("       mysql -u root < database/schema.sql")
    return 1

if __name__ == "__main__":
    sys.exit(main())

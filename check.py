#!/usr/bin/env python3
"""
Script de verificación previa de Mini POS.

Verifica que todos los requisitos estén instalados y configurados.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ requerido (actual: {version.major}.{version.minor})")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_mysql():
    """Verificar que MySQL está disponible"""
    try:
        result = subprocess.run(
            ["mysql", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ MySQL: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ MySQL no encontrado en PATH")
    print("   Instálalo desde https://dev.mysql.com/downloads/mysql/")
    return False

def check_dependencies():
    """Verificar dependencias Python"""
    deps = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'pymysql': 'PyMySQL'
    }
    
    missing = []
    for module, name in deps.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name}")
            missing.append(module)
    
    if missing:
        print("\n📦 Instala las dependencias con:")
        print("   pip install -r backend/requirements.txt")
        return False
    
    return True

def check_files():
    """Verificar que los archivos necesarios existen"""
    files = [
        "backend/app.py",
        "backend/config.py",
        "backend/models.py",
        "backend/routes.py",
        "backend/requirements.txt",
        "frontend/index.html",
        "database/schema.sql",
    ]
    
    all_exist = True
    for file in files:
        path = Path(file)
        if path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            all_exist = False
    
    return all_exist

def check_database_connection():
    """Verificar conexión a MySQL"""
    try:
        result = subprocess.run(
            ["mysql", "-u", "root", "-e", "SELECT 1"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Conexión MySQL (sin contraseña)")
            return True
    except:
        pass
    
    print("⚠️  No se puede conectar a MySQL con root sin contraseña")
    print("   (Probablemente está bien si MySQL está protegido con contraseña)")
    return None  # Warning, no error

def main():
    """Ejecutar todas las verificaciones"""
    
    print("=" * 60)
    print("🛒 Mini POS — Verificación de Requisitos")
    print("=" * 60)
    print()
    
    checks = [
        ("Python", check_python_version),
        ("MySQL/MariaDB", check_mysql),
        ("Archivos del proyecto", check_files),
        ("Dependencias Python", check_dependencies),
        ("Conexión a BD", check_database_connection),
    ]
    
    os.chdir(Path(__file__).parent)
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 Verificando {name}...")
        print("-" * 60)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append((name, False))
    
    # Resumen
    print()
    print("=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    critical_ok = all(r for _, r in results[:-1])  # Exclude BD check from critical
    
    for name, result in results:
        status = "✅" if result else ("⚠️ " if result is None else "❌")
        print(f"{status} {name}")
    
    print()
    if critical_ok:
        print("✅ Todos los requisitos críticos están OK")
        print()
        print("🚀 Próximos pasos:")
        print("   1. python init_db.py      (crear base de datos)")
        print("   2. python run.py           (iniciar servidor)")
        print("   3. http://localhost:5000   (abrir en navegador)")
        return 0
    else:
        print("❌ Faltan requisitos críticos. Revisa los errores arriba.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

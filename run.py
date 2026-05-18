#!/usr/bin/env python3
"""
Script para ejecutar la aplicación Mini POS en modo desarrollo.

Este script:
1. Verifica que el entorno virtual está activado
2. Verifica que las dependencias están instaladas
3. Inicia el servidor Flask

Uso:
    python run.py

O en Windows:
    python run.py
"""

import sys
import os
from pathlib import Path
import subprocess

def check_venv():
    """Verificar que estamos en un entorno virtual"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return True
    return False

def install_dependencies():
    """Instalar dependencias si no están presentes"""
    try:
        import flask
        import flask_cors
        import flask_sqlalchemy
        import pymysql
        print("✅ Todas las dependencias están instaladas")
        return True
    except ImportError as e:
        print(f"⚠️  Dependencia faltante: {e}")
        print("📦 Instalando dependencias...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "-r", "backend/requirements.txt"
            ])
            print("✅ Dependencias instaladas correctamente")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error instalando dependencias")
            return False

def main():
    """Función principal"""
    
    print("🛒 Mini POS — Iniciando servidor...")
    print()
    
    # Verificar entorno virtual
    if not check_venv():
        print("⚠️  ADVERTENCIA: No estás en un entorno virtual")
        print("   Se recomienda activar .venv primero:")
        print("   - Windows: .venv\\Scripts\\Activate.ps1")
        print("   - Linux/Mac: source .venv/bin/activate")
        print()
    
    # Obtener directorio raíz del proyecto
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Instalar dependencias si faltan
    if not install_dependencies():
        return 1
    
    # Agregar backend al path de Python para poder importar
    backend_path = str(project_root / "backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    print()
    print("🚀 Iniciando Flask en http://0.0.0.0:5000")
    print("   Abre http://localhost:5000 en tu navegador")
    print("   Presiona Ctrl+C para detener el servidor")
    print()
    
    try:
        # Importar y ejecutar app desde backend
        from app import create_app
        
        app = create_app()
        app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
        
    except ImportError as e:
        print(f"❌ Error importando aplicación: {e}")
        print(f"   Backend path: {backend_path}")
        print(f"   Python path: {sys.path}")
        return 1
    except KeyboardInterrupt:
        print("\n✋ Servidor detenido")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script alternativo para ejecutar Mini POS - Versión simplificada
"""

import sys
import os
from pathlib import Path

def main():
    # Configurar encoding UTF-8 para Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Obtener la ruta del proyecto
    project_root = Path(__file__).parent.absolute()
    backend_dir = project_root / "backend"
    
    # Agregar backend al path de Python
    sys.path.insert(0, str(backend_dir))
    
    # Cambiar al directorio del backend
    os.chdir(str(backend_dir))
    
    print("[*] Mini POS - Starting server...")
    print(f"    Directory: {backend_dir}")
    print()
    
    try:
        # Importar Flask app
        from app import create_app
        
        print("[+] Application loaded successfully")
        print()
        print("[*] Starting Flask on http://0.0.0.0:5000")
        print("    Open http://localhost:5000 in your browser")
        print("    Press Ctrl+C to stop the server")
        print()
        
        # Crear y ejecutar app
        app = create_app()
        app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
        
    except ModuleNotFoundError as e:
        print(f"ERROR: Module not found: {e}")
        print(f"    Make sure to install: pip install -r {backend_dir}/requirements.txt")
        return 1
    except FileNotFoundError as e:
        print(f"ERROR: File not found: {e}")
        return 1
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main() or 0)

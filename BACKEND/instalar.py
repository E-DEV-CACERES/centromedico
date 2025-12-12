#!/usr/bin/env python3
"""
Script de instalación automatizada para el Sistema de Centro Médico Backend

Este script configura automáticamente todo el entorno necesario:
- Verifica la versión de Python
- Crea el entorno virtual
- Instala las dependencias
- Verifica/crea la base de datos
- Opcionalmente ejecuta scripts de inicialización

Uso:
    python instalar.py
    python instalar.py --con-datos  # Incluye datos de ejemplo
"""

import sys
import os
import subprocess
import platform
import sqlite3
from pathlib import Path
from typing import Optional, Tuple

# Colores para la salida (si está disponible)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    # Crear funciones dummy para colores
    class Fore:
        GREEN = ""
        RED = ""
        YELLOW = ""
        BLUE = ""
        CYAN = ""
        RESET = ""
    class Style:
        RESET_ALL = ""
        BRIGHT = ""

# Configuración
REQUIRED_PYTHON_VERSION = (3, 8)
VENV_DIR = "venv"
DATABASE_FILE = "v1siscentro.db"
REQUIREMENTS_FILE = "requirements.txt"
SCRIPTS_INICIALIZACION = [
    "crear_admin.py",
    "crear_doctores.py",
    "crear_pacientes.py",
    "crear_recetas.py"
]


def print_success(message: str):
    """Imprime un mensaje de éxito"""
    if HAS_COLORAMA:
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    else:
        print(f"✓ {message}")


def print_error(message: str):
    """Imprime un mensaje de error"""
    if HAS_COLORAMA:
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
    else:
        print(f"✗ {message}")


def print_warning(message: str):
    """Imprime un mensaje de advertencia"""
    if HAS_COLORAMA:
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
    else:
        print(f"⚠ {message}")


def print_info(message: str):
    """Imprime un mensaje informativo"""
    if HAS_COLORAMA:
        print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")
    else:
        print(f"ℹ {message}")


def print_header(message: str):
    """Imprime un encabezado"""
    if HAS_COLORAMA:
        print(f"\n{Fore.BLUE}{Style.BRIGHT}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}{message}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{Style.BRIGHT}{'='*60}{Style.RESET_ALL}\n")
    else:
        print(f"\n{'='*60}")
        print(f"{message}")
        print(f"{'='*60}\n")


def verificar_python() -> Tuple[bool, Optional[str]]:
    """Verifica que Python esté instalado y tenga la versión correcta"""
    print_header("Verificando Python")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print_info(f"Versión de Python detectada: {version_str}")
    
    if version < REQUIRED_PYTHON_VERSION:
        print_error(
            f"Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}+ es requerido. "
            f"Versión actual: {version_str}"
        )
        return False, None
    
    print_success(f"Python {version_str} es compatible")
    
    # Verificar que pip esté disponible
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            check=True,
            capture_output=True
        )
        print_success("pip está disponible")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("pip no está disponible. Por favor, instálalo primero.")
        return False, None
    
    return True, sys.executable


def crear_entorno_virtual(python_exe: str) -> bool:
    """Crea el entorno virtual si no existe"""
    print_header("Configurando Entorno Virtual")
    
    venv_path = Path(VENV_DIR)
    
    if venv_path.exists():
        print_info(f"El entorno virtual '{VENV_DIR}' ya existe")
        respuesta = input("¿Deseas recrearlo? (s/N): ").strip().lower()
        if respuesta == 's':
            print_info("Eliminando entorno virtual existente...")
            import shutil
            try:
                shutil.rmtree(venv_path)
                print_success("Entorno virtual eliminado")
            except Exception as e:
                print_error(f"Error al eliminar entorno virtual: {e}")
                return False
        else:
            print_info("Usando entorno virtual existente")
            return True
    
    print_info(f"Creando entorno virtual en '{VENV_DIR}'...")
    try:
        subprocess.run(
            [python_exe, "-m", "venv", VENV_DIR],
            check=True,
            capture_output=True
        )
        print_success("Entorno virtual creado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Error al crear entorno virtual: {e}")
        return False


def obtener_python_venv() -> str:
    """Obtiene la ruta al ejecutable de Python del entorno virtual"""
    system = platform.system()
    if system == "Windows":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        return os.path.join(VENV_DIR, "bin", "python")


def obtener_pip_venv() -> str:
    """Obtiene la ruta al ejecutable de pip del entorno virtual"""
    system = platform.system()
    if system == "Windows":
        return os.path.join(VENV_DIR, "Scripts", "pip.exe")
    else:
        return os.path.join(VENV_DIR, "bin", "pip")


def instalar_dependencias() -> bool:
    """Instala las dependencias desde requirements.txt"""
    print_header("Instalando Dependencias")
    
    if not Path(REQUIREMENTS_FILE).exists():
        print_error(f"Archivo '{REQUIREMENTS_FILE}' no encontrado")
        return False
    
    pip_exe = obtener_pip_venv()
    
    if not Path(pip_exe).exists():
        print_error("pip del entorno virtual no encontrado")
        return False
    
    print_info(f"Instalando dependencias desde '{REQUIREMENTS_FILE}'...")
    try:
        # Actualizar pip primero
        print_info("Actualizando pip...")
        subprocess.run(
            [pip_exe, "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )
        print_success("pip actualizado")
        
        # Instalar dependencias
        result = subprocess.run(
            [pip_exe, "install", "-r", REQUIREMENTS_FILE],
            check=True,
            capture_output=True,
            text=True
        )
        print_success("Dependencias instaladas exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Error al instalar dependencias: {e}")
        if e.stdout:
            print_info(f"Salida: {e.stdout}")
        if e.stderr:
            print_error(f"Error: {e.stderr}")
        return False


def verificar_base_datos() -> bool:
    """Verifica que la base de datos exista y sea válida"""
    print_header("Verificando Base de Datos")
    
    db_path = Path(DATABASE_FILE)
    
    if not db_path.exists():
        print_warning(f"La base de datos '{DATABASE_FILE}' no existe")
        respuesta = input("¿Deseas crear una base de datos vacía? (s/N): ").strip().lower()
        if respuesta == 's':
            try:
                conn = sqlite3.connect(DATABASE_FILE)
                conn.execute("PRAGMA foreign_keys = ON")
                conn.close()
                print_success(f"Base de datos '{DATABASE_FILE}' creada")
                print_info("Inicializando tablas...")
                
                # Ejecutar script de inicialización de tablas
                python_venv = obtener_python_venv()
                if Path(python_venv).exists():
                    try:
                        subprocess.run(
                            [python_venv, "inicializar_tablas.py"],
                            check=True,
                            capture_output=True
                        )
                        print_success("Tablas inicializadas correctamente")
                    except subprocess.CalledProcessError:
                        print_warning("No se pudieron crear las tablas automáticamente")
                        print_info("Ejecuta 'python inicializar_tablas.py' manualmente")
                else:
                    print_warning("Ejecuta 'python inicializar_tablas.py' para crear las tablas")
                
                return True
            except Exception as e:
                print_error(f"Error al crear base de datos: {e}")
                return False
        else:
            print_warning("Continuando sin base de datos. Asegúrate de tenerla antes de ejecutar la API.")
            return True
    
    # Verificar que la base de datos sea válida
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cursor.fetchall()
        conn.close()
        
        if tablas:
            print_success(f"Base de datos '{DATABASE_FILE}' encontrada con {len(tablas)} tabla(s)")
            
            # Verificar que la tabla citas existe
            conn = sqlite3.connect(DATABASE_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='citas'")
            if not cursor.fetchone():
                print_warning("La tabla 'citas' no existe")
                respuesta = input("¿Deseas inicializar todas las tablas? (s/N): ").strip().lower()
                if respuesta == 's':
                    python_venv = obtener_python_venv()
                    if Path(python_venv).exists():
                        try:
                            subprocess.run(
                                [python_venv, "inicializar_tablas.py"],
                                check=True,
                                capture_output=True
                            )
                            print_success("Tablas inicializadas correctamente")
                        except subprocess.CalledProcessError as e:
                            print_warning("No se pudieron crear las tablas automáticamente")
                            print_info("Ejecuta 'python inicializar_tablas.py' manualmente")
            conn.close()
        else:
            print_warning("Base de datos existe pero no tiene tablas")
            respuesta = input("¿Deseas inicializar todas las tablas? (s/N): ").strip().lower()
            if respuesta == 's':
                python_venv = obtener_python_venv()
                if Path(python_venv).exists():
                    try:
                        subprocess.run(
                            [python_venv, "inicializar_tablas.py"],
                            check=True,
                            capture_output=True
                        )
                        print_success("Tablas inicializadas correctamente")
                    except subprocess.CalledProcessError:
                        print_warning("Ejecuta 'python inicializar_tablas.py' manualmente")
        return True
    except Exception as e:
        print_error(f"Error al verificar base de datos: {e}")
        return False


def ejecutar_script_inicializacion(script: str, con_datos: bool = False) -> bool:
    """Ejecuta un script de inicialización"""
    script_path = Path(script)
    
    if not script_path.exists():
        print_warning(f"Script '{script}' no encontrado, omitiendo...")
        return True
    
    python_venv = obtener_python_venv()
    
    if not Path(python_venv).exists():
        print_error("Python del entorno virtual no encontrado")
        return False
    
    print_info(f"Ejecutando '{script}'...")
    try:
        result = subprocess.run(
            [python_venv, script],
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        print_success(f"'{script}' ejecutado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print_warning(f"Error al ejecutar '{script}': {e}")
        if e.stdout:
            print_info(f"Salida: {e.stdout}")
        if e.stderr:
            print_warning(f"Error: {e.stderr}")
        # No fallar la instalación si un script opcional falla
        return True


def ejecutar_scripts_inicializacion(con_datos: bool = False):
    """Ejecuta los scripts de inicialización"""
    if not con_datos:
        print_header("Inicialización Básica")
        # Solo ejecutar crear_admin.py
        ejecutar_script_inicializacion("crear_admin.py", con_datos)
    else:
        print_header("Inicialización Completa con Datos de Ejemplo")
        for script in SCRIPTS_INICIALIZACION:
            ejecutar_script_inicializacion(script, con_datos)


def mostrar_resumen():
    """Muestra un resumen de la instalación"""
    print_header("Instalación Completada")
    
    print_info("Resumen de la instalación:")
    print(f"  • Entorno virtual: {VENV_DIR}/")
    print(f"  • Base de datos: {DATABASE_FILE}")
    print(f"  • Dependencias: {REQUIREMENTS_FILE}")
    
    print_info("\nPara iniciar el servidor:")
    system = platform.system()
    if system == "Windows":
        print("  • Windows: iniciar_api.bat")
    else:
        print("  • Linux/Mac: ./iniciar_api.sh")
    
    print_info("\nO manualmente:")
    if system == "Windows":
        print(f"  {VENV_DIR}\\Scripts\\activate")
    else:
        print(f"  source {VENV_DIR}/bin/activate")
    print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    
    print_info("\nLa API estará disponible en:")
    print("  • API: http://localhost:8000")
    print("  • Documentación: http://localhost:8000/docs")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Instalador automatizado para el Sistema de Centro Médico Backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python instalar.py                    # Instalación básica
  python instalar.py --con-datos        # Instalación con datos de ejemplo
        """
    )
    parser.add_argument(
        "--con-datos",
        action="store_true",
        help="Ejecutar scripts de inicialización con datos de ejemplo"
    )
    
    args = parser.parse_args()
    
    print_header("Instalador del Sistema de Centro Médico Backend")
    print_info("Este script configurará automáticamente todo el entorno necesario.\n")
    
    # Paso 1: Verificar Python
    python_ok, python_exe = verificar_python()
    if not python_ok:
        print_error("Instalación cancelada. Por favor, instala Python 3.8 o superior.")
        sys.exit(1)
    
    # Paso 2: Crear entorno virtual
    if not crear_entorno_virtual(python_exe):
        print_error("Instalación cancelada. Error al crear el entorno virtual.")
        sys.exit(1)
    
    # Paso 3: Instalar dependencias
    if not instalar_dependencias():
        print_error("Instalación cancelada. Error al instalar dependencias.")
        sys.exit(1)
    
    # Paso 4: Verificar base de datos
    if not verificar_base_datos():
        print_error("Instalación cancelada. Error al verificar la base de datos.")
        sys.exit(1)
    
    # Paso 5: Ejecutar scripts de inicialización
    ejecutar_scripts_inicializacion(con_datos=args.con_datos)
    
    # Resumen final
    mostrar_resumen()
    
    print_success("\n¡Instalación completada exitosamente!")


if __name__ == "__main__":
    main()


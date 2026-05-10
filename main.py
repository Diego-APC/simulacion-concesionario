import sys
from presentacion.cli import ejecutar_cli
from presentacion.gui import ejecutar_gui

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        ejecutar_gui()
    else:
        ejecutar_cli()
import os
import time


def execute(consoleLine):
    path = consoleLine[1][6:]
    if path.endswith('.dsk') == False:
        if path.endswith('.dsk\"') == False:
            return 'Error: Path debe ser un archivo .dsk'
    if path.startswith('\"'):
        path = path[1:-1]
        if not os.path.exists(path):
            return 'Error: El disco no existe.'
    else:
        if not os.path.exists(path):
            return 'Error: El disco no existe.'

    # Confirmar eliminacion
    print('¿Está seguro que desea eliminar el disco? (Y/N)')
    confirm = input()
    if not (confirm == 'Y' or confirm == 'y'):
        return 'Eliminación cancelada.'
    print('Eliminando disco en: ' + path + '...')
    os.remove(path)
    return "Disco eliminado exitosamente.\n"
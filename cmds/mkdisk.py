from cmds.structs.MBR import MBR, Partition

def execute(consoleLine):
    # Default values
    size = 0
    unit = 'M'
    path = ''
    fit = 'F'

    # Buscar parametros y retornar error si no son validos

    for i in range(len(consoleLine)):
        if consoleLine[i].startswith('-size='):
            size = int(consoleLine[i][6:])
            if size <= 0:
                return 'Error: Size debe ser mayor a 0.'
        elif consoleLine[i].startswith('-path='):
            path = consoleLine[i][6:]
            if path.endswith('.dsk') == False:
                if path.endswith('.dsk\"') == False:
                    return 'Error: Path debe ser un archivo .dsk'
            if len(path) < 5:
                return 'Error: Path no puede ser vacío.'
        elif consoleLine[i].startswith('-fit='):
            fit = consoleLine[i][5:].upper()
            if fit != 'BF' and fit != 'FF' and fit != 'WF':
                return 'Error: Fit no válido.'
            elif fit == 'BF':
                fit = 'B'
            elif fit == 'FF':
                fit = 'F'
            elif fit == 'WF':
                fit = 'W'
        elif consoleLine[i].startswith('-unit='):
            unit = consoleLine[i][6:].upper()
            if unit != 'K' and unit != 'M':
                return 'Error: Unit no válida.'

    if path == '':
        return 'Error: Path inválido.'
    # definir size en bytes
    if unit == 'K':
        size = size * 1024
    elif unit == 'M':
        size = size * 1024 * 1024
    # Tratar de crear disco
    mbr = MBR(fit, size)
    mbr.createDisk(path)

    return 'Disco creado exitosamente.'


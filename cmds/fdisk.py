import os
from cmds.structs.MBR import MBR, Partition, EBR


def execute(consoleLine):
    size = 0
    unit = 'K'
    path = ''
    name = ''
    type = 'P'
    fit = 'WF'
    delete = ''
    add = 0
    
    #     status='N', type='P', fit='F', start=-1, size=0, name=''):

    # Buscar parametros
    try:
        sizeFound, deleteFound, addFound = False, False, False
        for i in range(len(consoleLine)):
            if consoleLine[i].startswith('-size='):
                size = int(consoleLine[i][6:])
                if size <= 0:
                    return 'Error: Size debe ser mayor a 0.'
                if not deleteFound and not addFound:
                    sizeFound = True
            elif consoleLine[i].startswith('-path='):
                path = consoleLine[i][6:]
                if path.endswith('.dsk') == False:
                    return 'Error: Path debe ser un archivo .dsk'
                if len(path) < 5:
                    return 'Error: Path no puede ser vacío.'
            elif consoleLine[i].startswith('-name='):
                name = consoleLine[i][6:]
                if len(name) < 1:
                    return 'Error: Name no puede ser vacío.'
            elif consoleLine[i].startswith('-unit='):
                unit = consoleLine[i][6:].upper()
                if unit != 'B' and unit != 'K' and unit != 'M':
                    return 'Error: Unit no válida.'
            elif consoleLine[i].startswith('-type='):
                type = consoleLine[i][6:].upper()
                if type != 'P' and type != 'E' and type != 'L':
                    return 'Error: Type no válido.'                
            elif consoleLine[i].startswith('-fit='):
                fit = consoleLine[i][5:].upper()
                if fit != 'BF' and fit != 'FF' and fit != 'WF':
                    return 'Error: Fit no válido.'
            elif consoleLine[i].startswith('-delete='):
                delete = consoleLine[i][8:].upper()
                if delete != 'FULL':
                    return 'Error: Delete no válido.'
                if not sizeFound and not addFound:
                    deleteFound = True
            elif consoleLine[i].startswith('-add='):
                add = int(consoleLine[i][5:])
                if add == 0:
                    return 'Error: Add no puede ser 0.'
                if not sizeFound and not deleteFound:
                    addFound = True
        
        if sizeFound:
            # Se crea una partición
            if unit == 'K':
                size *= 1024
            elif unit == 'M':
                size *= 1024 * 1024
            if fit == 'BF':
                fit = 'B'
            elif fit == 'FF':
                fit = 'F'
            elif fit == 'WF':
                fit = 'W'
            return newPartition(size, path, name, type, fit)
        elif addFound:
            # Se modifica el tamaño de una partición
            pass
        elif deleteFound:
            # Se elimina una partición
            pass
    except:
        return 'Error: En ingreso de parámetros.'
    

def newPartition(size, path, name, type, fit):
    try:
        if not os.path.exists(path):
            return 'Error: Disco no encontrado.'
        with open(path, 'r+b') as file:
            mbr = MBR()
            mbr.decode(file.read(136))
            file.close()

        # Validar que no exista una partición con el mismo nombre
        if mbr.hasPartitionNamed(name, path):
            return 'Error: Ya existe una partición con ese nombre.'
        
        # Primarias y extendidas
        if type == 'P' or type == 'E':            
            if type == 'E' and mbr.hasExtendedPartition(): # Solo puede haber una extendida
                return 'Error: Ya existe una partición extendida.'
            if not mbr.hasFreePrimaryPartition: # Solo pueden haber 4 particiones primarias
                return 'Error: No se puede crear la partición.\nLas 4 particiones primarias ya están creadas.'
            
            # FF - First Fit
            index = mbr.getPartitionIndexForFF(size) # Obtener indice de partición para FF
            if index == -1:
                return ('Error: No hay espacio suficiente para crear la partición o ya se encuentran 4 particiones '
                        'creadas.')
            start = mbr.getStartForFF(index)
            newpartition = Partition(status='A', type=type, fit=fit, start=start, size=size, name=name)
            mbr.setPartition(index, newpartition)
            mbr.updateDisk(path)
            # Crear EBR si es extendida
            if type == 'E':
                mbr.addFirstEBR(path)
            return 'Partición creada exitosamente.'

        # Lógicas
        elif type == 'L':
            print('Creando partición lógica...')
            if not mbr.hasExtendedPartition():
                return 'Error: No existe una partición extendida aún para una partición lógica.'
            if not mbr.hasFreeLogicalPartition(path): # Solo pueden haber X particiones lógicas
                return 'Error: No se puede crear la partición. Límite de particiones lógicas alcanzado.'
            mbr.addLogicFirstFit(path, size, name, fit)
            return 'Partición creada exitosamente.'


    except Exception as e   :
        return 'Error: Disco no encontrado.'
    
    
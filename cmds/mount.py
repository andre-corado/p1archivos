from cmds.structs.MBR import MBR, Partition, EBR


def execute(consoleLine):
    name = ''
    path = ''
    for i in range(len(consoleLine)):
        if consoleLine[i].startswith('-name='):
            name = consoleLine[i][6:]
            if len(name) < 1:
                return 'Error: Name no puede ser vacío.'
        elif consoleLine[i].startswith('-path='):
            path = consoleLine[i][6:]
            if path.endswith('.dsk') == False:
                return 'Error: Path debe ser un archivo .dsk'
            if len(path) < 5:
                return 'Error: Path no puede ser vacío.'
    if name == '' or path == '':
        return 'Error: Falta parámetro obligatorio.'

    # Leer MBR del disco
    try:
        with open(path, 'r+b') as file:
            mbr = MBR()
            mbr.decode(file.read(136))
            file.close()
    except:
        return 'Error: No se pudo leer el disco.'

    if not mbr.hasPartitionNamed(name, path):
        return 'Error: No existe la partición con ese nombre.'

    # Obtener partición
    partition, type = mbr.getPartitionNamed(name, path)
    if type == 'E':
        return 'Error: No se puede montar la partición extendida.'
    if partition == None:
        return 'Error: No se pudo obtener la partición.'


    # Obtener id de partición
    idPartition = "54"
    # Obtener int dentro de name
    for i in range(len(name)):
        if name[i].isdigit():
            idPartition += name[i]
        else:
            continue
    idPartition += path.split('/')[-1][:-4] # Obtener nombre del disco

    # Montar partición
    if isMounted(idPartition):
        return 'Error: La partición ya está montada.'
    return mountPartition(path, name, idPartition, type)


def isMounted(idPartition):
    # Verificar si ya está montada
    from analizador import mountedPartitions
    # Verificar si ya está montada en el diccionario
    if idPartition in mountedPartitions:
        return True
    return False

def getMountedPartition(idPartition):
    from analizador import mountedPartitions
    return mountedPartitions[idPartition]

def mountPartition(path, name, id, type):
    # Montar partición
    from analizador import mountedPartitions, mountedPartition
    part = mountedPartition(path, name, type)
    mountedPartitions[id] = part
    return 'Partición montada.'
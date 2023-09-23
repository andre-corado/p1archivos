import os.path
from graphviz import Digraph

from cmds.structs.MBR import MBR
from cmds.mount import getMountedPartition
from cmds.rep.bitmaps import makebm_block, makebm_inode

def execute(consoleLine):
    name, path, id, ruta = '', '', '', ''
    nameFound, pathFound, idFound, rutaFound = False, False, False, False
    for i in range(len(consoleLine)):
        if consoleLine[i].startswith('-path='):
            path = consoleLine[i][6:]
            if len(path) < 5:
                return 'Error: Path no puede ser vacío.'
            pathFound = True
        if consoleLine[i].startswith('-name='):
            name = consoleLine[i][6:].upper()
            if len(name) < 1:
                return 'Error: Name no puede ser vacío.'
            nameFound = True
        if consoleLine[i].startswith('-id='):
            id = consoleLine[i][4:]
            if len(id) < 4:
                return 'Error: Id no válido, muy breve.'
            p = getMountedPartition(id)
            if p == None:
                return 'Error: No existe una partición montada con ese id.'
            idFound = True
        if consoleLine[i].startswith('-ruta='):
            ruta = consoleLine[i][6:]
            if len(ruta) < 1:
                return 'Error: Ruta no puede ser vacío.'
            rutaFound = True

    if p == None:
        return 'Error: No existe una partición montada con ese id.'

    if name == 'MBR':
        if not pathFound or not idFound:
            return 'Error: Faltan parámetros obligatorios.'
        return makeMBRTable(path, p.path)
    elif name == 'DISK':
        if not pathFound or not idFound:
            return 'Error: Faltan parámetros obligatorios.'
        return makeDiskTable(path, p.path)
    elif name == 'BM_INODE':
        if not pathFound or not idFound:
            return 'Error: Faltan parámetros obligatorios.'
        if not path.endswith('.txt'):
            return 'Error: El archivo debe ser .txt'
        return makebm_inode(path, p)
    elif name == 'BM_BLOCK':
        if not pathFound or not idFound:
            return 'Error: Faltan parámetros obligatorios.'
        if not path.endswith('.txt'):
            return 'Error: El archivo debe ser .txt'
        return makebm_block(path, p)




def makeMBRTable(tablePath, diskPath):
    # Leer disco
    mbr = getMBRFromDisk(diskPath)
    if isinstance(mbr, str):
        return mbr
    if ".jpg" in tablePath or ".png" in tablePath or ".pdf" in tablePath:
        if not tablePath.endswith("\""):
            ext = tablePath[-3:]
            tablePath = tablePath[:-4]
        else:
            ext = tablePath[-4:-1]
            tablePath = tablePath[1:-5]
        dot = mbr.getGraph(ext, diskPath)
        # Verificar si existe directorio y crearlo si no existe
        dir = getDirFromPath(tablePath)
        if os.path.exists(dir) == False:
            os.makedirs(dir)

        # Renderizar dot en table path
        dot.render(tablePath, view=True)

        # Borrar archivos temporales
        os.remove(tablePath)
    else:
        return 'Error: Formato de reporte no válido.'
    return 'Tabla MBR creada exitosamente.'


def makeDiskTable(tablePath, diskPath):
    ext = ''

    class Bloque:
        def __init__(self, size, tipo):
            self.size = size
            self.type = tipo
            self.ebr = None

    mbr = getMBRFromDisk(diskPath)
    if isinstance(mbr, str):
        return mbr
    if ".jpg" in tablePath or ".png" in tablePath or ".pdf" in tablePath:
        if not tablePath.endswith("\""):
            ext = tablePath[-3:]
            tablePath = tablePath[:-4]
        else:
            ext = tablePath[-4:-1]
            tablePath = tablePath[1:-5]

    # Será una gráfica que muestre el mbr, los bloques de espacio libre y de las particiones, indicando el porcentaje que ocupa cada una
    dot = Digraph(format=ext, name='Reporte de Disco')
    # Caja que contiene todo el disco
    with dot.subgraph(name='cluster_Disco') as disk:
        disk.attr(label='Disco', rankdir='LR', fontsize='30', fillcolor='gray', style='filled')
        subgraphs = []
        extendida = []

        # Identificar particiones y bloques de espacio libre
        bloques = []
        startDisk = 137
        finishDisk = mbr.mbr_tamano
        left = startDisk
        right = finishDisk
        for i in range(4):
            partition = mbr.getPartitions()[i]
            if partition.part_status != 'N':
                if partition.part_type == 'P':
                    if left == partition.part_start:
                        bloques.append(
                            Bloque(str(round((partition.part_s / (finishDisk - 136)) * 100)) + '%', 'Primaria'))
                        left = partition.part_start + partition.part_s
                    else:
                        bloques.append(
                            Bloque(str(round(((partition.part_start - left) / (finishDisk - 136)) * 100)) + '%', 'Libre'))
                        bloques.append(
                            Bloque(str(round((partition.part_s / (finishDisk - 136)) * 100)) + '%', 'Primaria'))
                        left = partition.part_start + partition.part_s
                if partition.part_type == 'E':
                    extendida = Bloque(tipo='Extendida', size=0)
                    # Crear subbloques con las particiones lógicas
                    ebrs = mbr.getLogicPartitions(diskPath)
                    subbloques = []
                    for ebr in ebrs:
                        if ebr.part_status != 'N':
                            if left == ebr.part_start:
                                subbloques.append(
                                    Bloque(str(round((ebr.part_s / (finishDisk - 136)) * 100)) + '%', 'Lógica'))
                                left = ebr.part_start + ebr.part_s
                            else:
                                subbloques.append(
                                    Bloque(str(round(((ebr.part_start - left) / (finishDisk - 136)) * 100)) + '%',
                                           'Libre'))
                                subbloques.append(
                                    Bloque(str(round((ebr.part_s / (finishDisk - 136)) * 100)) + '%', 'Lógica'))
                                left = ebr.part_start + ebr.part_s
                    if len(subbloques) == 0:
                        # Añadir bloque con toda la extendida vacío
                        subbloques.append(Bloque(str(round((partition.part_s / (finishDisk - 136)) * 100)) + '%', 'Libre'))
                        left = partition.part_start + partition.part_s
                    # Si hay espacio libre al final de la extendida
                    if left != (partition.part_start + partition.part_s):
                        subbloques.append(
                            Bloque(str(round(((extendida.size - left) / (finishDisk - 136)) * 100)) + '%', 'Libre'))
                    extendida.ebr = subbloques
                    bloques.append(extendida)

        # Si hay espacio libre al final del disco
        if left != mbr.mbr_tamano:
            bloques.append(Bloque(str(round(((finishDisk - left) / (finishDisk - 136)) * 100)) + '%', 'Libre'))

        # Crear subgrafos con los bloques.pop
        for i in range(len(bloques)):
            bloque = bloques.pop()
            if bloque.type == 'Libre':
                with disk.subgraph(name='cluster_Libre' + str(i)) as libre:
                    libre.attr(label='Libre', fontsize='20', fillcolor='lightgreen', style='filled')
                    libre.node('libre' + str(i), label=bloque.size, shape='box', fontsize='15', fillcolor='lightgreen',
                               style='filled', color='transparent')
            elif bloque.type == 'Primaria':
                with disk.subgraph(name='cluster_Primaria' + str(i)) as primaria:
                    primaria.attr(label='Primaria', fontsize='20', fillcolor='lightblue', style='filled')
                    primaria.node('primaria' + str(i), label=bloque.size, shape='box', fontsize='15',
                                  fillcolor='lightblue', style='filled', color='transparent')
            elif bloque.type == 'Extendida':
                with disk.subgraph(name='cluster_Extendida') as extendida:
                    extendida.attr(label='Extendida', fontsize='20', fillcolor='lightpink', style='filled')
                # Añadir subbloques con .pop()
                    for j in range(len(bloque.ebr)):
                        subbloque = bloque.ebr.pop()
                        if subbloque.type == 'Libre':
                            with extendida.subgraph(name='cluster_Libre' + str(j)) as libre:
                                libre.attr(label='Libre', fontsize='20', fillcolor='lightgreen', style='filled')
                                libre.node('libre' + str(i) + str(j), label=subbloque.size, shape='box',
                                           fontsize='15', fillcolor='lightgreen', style='filled',
                                           color='transparent')
                        elif subbloque.type == 'Lógica':
                            with extendida.subgraph(name='cluster_Lógica' + str(j)) as logica:
                                logica.attr(label='Lógica', fontsize='20', fillcolor='lightblue', style='filled')
                                logica.node('logica' + str(i) + str(j), label=subbloque.size, shape='box',
                                            fontsize='15', fillcolor='lightblue', style='filled',
                                            color='transparent')


        # Caja que contiene el MBR
        with disk.subgraph(name='cluster_MBR') as mbrbox:
            mbrbox.attr(label='MBR', fontsize='20', fillcolor='lightyellow', style='filled')
            mbrbox.node('mbr', label='', shape='box', fontsize='15', fillcolor='lightyellow', style='filled',
                        color='transparent')

    # ---- CREAR REPORTE ----

    # Verificar si existe directorio y crearlo si no existe
    dir = getDirFromPath(tablePath)
    if os.path.exists(dir) == False:
        os.makedirs(dir)
    # Renderizar dot en table path
    dot.render(tablePath, view=True)
    # Borrar archivos temporales
    os.remove(tablePath)
    return 'Tabla DISK creada exitosamente.'


def getMBRFromDisk(diskPath):
    if not os.path.exists(diskPath):
        return 'Error: No existe el disco.'
    with open(diskPath, "r+b") as file:
        mbr = MBR()
        mbr.decode(file.read(136))
        file.close()
    return mbr


def getDirFromPath(path):
    words = path.split('/')
    dir = ''
    for i in range(len(words) - 1):
        dir += words[i] + '/'
    return dir


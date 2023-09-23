from cmds.structs.MBR import MBR, Partition, EBR, readMBR

EBR = 30
BLOCK = 64
SUPERBLOCK = 89
INODE = 128


def execute(consoleLine):
    id = ''
    type = 'FULL'
    fs = '2FS'

    # Buscar parametros
    for i in range(1, len(consoleLine)):
        if consoleLine[i].startswith("-id="):
            id = consoleLine[i][4:]
            from cmds.mount import isMounted
            if not isMounted(id):
                return 'Error: No existe partición montada con ese id.'
        if consoleLine[i].startswith("-type="):
            type = consoleLine[i][6:].upper()
            if type != 'FULL':
                return 'Error: Type no válido.'
        if consoleLine[i].startswith("-fs="):
            fs = consoleLine[i][4:].upper()
            if fs != '2FS' and fs != '3FS':
                return 'Error: FS no válido.'

    if fs == '2FS':
        return format2FS(id)
    elif fs == '3FS':
        return format2FS(id)  # TODO: Cambiar a 3FS


def format2FS(id):
    # Obtener partición
    from cmds.mount import getMountedPartition
    mountedPart = getMountedPartition(id)
    # Obtener MBR
    mbr = readMBR(mountedPart.path)
    if mbr == None:
        return 'Error: No se pudo leer el disco.'
    # Obtener partición
    partition, type = mbr.getPartitionNamed(mountedPart.name, mountedPart.path)
    if type == 'E':
        return 'Error: No se puede formatear la partición extendida.'
    if partition.part_status == 'F':
        return 'Error: La partición ya fue formateada.'
    # Cálculo de n cantidad de bloques
    print("Calculando cantidad de bloques e inodos...")
    n = float((partition.part_s - SUPERBLOCK) / (INODE + 3 * BLOCK + 4)).__floor__()
    print("Cantidad de Inodos: " + str(n) + "\tCantidad de Bloques: " + str(n * 3))

    # Crear Superbloque
    from cmds.structs.Superbloque import Superbloque
    superblock = Superbloque()
    superblock.s_filesystem_type = 0
    superblock.s_inodes_count = n
    superblock.s_blocks_count = n * 3
    superblock.s_free_blocks_count = n * 3
    superblock.s_free_inodes_count = n
    superblock.s_inode_s = INODE
    superblock.s_block_s = BLOCK
    if mountedPart.type == 'P':
        superblock.s_bm_inode_start = partition.part_start + SUPERBLOCK
    elif mountedPart.type == 'L':
        superblock.s_bm_inode_start = partition.part_start + EBR + SUPERBLOCK
    superblock.s_bm_block_start = superblock.s_bm_inode_start + n
    superblock.s_inode_start = superblock.s_bm_block_start + 3 * n
    superblock.s_block_start = superblock.s_inode_start + n * INODE
    superblock.s_first_ino = superblock.s_inode_start
    superblock.s_first_blo = superblock.s_block_start

    try:
        with open(mountedPart.path, 'rb+') as file:
            if mountedPart.type == 'P':
                file.seek(partition.part_start)
            elif mountedPart.type == 'L':
                file.seek(partition.part_start + EBR)
            file.write(superblock.encode())
            # Crear Bitmap de Inodos
            file.seek(superblock.s_bm_inode_start)
            file.write("0".encode() * n)
            # Crear Bitmap de Bloques
            file.seek(superblock.s_bm_block_start)
            file.write("0".encode() * (3 * n))
            # Crear Inodos
            from cmds.structs.Superbloque import Inode
            inode = Inode()
            for i in range(n):
                file.seek(superblock.s_inode_start + i * INODE)
                file.write(inode.encode())

    except Exception as e:
        print(e)
        return 'Error: No se pudo escribir el Superbloque.'








    return 'Se formateó la partición:  ' + id + ' correctamente.'

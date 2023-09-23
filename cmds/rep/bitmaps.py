from cmds.structs.MBR import getSuperblockByMountedPartition

def makebm_inode(filename, mountedPart):
    try:
        superbloque = getSuperblockByMountedPartition(mountedPart)
        if isinstance(superbloque, str):
            return superbloque
        with open(mountedPart.path, 'rb+') as file:
            file.seek(superbloque.s_bm_inode_start)
            chars = file.read(superbloque.s_inodes_count).decode()
            file.close()
    except:
        return 'Error: No se pudo leer el Bitmap de Inodos.'
    try:
        # Crear archivo de texto imprimiendo los chars en líneas de 20 caracteres
        with open(filename, 'w') as file:
            for i in range(0, len(chars), 20):
                file.write(chars[i:i + 20] + '\n')
            file.close()
    except:
        return 'Error: No se pudo crear el archivo de texto.'

    return 'Bitmap de Inodos creado exitosamente.'


def makebm_block(filename, mountedPart):
    try:
        superbloque = getSuperblockByMountedPartition(mountedPart)
        if isinstance(superbloque, str):
            return superbloque
        with open(mountedPart.path, 'rb+') as file:
            file.seek(superbloque.s_bm_block_start)
            chars = file.read(superbloque.s_blocks_count).decode()
            file.close()
    except:
        return 'Error: No se pudo leer el Bitmap de Bloques.'
    try:
        # Crear archivo de texto imprimiendo los chars en líneas de 20 caracteres
        with open(filename, 'w') as file:
            for i in range(0, len(chars), 20):
                file.write(chars[i:i + 20] + '\n')
            file.close()
    except:
        return 'Error: No se pudo crear el archivo de texto.'

    return 'Bitmap de Bloques creado exitosamente.'

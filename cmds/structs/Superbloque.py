from datetime import datetime


class Superbloque:

    # SIZE = 89
    # filesystem_type-4 |  inodes_count-4 | blocks_count-4 | free_blocks_count-4 | free_inodes_count-4 | mtime-19 | umtime-19 | mnt_count-2 | magic-2 | inode_size-3 | block_size-3 | first_ino-4 | first_blo-4 | bm_inode_start-4 | bm_block_start-4 | inode_start-4 | block_start-4
    # <<<< ----- bytes = 89 ----- >>>>
    def __init__(self):
        self.s_filesystem_type = 0  # int1 0 = 2FS, 1 = 3FS
        self.s_inodes_count = 0 # int4
        self.s_blocks_count = 0 # int4
        self.s_free_blocks_count = 0 # int4
        self.s_free_inodes_count = 0 # int4
        self.s_mtime = "00/00/0000 00:00:00" # char19
        self.s_umtime = "00/00/0000 00:00:00" # char19
        self.s_mnt_count = 0 # int2
        self.s_magic = 61267 # 0xEF53 int2
        self.s_inode_s = 0 #int3
        self.s_block_s = 0 #int3
        self.s_first_ino = 0 #int4
        self.s_first_blo = 0 #int4
        self.s_bm_inode_start = 0 #int4
        self.s_bm_block_start = 0 #int4
        self.s_inode_start = 0 #int4
        self.s_block_start = 0 #int4

    def encode(self):
        bytes = bytearray()
        bytes += self.s_filesystem_type.to_bytes(1, byteorder='big', signed=False)
        bytes += self.s_inodes_count.to_bytes(4, byteorder='big', signed=False)
        bytes += self.s_blocks_count.to_bytes(4, byteorder='big', signed=False)
        bytes += self.s_free_blocks_count.to_bytes(4, byteorder='big', signed=False)
        bytes += self.s_free_inodes_count.to_bytes(4, byteorder='big', signed=False)
        bytes += formatStr(self.s_mtime, 19).encode()
        bytes += formatStr(self.s_umtime, 19).encode()
        bytes += self.s_mnt_count.to_bytes(2, byteorder='big', signed=False)
        bytes += self.s_magic.to_bytes(2, byteorder='big', signed=False)
        bytes += self.s_inode_s.to_bytes(3, byteorder='big', signed=False)
        bytes += self.s_block_s.to_bytes(3, byteorder='big', signed=False)
        bytes += self.s_first_ino.to_bytes(4, byteorder='big', signed=False)
        bytes += self.s_first_blo.to_bytes(4, byteorder='big', signed=False)
        bytes += self.s_bm_inode_start.to_bytes(4, byteorder='big', signed=False)
        bytes += self.s_bm_block_start.to_bytes(4, byteorder='big', signed=False)
        bytes += self.s_inode_start.to_bytes(4, byteorder='big', signed=False)
        bytes += self.s_block_start.to_bytes(4, byteorder='big', signed=False)
        return bytes

    def decode(self, bytes):
        self.s_filesystem_type = int.from_bytes(bytes[0:1], byteorder='big', signed=False)
        self.s_inodes_count = int.from_bytes(bytes[1:5], byteorder='big', signed=False)
        self.s_blocks_count = int.from_bytes(bytes[5:9], byteorder='big', signed=False)
        self.s_free_blocks_count = int.from_bytes(bytes[9:13], byteorder='big', signed=False)
        self.s_free_inodes_count = int.from_bytes(bytes[13:17], byteorder='big', signed=False)
        self.s_mtime = bytes[17:36].decode().replace('\x00', '')
        self.s_umtime = bytes[36:55].decode().replace('\x00', '')
        self.s_mnt_count = int.from_bytes(bytes[55:57], byteorder='big', signed=False)
        self.s_magic = int.from_bytes(bytes[57:59], byteorder='big', signed=False)
        self.s_inode_s = int.from_bytes(bytes[59:62], byteorder='big', signed=False)
        self.s_block_s = int.from_bytes(bytes[62:65], byteorder='big', signed=False)
        self.s_first_ino = int.from_bytes(bytes[65:69], byteorder='big', signed=False)
        self.s_first_blo = int.from_bytes(bytes[69:73], byteorder='big', signed=False)
        self.s_bm_inode_start = int.from_bytes(bytes[73:77], byteorder='big', signed=False)
        self.s_bm_block_start = int.from_bytes(bytes[77:81], byteorder='big', signed=False)
        self.s_inode_start = int.from_bytes(bytes[81:85], byteorder='big', signed=False)
        self.s_block_start = int.from_bytes(bytes[85:89], byteorder='big', signed=False)

    def getN(self):
        return self.s_inodes_count + self.s_free_inodes_count


class Inode:
    #  <<<<<---- SIZE = 128 ---->>>>>
    # i_uid-2 | i_gid-2 | i_size-3 | i_atime-19 | i_ctime-19 | i_mtime-19 | i_block-60 | i_type-1 | i_perm-3
    def __init__(self):
        self.i_uid = 0 # int2
        self.i_gid = 0 # int2
        self.i_s = 0 # int3
        self.i_atime = "00/00/0000 00:00:00" # char19
        self.i_ctime = getTime() # char19
        self.i_mtime = "00/00/0000 00:00:00" # char19
        self.i_block = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]  # int4[15]
        self.i_type = '0'  # char '0' = Carpeta, '1' = Archivo
        self.i_perm = 0  # int3

    def encode(self):
        bytes = bytearray()
        bytes += self.i_uid.to_bytes(2, byteorder='big', signed=False)
        bytes += self.i_gid.to_bytes(2, byteorder='big', signed=False)
        bytes += self.i_s.to_bytes(3, byteorder='big', signed=False)
        bytes += formatStr(self.i_atime, 19).encode()
        bytes += formatStr(self.i_ctime, 19).encode()
        bytes += formatStr(self.i_mtime, 19).encode()
        for pointer in self.i_block:
            bytes += pointer.to_bytes(4, byteorder='big', signed=True)
        bytes += self.i_type.encode()
        bytes += self.i_perm.to_bytes(3, byteorder='big', signed=False)
        return bytes

    def decode(self, bytes):
        self.i_uid = int.from_bytes(bytes[0:2], byteorder='big', signed=False)
        self.i_gid = int.from_bytes(bytes[2:4], byteorder='big', signed=False)
        self.i_s = int.from_bytes(bytes[4:7], byteorder='big', signed=False)
        self.i_atime = bytes[7:26].decode().replace('\x00', '')
        self.i_ctime = bytes[26:45].decode().replace('\x00', '')
        self.i_mtime = bytes[45:64].decode().replace('\x00', '')
        for i in range(15):
            self.i_block[i] = int.from_bytes(bytes[64 + i * 4:64 + (i + 1) * 4], byteorder='big', signed=True)
        self.i_type = bytes[124:125].decode().replace('\x00', '')
        self.i_perm = int.from_bytes(bytes[125:128], byteorder='big', signed=False)


def getTime():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S").rstrip()


def formatStr(string, size):
    if len(string) < size:
        string += (size - len(string)) * '\x00'
    elif len(string) > size:
        string = string[:size]
    return string

import os
import random
import datetime
import graphviz as gv

from cmds.structs.Superbloque import Superbloque

class MBR:  # Size = 136 bytes
    def __init__(self, fit='F', size=0):
        self.mbr_tamano = size
        self.mbr_fecha_creacion = ""
        self.mbr_dsk_signature = random.randint(0, 2147483646)
        self.dsk_fit = fit
        self.mbr_partition_1 = Partition()
        self.mbr_partition_2 = Partition()
        self.mbr_partition_3 = Partition()
        self.mbr_partition_4 = Partition()

    # ------------ STRUCTURE ------------
    # tamano-4 | fecha-19 | signature-4 | fit-1 | 
    # <-- 28 bytes --> | DATA

    # partion_1-27 | partition_2-27 | partition_3-27 | partition_4-27
    # <-- 108 bytes -->

    # TOTAL = 136 bytes

    def encode(self):
        bytes = bytearray()
        bytes += self.mbr_tamano.to_bytes(4, byteorder='big')
        bytes += self.mbr_fecha_creacion.encode()
        bytes += self.mbr_dsk_signature.to_bytes(4, byteorder='big')
        bytes += self.dsk_fit.encode()
        bytes += self.mbr_partition_1.encode()
        bytes += self.mbr_partition_2.encode()
        bytes += self.mbr_partition_3.encode()
        bytes += self.mbr_partition_4.encode()
        return bytes

    def decode(self, bytes):
        self.mbr_tamano = int.from_bytes(bytes[0:4], byteorder='big')
        self.mbr_fecha_creacion = bytes[4:23].decode()
        self.mbr_dsk_signature = int.from_bytes(bytes[23:27], byteorder='big')
        self.dsk_fit = bytes[27:28].decode()
        self.mbr_partition_1.decode(bytes[28:55])
        self.mbr_partition_2.decode(bytes[55:82])
        self.mbr_partition_3.decode(bytes[82:109])
        self.mbr_partition_4.decode(bytes[109:136])

    def setFecha(self):
        # formato = d/m/Y H:M:S y quitar espacios al final
        self.mbr_fecha_creacion = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S").rstrip()

    def setPartition(self, index, partition):
        if index == 0:
            self.mbr_partition_1 = partition
        elif index == 1:
            self.mbr_partition_2 = partition
        elif index == 2:
            self.mbr_partition_3 = partition
        elif index == 3:
            self.mbr_partition_4 = partition

    def createDisk(self, path):
        print('Creando disco en :' + path + '...')
        if path.startswith('\"'):
            path = path[1:-1]
            if os.path.exists(os.path.dirname(path)) == False:
                # Crear directorio
                os.makedirs(os.path.dirname(path))
        else:
            if os.path.exists(os.path.dirname(path)) == False:
                # Crear directorio
                os.makedirs(os.path.dirname(path))
        with open(path, "wb") as file:
            file.write(b'\x00' * self.mbr_tamano)
            file.close()
        self.setFecha()
        self.updateDisk(path)
        print("Disco creado exitosamente.")

    def updateDisk(self, path):
        with open(path, "r+b") as file:
            file.write(self.encode())
            file.close()
        print("MBR actualizado en el disco.")

    def getPartitions(self):
        return [self.mbr_partition_1, self.mbr_partition_2, self.mbr_partition_3, self.mbr_partition_4]

    def getPartitionNamed(self, name, path):
        partitions = self.getPartitions()
        for partition in partitions:
            if partition.part_name == name:
                if partition.part_type == 'E':
                    return None, 'E'
                return partition, 'P'
        if self.hasExtendedPartition():
            partitions = self.getLogicPartitions(path)
            for partition in partitions:
                if partition.part_name == name:
                    return partition, 'L'
        return None

    def getLogicPartitions(self, path):
        partitions = []
        partition = self.getExtendedPartition()
        with open(path, 'r+b') as file:
            file.seek(partition.part_start)
            while True:
                ebr = EBR()
                ebr.decode(file.read(30))
                partitions.append(ebr)
                if ebr.part_next == -1:
                    break
                file.seek(ebr.part_next)
            file.close()
        return partitions
    # FDISK FUNCTIONS

    def getPartitionIndexForFF(self, size):
        for i in range(4):
            partition = self.getPartitions()[i]
            if partition.part_status == 'N' and self.partitionSizeIsCorrect(i, size):
                return i
        return -1

    def getStartForFF(self, indexPartition):
        if indexPartition == 0:
            return 137
        else:
            return self.getPartitions()[indexPartition - 1].part_start + self.getPartitions()[indexPartition - 1].part_s

    def partitionSizeIsCorrect(self, partIndex,
                               size):  # Validates if the size is correct for a new partition and if there is enough space between partitions
        if partIndex == 0:
            # Encontrar tope izquierdo y derecho del espacio libre
            left = 137
            right = self.mbr_tamano
            for i in range(1, 4):
                partition = self.getPartitions()[i]
                if partition.part_status == 'N':
                    continue
                right = partition.part_start
                break
            # Validar que el tamaño sea correcto
            if size > (right - left) or (left + size) > self.mbr_tamano:
                return False
            return True
        else:
            # Encontrar tope izquierdo y derecho del espacio libre
            left = self.getPartitions()[partIndex - 1].part_start + self.getPartitions()[partIndex - 1].part_s
            right = self.mbr_tamano
            for i in range(partIndex + 1, 4):
                partition = self.getPartitions()[i]
                if partition.part_status == 'N':
                    continue
                right = partition.part_start
                break
            # Validar que el tamaño sea correcto
            if size > (right - left) or (left + size) > self.mbr_tamano:
                return False
            return True

    # VALIDACIONES
    def hasExtendedPartition(self):
        for partition in self.getPartitions():
            if partition.part_type == 'E':
                return True
        return False

    def hasFreePrimaryPartition(self):
        for partition in self.getPartitions():
            if partition.part_status == 'N':
                return True
        return False

    def hasPartitionNamed(self, name, path):
        partitions = self.getPartitions()
        if self.hasExtendedPartition():
            partitions += self.getLogicPartitions(path)
        for partition in partitions:
            if partition.part_name == name:
                return True
        return False

    def hasFreeLogicalPartition(self, path):
        return len(self.getLogicPartitions(path)) < 6

    # ==================== EXTENDED PARTITION ====================

    def getExtendedPartition(self):
        for partition in self.getPartitions():
            if partition.part_type == 'E':
                return partition
        return None

    def addFirstEBR(self, path):
        try:
            extPart = self.getExtendedPartition()
            with open(path, 'r+b') as file:
                file.seek(extPart.part_start)
                ebr = EBR()
                file.write(ebr.encode())
                file.close()
        except Exception as e:
            print(e)

    def addLogicFirstFit(self, path, size, name, fit):
        extended = self.getExtendedPartition()
        ebrs = self.getLogicPartitions(path)
        right = extended.part_start + extended.part_s
        left = extended.part_start
        for i in range(len(ebrs)):
            # Primer EBR
            if i == 0:
                if ebrs[i].part_status == 'N':
                    if size < (right - (left + 30)):
                        # Modificar EBR
                        ebrs[i].part_status = 'A'
                        ebrs[i].part_fit = fit
                        ebrs[i].part_s = size
                        ebrs[i].part_name = name
                        ebrs[i].part_start = left
                        self.updateEBRS(path, ebrs)
                        return 'Partición creada exitosamente.'
                    else:
                        return 'Error: No hay espacio suficiente para crear la partición.'
                left = ebrs[i].part_start + ebrs[i].part_s
            if ebrs[i].part_next != -1:
                continue
            else:
                if size < (right - (left + 30)):
                    #Crear EBR
                    ebr = EBR(status='N', fit=fit, start=left, size=size, next=-1, name=name)
                    ebrs[i].part_next = ebr.part_start
                    ebrs.append(ebr)
                    self.updateEBRS(path, ebrs)
                    return 'Partición creada exitosamente.'
                else:
                    return 'Error: No hay espacio suficiente para crear la partición.'

    def updateEBRS(self, path, ebrs):
        with open(path, 'r+b') as file:
            for i in range(len(ebrs)):
                file.seek(ebrs[i].part_start)
                print('Posición: ' + str(ebrs[i].part_start))
                file.write(ebrs[i].encode())
            file.close()




    # ======================= Graphviz =========================
    def getGraph(self, extension='png', path=''):
        # Encabezado MBR
        dot = gv.Digraph(format=extension, name='MBR')
        with dot.subgraph(name='cluster_encabezadoMBR') as b1:
            b1.attr(label='MBR', fontsize='30', fillcolor='lightyellow', style='filled')
            b1.node_attr.update(shape='box', style='filled', fillcolor='lightgray', width='3', height='1')
            txt = 'Tamaño: ' + str(self.mbr_tamano) + '\n' + 'Fecha Creación: ' + self.mbr_fecha_creacion + '\n'
            txt += 'Signature: ' + str(self.mbr_dsk_signature) + '\n' + 'Fit: ' + self.dsk_fit
            b1.node('B1', label=txt)
        numlogicPart=0
        # Obtener subgrafos de particiones
        for i in range(len(self.getPartitions())):
            partition = self.getPartitions()[i]
            nameSubGraph = 'cluster_part' + str(i)
            if partition.part_type == 'P':
                with dot.subgraph(name=nameSubGraph) as b:
                    b.attr(label='Partición Primaria', fontsize='20', fillcolor='lightblue', style='filled')
                    b.node_attr.update(shape='box', style='filled', fillcolor='lightgray', width='3', height='1')
                    txt = 'Status: ' + partition.part_status + '\n' + 'Type: ' + partition.part_type + '\n'
                    txt += 'Fit: ' + partition.part_fit + '\n' + 'Start: ' + str(partition.part_start) + '\n'
                    txt += 'Size: ' + str(partition.part_s) + '\n' + 'Name: ' + partition.part_name
                    b.node(nameSubGraph, label=txt)
            elif partition.part_type == 'E':
                with dot.subgraph(name=nameSubGraph) as b:
                    b.attr(label='Partición Extendida', fontsize='20', fillcolor='blue', style='filled', fontcolor='white')
                    b.node_attr.update(shape='box', style='filled', fillcolor='lightgray', width='3', height='1')
                    txt = 'Status: ' + partition.part_status + '\n' + 'Type: ' + partition.part_type + '\n'
                    txt += 'Fit: ' + partition.part_fit + '\n' + 'Start: ' + str(partition.part_start) + '\n'
                    txt += 'Size: ' + str(partition.part_s) + '\n' + 'Name: ' + partition.part_name
                    b.node(nameSubGraph, label=txt)

                # Obtener subgrafos de EBRs

                for ebr in self.getLogicPartitions(path):
                    namesubgraph2 = 'cluster_ebr' + str(numlogicPart)
                    with dot.subgraph(name=namesubgraph2) as e:
                        e.attr(label='Partición Lógica', fontsize='20', fillcolor='darkgreen', style='filled', fontcolor='white')
                        e.node_attr.update(shape='box', style='filled', fillcolor='lightgray', width='2', height='1')
                        txt = 'Status: ' + ebr.part_status + '\n' + 'Fit: ' + ebr.part_fit + '\n'
                        txt += 'Start: ' + str(ebr.part_start) + '\n' + 'Size: ' + str(ebr.part_s) + '\n'
                        txt += 'Next: ' + str(ebr.part_next) + '\n' + 'Name: ' + ebr.part_name
                        e.node(namesubgraph2, label=txt)
                    numlogicPart += 1

        # Enlaces
        lastSubgraph = 'B1'
        for i in range(4):
            if self.getPartitions()[i].part_type == 'P':
                dot.edge(lastSubgraph, 'cluster_part' + str(i), style='invis')
                lastSubgraph = 'cluster_part' + str(i)
            elif self.getPartitions()[i].part_type == 'E':
                dot.edge(lastSubgraph, 'cluster_part'+str(i), style='invis')
                lastSubgraph = 'cluster_part'+str(i)
                for j in range(numlogicPart):
                    dot.edge(lastSubgraph, 'cluster_ebr'+str(j), style='invis')
                    lastSubgraph = 'cluster_ebr'+str(j)

        dot.attr(ranksep='0.1')

        return dot


class Partition:  # Size = 27 bytes
    def __init__(self, status='N', type='P', fit='F', start=-1, size=0, name=''):
        self.part_status = status  # Char
        self.part_type = type  # Char P o E
        self.part_fit = fit  # Char B, F o W
        self.part_start = start  # Int4 signed
        self.part_s = size  # Int4
        self.part_name = formatStr(name, 16)

    # ------------ STRUCTURE ------------
    # status-1 | type-1 | fit-1 | start-4 | size-4 | name-16
    # <-- 27 bytes -->

    def encode(self):
        bytes = bytearray()
        bytes += self.part_status.encode()
        bytes += self.part_type.encode()
        bytes += self.part_fit.encode()
        bytes += self.part_start.to_bytes(4, byteorder='big', signed=True)
        bytes += self.part_s.to_bytes(4, byteorder='big')
        bytes += formatStr(self.part_name, 16).encode()
        return bytes

    def decode(self, bytes):
        self.part_status = bytes[0:1].decode()
        self.part_type = bytes[1:2].decode()
        self.part_fit = bytes[2:3].decode()
        self.part_start = int.from_bytes(bytes[3:7], byteorder='big', signed=True)
        self.part_s = int.from_bytes(bytes[7:11], byteorder='big')
        self.part_name = bytes[11:27].decode().replace('\x00', '')


def formatStr(string, size):
    if len(string) < size:
        string += (size - len(string)) * '\x00'
    elif len(string) > size:
        string = string[:size]
    return string


class EBR:

    # ESTRUCTURA
    # status-1 | fit-1 | start-4 | size-4 | next-4 | name-16
    # <-- 30 bytes -->

    def __init__(self, status='N', fit='F', start=0, size=0, next=-1, name=''):
        self.part_status = status  # Char
        self.part_fit = fit  # Char B, F o W
        self.part_start = start  # Int4 signed
        self.part_s = size  # Int4
        self.part_next = next  # Int4
        self.part_name = formatStr(name, 16)

    def encode(self):
        bytes = bytearray()
        bytes += self.part_status.encode()
        bytes += self.part_fit.encode()
        bytes += self.part_start.to_bytes(4, byteorder='big')
        bytes += self.part_s.to_bytes(4, byteorder='big')
        bytes += self.part_next.to_bytes(4, byteorder='big', signed=True)
        bytes += formatStr(self.part_name, 16).encode()
        return bytes

    def decode(self, bytes):
        self.part_status = bytes[0:1].decode()
        self.part_fit = bytes[1:2].decode()
        self.part_start = int.from_bytes(bytes[2:6], byteorder='big')
        self.part_s = int.from_bytes(bytes[6:10], byteorder='big')
        self.part_next = int.from_bytes(bytes[10:14], byteorder='big', signed=True)
        self.part_name = bytes[14:30].decode().replace('\x00', '')

def readMBR(path):
    try:
        with open(path, 'rb') as file:
            mbr = MBR()
            mbr.decode(file.read(136))
            file.close()
            return mbr
    except:
        return None

def getSuperblockByMountedPartition(mountedPart):
    mbr = readMBR(mountedPart.path)
    part, type = mbr.getPartitionNamed(mountedPart.name, mountedPart.path)
    if type == 'E':
        return 'Error: No se puede generar gráfico en partición extendida.'
    try:
        with open(mountedPart.path, 'rb+') as file:
            if type == 'P':
                file.seek(part.part_start)
            elif type == 'L':
                file.seek(part.part_start + EBR)
            from cmds.mkfs import SUPERBLOCK
            bytes = file.read(SUPERBLOCK)
            superbloque = Superbloque()
            superbloque.decode(bytes)
            file.close()
        return superbloque
    except:
        return 'Error: No se pudo leer el Superbloque.'

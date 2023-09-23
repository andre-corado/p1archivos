class Content: # 16 bytes
    def __init__(self):
        self.b_name = ""  # Char[12]
        self.b_inodo = 0  # int4 unsigned

    def encode(self):
        bytes = bytearray()
        bytes += formatStr(self.b_name, 12).encode()
        bytes += self.b_inodo.to_bytes(4, byteorder='big', signed=False)
        return bytes

    def decode(self, bytes):
        self.b_name = bytes[:12].decode().replace('\x00', '')
        self.b_inodo = int.from_bytes(bytes[12:16], byteorder='big', signed=False)


class DirBlock: # 64 bytes
    def __init__(self):
        # Content[4]
        self.b_Content = [Content(), Content(), Content(), Content()]

    def encode(self):
        bytes = bytearray()
        for Content in self.b_Content:
            bytes += Content.encode()
        return bytes

    def decode(self, bytes):
        for i in range(4):
            self.b_Content[i].decode(bytes[i * 16:(i + 1) * 16])


class FileBlock: # 64 bytes
    def __init__(self):
        self.b_Content = ""  # char[64]

    def encode(self):
        bytes = bytearray()
        bytes += formatStr(self.b_Content, 64).encode()
        return bytes

    def decode(self, bytes):
        self.b_Content = bytes.decode().replace('\x00', '')


class PointerBlock: # 64 bytes
    def __init__(self):
        # int4[16]
        self.b_pointers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def encode(self):
        bytes = bytearray()
        for pointer in self.b_pointers:
            bytes += pointer.to_bytes(4, byteorder='big', signed=False)
        return bytes


def formatStr(string, size):
    if len(string) < size:
        string += (size - len(string)) * '\x00'
    elif len(string) > size:
        string = string[:size]
    return string

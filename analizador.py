from cmds import mkdisk, fdisk, rmdisk, mount, mkfs  # Importar módulo de comandos
from cmds.rep import rep
import os
# Diccionario de particiones montadas   id -> MountedPartition
mountedPartitions = {}


def split_Command(inputTxt):  # ANALIZADOR LÉXICO EN TEORÍA

    words = inputTxt.split(" ")
    words2 = []

    for i in range(len(words)):  # Se analiza cada palabra

        # ------------- COMILLAS DOBLES -------------
        if words[i].endswith("\""):
            continue
        if words[i].startswith("-path=\"") or words[i].startswith("-id=\""):
         # Se busca la palabra con las siguientes comillas
            for j in range(i + 1, len(words)):
                words[i] = words[i] + " " + words[j]
                if words[j].endswith("\""):
                    # Se concatena la palabra con las comillas
                    words2.append(words[i])
                    break
                # Si no se encontró la palabra con las comillas se retorna error
                return "Error: No se encontró el cierre de comillas"

        else:  # SE REALIZA LOWERCASE A LAS PALABRAS, EXCEPTO LO QUE ESTE DESPUES DE UN =
            if "=" not in words[i]:
                words[i] = words[i].lower()
                words2.append(words[i])
            else:
                # SOLO DAR LOWER A LO QUE ESTE ANTES DE UN =
                temp = words[i][:words[i].find("=")].lower() + words[i][words[i].find("="):]
                # Si es param path
                if temp.startswith("-path=") or temp.startswith("-id="):
                    # Si contiene /user/
                    if temp.find("/user/") != -1:
                        # Averiguar usuario actual por terminal con whoami
                        user = os.popen("whoami").read()
                        # Sustituir /user/ por /home/user/
                        temp = temp.replace("/user/", "/" + user[:-1] + "/")
                words2.append(temp)

    return analizar_Comando(words2);


def analizar_Comando(consoleLine):
    print(consoleLine) # PARA VER COMO LLEGAN LAS PALABRAS
    # ------------- COMANDO EXECUTE -------------
    if consoleLine[0] == "execute":
        # Si contiene -path= y tiene un path válido
        if consoleLine[1].startswith("-path=") and len(consoleLine[1]) > 6:
            # Obtener path
            path = consoleLine[1][6:]
            # tratar de leer el archivo y obtener String
            try:
                file = open(path, "r")
                text = file.read()
                file.close()
            except:
                return "Error: No se pudo leer el archivo"
            # Separar líneas
            lines = text.split("\n")
            # Analizar cada línea
            for line in lines:
                if line.startswith("#"):
                    print('\n############################\n'+line+'\n############################\n')
                    continue
                print(split_Command(line))
        return "Comando execute ejecutado."

    # ===========================================================
    # ================ ADMINISTRACIÓN DE DISCOS =================
    # ===========================================================
    # ------------- COMANDO MKDISK -------------
    elif consoleLine[0] == "mkdisk":
        sizeFound, pathFound = False, False
        for i in range(1, len(consoleLine)):
            if consoleLine[i].startswith("-size="):
                sizeFound = True
            elif consoleLine[i].startswith("-path="):
                pathFound = True
        if not sizeFound or not pathFound:
            return "Error: Faltan parámetros obligatorios"
        return mkdisk.execute(consoleLine)

    # ------------- COMANDO FDISK -------------
    elif consoleLine[0] == "fdisk":
        pathFound, nameFound = False, False
        for i in range(1, len(consoleLine)):
            if consoleLine[i].startswith("-path="):
                pathFound = True
            elif consoleLine[i].startswith("-name="):
                nameFound = True
        if not pathFound or not nameFound:
            return "Error: Faltan parámetros obligatorios"
        return fdisk.execute(consoleLine)

        # ------------- COMANDO RMDISK -------------
    elif consoleLine[0] == "rmdisk":
        if consoleLine[1].startswith("-path=") and len(consoleLine[1]) > 10:
            return rmdisk.execute(consoleLine)
        return "Error: Faltan parámetros obligatorios"

    # ------------- COMANDO FDISK -------------
    elif consoleLine[0] == "fdisk":
        pathFound, nameFound = False, False
        for i in range(1, len(consoleLine)):
            if consoleLine[i].startswith("-path="):
                pathFound = True
            elif consoleLine[i].startswith("-name="):
                nameFound = True
        if not pathFound or not nameFound:
            return "Error: Faltan parámetros obligatorios"
        return fdisk.execute(consoleLine)

    # ------------- COMANDO MOUNT -------------
    elif consoleLine[0] == "mount":
        pathFound, nameFound = False, False
        for i in range(1, len(consoleLine)):
            if consoleLine[i].startswith("-path="):
                pathFound = True
            elif consoleLine[i].startswith("-name="):
                nameFound = True
        if not pathFound or not nameFound:
            return "Error: Faltan parámetros obligatorios"
        return mount.execute(consoleLine)


    # ------------- COMANDO UNMOUNT -------------
    elif consoleLine[0] == "unmount":
        if not consoleLine[1].startswith("-id="):
            return "Error: Faltan parámetros obligatorios"
        id = consoleLine[1][4:]
        if id in mountedPartitions:
            del mountedPartitions[id]
            return "Partición desmontada."
        return "Error: No existe la partición con ese id."

    # ------------- COMANDO MKFS -------------
    elif consoleLine[0] == "mkfs":
        for i in range(len(consoleLine)):
            if consoleLine[i].startswith("-id="):
                return mkfs.execute(consoleLine)
        return "Eror: Faltan parámetros obligatorios"
    # ===========================================================
    # =========== ADMINISTRACIÓN DE USUARIOS Y GRUPOS ===========
    # ===========================================================

    # ------------- COMANDO LOGIN -------------
    elif consoleLine[0] == "login":
        if "-user=" not in consoleLine or "-pass=" not in consoleLine or "-id=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.login.execute(consoleLine)

    # ------------- COMANDO LOGOUT -------------
    elif consoleLine[0] == "logout":
        # return c.logout.execute(consoleLine)
        return
    # ------------- COMANDO MKGRP -------------
    elif consoleLine[0] == "mkgrp":
        if "-name=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.mkgrp.execute(consoleLine)
    # ------------- COMANDO RMGRP -------------
    elif consoleLine[0] == "rmgrp":
        if "-name=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.rmgrp.execute(consoleLine)
    # ------------- COMANDO MKUSR -------------
    elif consoleLine[0] == "mkusr":
        if "-user=" not in consoleLine or "-pwd=" not in consoleLine or "-grp=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.mkusr.execute(consoleLine)
    # ------------- COMANDO RMUSR -------------
    elif consoleLine[0] == "rmusr":
        if "-user=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.rmusr.execute(consoleLine)

    # ===========================================================
    # ======= ADMINISTRACIÓN DE CARPETAS Y ARCHIVOS =============
    # ===========================================================

    # ------------- COMANDO MKFILE -------------
    elif consoleLine[0] == "mkfile":
        if "-path=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.mkfile.execute(consoleLine)
    # ------------- COMANDO CAT -------------
    elif consoleLine[0] == "cat":
        if "-fileN=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.cat.execute(consoleLine)
    # ------------- COMANDO REMOVE -------------
    elif consoleLine[0] == "remove":
        if "-path=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.remove.execute(consoleLine)
    # ------------- COMANDO EDIT -------------
    elif consoleLine[0] == "edit":
        if "-path=" not in consoleLine or "-cont=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.edit.execute(consoleLine)
    # ------------- COMANDO RENAME -------------
    elif consoleLine[0] == "rename":
        if "-path=" not in consoleLine or "-name=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.rename.execute(consoleLine)
    # ------------- COMANDO MKDIR -------------
    elif consoleLine[0] == "mkdir":
        if "-path=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.mkdir.execute(consoleLine)
    # ------------- COMANDO COPY -------------
    elif consoleLine[0] == "copy":
        if "-path=" not in consoleLine or "-destino=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.copy.execute(consoleLine)
    # ------------- COMANDO MOVE -------------
    elif consoleLine[0] == "move":
        if "-path=" not in consoleLine or "-destino=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.move.execute(consoleLine)
    # ------------- COMANDO FIND -------------
    elif consoleLine[0] == "find":
        if "-path=" not in consoleLine or "-name=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.find.execute(consoleLine)
    # ------------- COMANDO CHOWN -------------
    elif consoleLine[0] == "chown":
        if "-path=" not in consoleLine or "-user=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.chown.execute(consoleLine)
    # ------------- COMANDO CHGRP -------------
    elif consoleLine[0] == "chgrp":
        if "-user=" not in consoleLine or "-grp=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.chgrp.execute(consoleLine)
    # ------------- COMANDO CHMOD -------------
    elif consoleLine[0] == "chmod":
        if "-path=" not in consoleLine or "-ugo=" not in consoleLine:
            return "Error: Faltan parámetros obligatorios"
        # return c.chmod.execute(consoleLine)
    # ------------- COMANDO PAUSE -------------
    elif consoleLine[0] == "pause":
        # return c.pause.execute(consoleLine)
        return

    # ===========================================================
    # ==================== REPORTE DE DATOS =====================
    # ===========================================================

    # ------------- COMANDO REP -------------
    elif consoleLine[0] == "rep":
        nameFound, pathFound, idFound = False, False, False
        for i in range(1, len(consoleLine)):
            if consoleLine[i].startswith("-name="):
                nameFound = True
            elif consoleLine[i].startswith("-path="):
                pathFound = True
            elif consoleLine[i].startswith("-id="):
                idFound = True
        if not nameFound or not pathFound or not idFound:
            return "Error: Faltan parámetros obligatorios"
        return rep.execute(consoleLine)

    # ------------- COMANDO EXIT -------------
    elif consoleLine[0] == "exit":
        return "Comando exit reconocido."

    # ------------ COMANDO SHOW PARTS ------------
    elif consoleLine[0] == "show":
        if 'parts' in consoleLine:
            if mountedPartitions == {}:
                return "No hay particiones montadas."
            # Imprimir diccionario de particiones montadas
            print("\n ________ Particiones montadas: ________")
            for key in mountedPartitions:
                print("id: " + key)
                print('________________________________________')
            return ""
        return "Comando no reconocido"

    # ------------- COMANDO NO RECONOCIDO -------------
    elif consoleLine[0] == '':
        return ""
    return "Comando no reconocido"


class mountedPartition:
    def __init__(self, path, name, type):
        self.path = path
        self.name = name
        self.type = type

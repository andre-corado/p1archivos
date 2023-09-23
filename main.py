from analizador import split_Command

if __name__ == '__main__':
    # Simular consola de comandos y pedir al usuario que ingrese un comando
    # para ejecutar la acción correspondiente
    while True:
        print("> ", end="")
        console = input()
        try:
            print(split_Command(console)+"\n")
        except Exception as e:
            print('Error: Falta parámetro obligatorio.')
            print(e)

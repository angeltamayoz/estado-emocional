try:
    from .utils import registrar_usuario, mostrar_usuarios, realizar_encuesta_emocional
except Exception:
    from utils import registrar_usuario, mostrar_usuarios, realizar_encuesta_emocional


def main():
    while True:
        print("1. Registrar nuevo usuario")
        print("2. Ver usuarios registrados")
        print("3. Realizar encuesta emocional")
        print("4. Salir")
        
        opcion = input("Selecciona una opción: ")
        
        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            mostrar_usuarios()
        elif opcion == "3":
            realizar_encuesta_emocional()
        elif opcion == "4":
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida. Intenta de nuevo.\n")

if __name__ == "__main__":
    main()

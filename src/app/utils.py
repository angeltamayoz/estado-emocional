# utils.py

usuarios = {}  # Diccionario para almacenar usuarios

def registrar_usuario():
    print("=== Registro de Usuario ===")
    username = input("Ingresa un nombre de usuario: ")
    
    if username in usuarios:
        print("❌ El nombre de usuario ya existe. Intenta con otro.")
        return
    
    password = input("Ingresa una contraseña: ")
    confirm_password = input("Confirma tu contraseña: ")
    
    if password != confirm_password:
        print("❌ Las contraseñas no coinciden.")
        return
    
    usuarios[username] = password
    print(f"✅ Usuario '{username}' registrado exitosamente.\n")

def mostrar_usuarios():
    print("=== Lista de Usuarios Registrados ===")
    for username in usuarios:
        print(f"- {username}")
    print()

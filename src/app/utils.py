import csv
from typing import List, Dict

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

def read_csv(file_path: str) -> List[Dict[str, str]]:
    """
    Reads a CSV file and returns a list of dictionaries.

    :param file_path: Path to the CSV file.
    :return: List of rows as dictionaries.
    """
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

def write_csv(file_path: str, data: List[Dict[str, str]], fieldnames: List[str]) -> None:
    """
    Writes a list of dictionaries to a CSV file.

    :param file_path: Path to the CSV file.
    :param data: List of rows as dictionaries.
    :param fieldnames: List of field names (keys) for the CSV file.
    """
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

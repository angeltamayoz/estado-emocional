# Import robusto para modelos: prueba relativa y luego absoluta
try:
    from .models import EMOTIONAL_QUESTIONS, EmotionalSurvey
except Exception:
    from models import EMOTIONAL_QUESTIONS, EmotionalSurvey

import os
import csv
from typing import List, Dict

# Helpers CSV
def read_csv(file_path: str) -> List[Dict[str, str]]:
    if not os.path.exists(file_path):
        return []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

def write_csv(file_path: str, data: List[Dict[str, str]], fieldnames: List[str]) -> None:
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

usuarios = {}  # Diccionario para almacenar usuarios

# Realizar encuesta emocional por consola y guardar en CSV
def realizar_encuesta_emocional():
    print("=== Encuesta de Estado Emocional ===")
    username = input("Ingresa tu nombre de usuario: ")
    if username not in usuarios:
        print("❌ Usuario no registrado. Regístrate primero.")
        return
    answers = []
    for q in EMOTIONAL_QUESTIONS:
        ans = input(q + " ")
        answers.append(ans)
    encuesta = EmotionalSurvey(username, answers)
    # Guardar en encuestas.csv
    fieldnames = ['username'] + [f"q{i+1}" for i in range(len(EMOTIONAL_QUESTIONS))]
    answers_dict = {f"q{i+1}": v for i, v in enumerate(answers)}
    row = {"username": username, **answers_dict}
    file_path = 'encuestas.csv'
    existing_data = read_csv(file_path)
    existing_data.append(row)
    write_csv(file_path, existing_data, fieldnames)
    print("✅ Encuesta registrada exitosamente.\n")


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

# Modelo de encuesta emocional y relación con usuario
from typing import Dict, List

class EmotionalSurvey:
	def __init__(self, username: str, answers: Dict[str, str]):
		self.username = username
		self.answers = answers

	def to_dict(self):
		return {"username": self.username, **self.answers}

# Preguntas fijas de la encuesta
EMOTIONAL_QUESTIONS = [
	"¿Cómo te sientes hoy? (Feliz, Triste, Ansioso, Enojado, Otro)",
	"¿Qué tan estresado te sientes? (Nada, Poco, Moderado, Mucho)",
	"¿Dormiste bien anoche? (Sí, No)",
	"¿Te gustaría hablar con alguien sobre tus emociones? (Sí, No)"
]

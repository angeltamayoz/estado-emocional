#!/usr/bin/env python3
"""
Punto de entrada principal para EmoTrack (control de emociones)
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Iniciando EmoTrack...")
    print("📍 La aplicación estará disponible en: http://localhost:8000")
    print("📖 Documentación interactiva en: http://localhost:8000/docs")
    print("🔧 Para detener la aplicación: Ctrl+C")
    
    uvicorn.run(
        "app.api:app",  # String de importación en lugar del objeto
        host="0.0.0.0", 
        port=8000,
        reload=True,  # Recarga automática en desarrollo
        log_level="info"
    )
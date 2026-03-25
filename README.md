# backend-2026

Lancer le projet 
Depuis le dossier karibmarket-api/ :                                                                                                                             
  # 1. Activer l'environnement virtuel                                                                                                                     
  source .venv/bin/activate                                                                                                                                
                                                                                                                                                           
  # 2. Installer les dépendances (si pas encore fait)                                                                                                      
  pip install -r requirements.txt                                                                                                                          
                  
  # 3. Lancer le serveur
  uvicorn app.main:app --reload

  L'API sera disponible sur :
  - http://localhost:8000/docs — Swagger UI
  - http://localhost:8000/redoc — ReDoc

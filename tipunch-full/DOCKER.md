# Lancer Ti Punch avec Docker

Depuis ce dossier :

```powershell
cd C:\Users\ville\Downloads\backend-2026\backend-2026\tipunch-full
docker compose up --build
```

Frontend :

```text
http://localhost:3016/
```

API FastAPI :

```text
http://localhost:8016/docs
```

Arreter les conteneurs :

```powershell
docker compose down
```

Si les ports `3016` ou `8016` sont deja occupes par un lancement manuel Python, arrete d'abord ces processus ou ferme les terminaux correspondants.

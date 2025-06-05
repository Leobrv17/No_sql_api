# Forms API - Backend FastAPI

Backend pour un service de création de formulaires en ligne inspiré de Google Forms.

## 🚀 Fonctionnalités

- **Authentification JWT** : Inscription et connexion sécurisées
- **Gestion des formulaires** : CRUD complet pour créer et gérer des formulaires
- **Types de questions variés** : 
  - Texte court/long
  - Choix multiple/Cases à cocher/Liste déroulante
  - Nombre/Date/Email
- **Collecte de réponses** : Soumission anonyme ou authentifiée
- **API RESTful** : Documentation automatique avec Swagger/ReDoc

## 📋 Prérequis

- Docker et Docker Compose
- Python 3.11+ (pour développement local)
- MongoDB 7.0+

## 🛠️ Installation

### Avec Docker (Recommandé)

1. Cloner le repository
```bash
git clone <repo-url>
cd forms-api
```

2. Copier le fichier d'environnement
```bash
cp .env.example .env
# Modifier les variables selon vos besoins
```

3. Lancer avec Docker Compose
```bash
docker-compose up -d
```

L'API sera disponible sur `http://localhost:8000`

### Sans Docker

1. Installer les dépendances
```bash
pip install -r requirements.txt
```

2. Configurer MongoDB localement

3. Lancer l'application
```bash
uvicorn app.main:app --reload
```

## 📚 Documentation API

- **Swagger UI** : `http://localhost:8000/api/docs`
- **ReDoc** : `http://localhost:8000/api/redoc`

### Endpoints principaux

#### Authentification
- `POST /api/v1/auth/register` : Inscription
- `POST /api/v1/auth/login` : Connexion (retourne JWT)

#### Formulaires
- `GET /api/v1/forms` : Liste des formulaires de l'utilisateur
- `POST /api/v1/forms` : Créer un formulaire
- `GET /api/v1/forms/{id}` : Détails d'un formulaire
- `PATCH /api/v1/forms/{id}` : Mettre à jour
- `DELETE /api/v1/forms/{id}` : Supprimer

#### Questions
- `POST /api/v1/forms/{id}/questions` : Ajouter une question
- `PATCH /api/v1/forms/{id}/questions/{qid}` : Modifier
- `DELETE /api/v1/forms/{id}/questions/{qid}` : Supprimer

#### Réponses
- `POST /api/v1/forms/{id}/submit` : Soumettre des réponses
- `GET /api/v1/forms/{id}/responses` : Voir les réponses
- `GET /api/v1/forms/{id}/stats` : Statistiques

## 🏗️ Architecture

```
app/
├── models/        # Modèles Beanie (ODM MongoDB)
├── schemas/       # Schémas Pydantic (validation)
├── routers/       # Routes FastAPI
├── services/      # Logique métier
├── utils/         # Utilitaires (auth, sécurité)
└── exceptions/    # Exceptions personnalisées
```

### Principes de code

- **Fonctions courtes** : Maximum 25-30 lignes
- **Séparation des responsabilités** : Routes → Services → Models
- **Validation stricte** : Pydantic pour toutes les entrées/sorties
- **Gestion d'erreurs** : Exceptions HTTP personnalisées
- **Documentation** : Commentaires explicites pour chaque fonction

## 🔒 Sécurité

- Mots de passe hashés avec bcrypt
- Authentification JWT
- Validation des permissions
- Protection CORS configurée

## 🧪 Tests

```bash
# Lancer les tests
pytest

# Avec couverture
pytest --cov=app
```

## 📦 Services Docker

- **api** : Backend FastAPI (port 8000)
- **mongodb** : Base de données (port 27017)
- **mongo-express** : Interface MongoDB (port 8081)

## 🔧 Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `MONGODB_URL` | URL de connexion MongoDB | `mongodb://localhost:27017` |
| `SECRET_KEY` | Clé secrète JWT | À changer en production |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Durée de vie du token | `30` |
| `CORS_ORIGINS` | Origines CORS autorisées | `["http://localhost:3000"]` |
| `DEBUG` | Mode debug | `False` |

## 🚀 Déploiement

### Production avec Docker

1. Modifier le `.env` avec des valeurs sécurisées
2. Construire l'image optimisée :
```bash
docker build -t forms-api:prod .
```

3. Utiliser docker-compose pour la production :
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Recommandations de sécurité

- Changer `SECRET_KEY` avec une valeur aléatoire forte
- Utiliser HTTPS en production
- Configurer un reverse proxy (Nginx/Traefik)
- Limiter les CORS aux domaines autorisés
- Activer l'authentification MongoDB

## 📝 Exemples d'utilisation

### 1. Inscription d'un utilisateur

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

### 2. Connexion et récupération du token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=securepassword123"
```

### 3. Créer un formulaire

```bash
curl -X POST http://localhost:8000/api/v1/forms \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Enquête de satisfaction",
    "description": "Aidez-nous à améliorer nos services",
    "accepts_responses": true
  }'
```

### 4. Ajouter une question

```bash
curl -X POST http://localhost:8000/api/v1/forms/FORM_ID/questions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Comment évaluez-vous notre service ?",
    "question_type": "multiple_choice",
    "is_required": true,
    "options": ["Excellent", "Bon", "Moyen", "Mauvais"],
    "order": 1
  }'
```

### 5. Soumettre une réponse

```bash
curl -X POST http://localhost:8000/api/v1/forms/FORM_ID/submit \
  -H "Content-Type: application/json" \
  -d '{
    "answers": [
      {
        "question_id": "QUESTION_ID",
        "value": "Excellent"
      }
    ]
  }'
```

## 🐛 Debugging

### Logs Docker

```bash
# Voir les logs de l'API
docker-compose logs -f api

# Voir tous les logs
docker-compose logs -f
```

### Accès MongoDB

- **Mongo Express** : http://localhost:8081
  - Username: `admin`
  - Password: `pass`

- **MongoDB Shell** :
```bash
docker exec -it forms-mongodb mongosh
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.
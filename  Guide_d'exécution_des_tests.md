# 🧪 Guide d'exécution des tests

## 📋 Prérequis

- Python 3.11+
- Docker et Docker Compose
- MongoDB (pour tests locaux)

## 🚀 Exécution des tests

### 1. Tests avec Docker (Recommandé)

```bash
# Lancer tous les tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Reconstruire et tester
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Nettoyer après les tests
docker-compose -f docker-compose.test.yml down -v
```

### 2. Tests locaux

```bash
# Installer les dépendances de test
pip install -r requirements.txt
pip install pytest-cov

# Lancer MongoDB local (si pas déjà fait)
docker run -d -p 27017:27017 --name mongodb-test mongo:7.0

# Exécuter tous les tests
pytest

# Tests avec rapport de couverture
pytest --cov=app --cov-report=html

# Tests spécifiques
pytest tests/unit/                     # Seulement les tests unitaires
pytest tests/integration/              # Seulement les tests d'intégration
pytest tests/integration/test_auth.py  # Un fichier spécifique
pytest -k "test_login"                 # Tests contenant "test_login"
```

### 3. Options pytest utiles

```bash
# Mode verbose
pytest -v

# Afficher les prints
pytest -s

# Arrêter au premier échec
pytest -x

# Exécuter les tests marqués
pytest -m unit          # Seulement tests unitaires
pytest -m integration   # Seulement tests d'intégration
pytest -m "not slow"    # Exclure les tests lents

# Tests en parallèle (installer pytest-xdist)
pip install pytest-xdist
pytest -n auto

# Générer un rapport JUnit (pour CI/CD)
pytest --junitxml=report.xml
```

## 📊 Rapport de couverture

Après avoir exécuté les tests avec couverture :

```bash
# Voir le rapport en console
pytest --cov=app --cov-report=term-missing

# Générer un rapport HTML
pytest --cov=app --cov-report=html

# Ouvrir le rapport
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## 🔧 Configuration des tests

### Variables d'environnement

Pour les tests locaux, créez un fichier `.env.test` :

```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=forms_db_test
SECRET_KEY=test-secret-key
DEBUG=true
```

### Exécution avec variables custom

```bash
# Linux/macOS
export $(cat .env.test | xargs) && pytest

# Windows PowerShell
Get-Content .env.test | ForEach-Object { $var = $_.Split('='); [Environment]::SetEnvironmentVariable($var[0], $var[1]) }
pytest
```

## 🐛 Débogage des tests

### Avec VS Code

Ajoutez dans `.vscode/launch.json` :

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["-v", "${file}"],
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

### Avec PyCharm

1. Clic droit sur le dossier `tests`
2. "Run 'pytest in tests'"
3. Pour déboguer : "Debug 'pytest in tests'"

## 📈 Objectifs de qualité

- **Couverture minimale** : 80%
- **Temps d'exécution** : < 30 secondes
- **Tous les endpoints testés**
- **Cas d'erreur couverts**

## 🔄 Intégration CI/CD

### GitHub Actions exemple

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mongodb:
        image: mongo:7.0
        ports:
          - 27017:27017
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest-cov
    
    - name: Run tests
      run: pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## ⚠️ Troubleshooting

### MongoDB connection failed

```bash
# Vérifier que MongoDB tourne
docker ps | grep mongo

# Relancer MongoDB
docker-compose -f docker-compose.test.yml down
docker-compose -f docker-compose.test.yml up -d mongodb-test
```

### Import errors

```bash
# S'assurer d'être dans le bon dossier
cd forms-api

# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Tests lents

```bash
# Identifier les tests lents
pytest --durations=10

# Marquer les tests lents
# Dans le test : @pytest.mark.slow
# Exécuter sans : pytest -m "not slow"
```
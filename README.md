# Orchestrating AI Models - Microservices Architecture

Este proyecto implementa una arquitectura de microservicios para orquestar modelos de IA, separando las funcionalidades en servicios independientes para optimizar el despliegue y escalabilidad.

## 🏗️ Arquitectura

```
Frontend (Vue.js)
       ↓
Core Backend (FastAPI) ← API Gateway
       ↓
┌─────────────────────────────────────────┐
│              Microservicios             │
├─────────────────────────────────────────┤
│ describe-image-service    (Puerto 8001) │ ← GPU Intensivo (RunPod)
│ extract-webcontent-service (Puerto 8002) │ ← CPU (Servidor estándar)
│ generate-description-service (Puerto 8003) │ ← GPU/CPU (RunPod/Estándar)
└─────────────────────────────────────────┘
       ↓
PostgreSQL Database
```

## 📁 Estructura del Monorepo

```
orchestrating-ai-models/
├── backend/              # Backend principal (CRUD, Gateway)
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── services/                  # Microservicios AI
│   ├── describe-image/        # Análisis de imágenes con Qwen2.5-VL
│   ├── extract-webcontent/    # Extracción de contenido web
│   └── generate-description/  # Generación de descripciones
├── shared/                    # Código compartido
│   ├── models/
│   ├── utils/
│   └── config/
├── frontend/                  # Interfaz Vue.js
├── docker-compose.yml         # Desarrollo local
└── .github/workflows/         # CI/CD pipelines
```

## 🚀 Despliegue por Servicios

### Desarrollo Local (Docker)

```bash
# Iniciar todos los servicios
docker-compose up -d

# Servicios disponibles:
# - Core Backend: http://localhost:8000
# - Describe Image: http://localhost:8001
# - Extract WebContent: http://localhost:8002
# - Generate Description: http://localhost:8003
# - PostgreSQL: localhost:5432
```

### Producción (RunPod + Servidores)

**Backend** → Servidor estándar (DigitalOcean, AWS, etc.)
```bash
# Variables de entorno para producción
DESCRIBE_IMAGE_SERVICE_URL=https://describe-image.runpod.io
EXTRACT_WEBCONTENT_SERVICE_URL=https://extract-web.yourserver.com
GENERATE_DESCRIPTION_SERVICE_URL=https://generate-desc.runpod.io
```

**Servicios AI** → RunPod (GPU) o servidores estándar (CPU)

## 🔧 Configuración por Servicio

### Backend (Puerto 8000)
- **Función**: API Gateway, CRUD productos, upload imágenes
- **Recursos**: CPU estándar, base de datos
- **Despliegue**: Cualquier proveedor cloud

### Describe Image Service (Puerto 8001)
- **Función**: Análisis de imágenes con Qwen2.5-VL
- **Recursos**: GPU (NVIDIA RTX 4090 recomendada)
- **Despliegue**: RunPod con GPU

### Extract WebContent Service (Puerto 8002)
- **Función**: Scraping y extracción de contenido web
- **Recursos**: CPU, memoria para Selenium
- **Despliegue**: Servidor estándar

### Generate Description Service (Puerto 8003)
- **Función**: Generación de descripciones con LLMs
- **Recursos**: GPU (opcional) o CPU con APIs externas
- **Despliegue**: RunPod (GPU) o servidor estándar (API)

## 🛠️ Desarrollo

### Ejecutar un servicio individual

```bash
# Describe Image Service
cd services/describe-image
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001

# Extract WebContent Service
cd services/extract-webcontent
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002

# Generate Description Service
cd services/generate-description
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8003
```

### Construir imágenes Docker individuales

```bash
# Backend
docker build -t backend ./backend

# Servicios AI
docker build -t describe-image-service ./services/describe-image
docker build -t extract-webcontent-service ./services/extract-webcontent
docker build -t generate-description-service ./services/generate-description
```

## 🔄 CI/CD con GitHub Actions

Cada servicio tiene su propio workflow que se activa cuando hay cambios:

- **build-backend.yml** → Cambios en `backend/`
- **build-describe-image.yml** → Cambios en `services/describe-image/`
- **build-extract-webcontent.yml** → Cambios en `services/extract-webcontent/`
- **build-generate-description.yml** → Cambios en `services/generate-description/`

Los workflows automáticamente:
1. Construyen la imagen Docker
2. La suben a GitHub Container Registry
3. Despliegan a producción (RunPod/servidor)

## 🌐 Endpoints de Servicios

### Backend (Gateway)
```
POST /api/v1/services/describe-image
POST /api/v1/services/extract-webcontent
POST /api/v1/services/generate-description
GET  /api/v1/services/health
```

### Servicios Directos
```
# Describe Image Service
POST http://localhost:8001/api/v1/describe
GET  http://localhost:8001/health

# Extract WebContent Service
POST http://localhost:8002/api/v1/extract
GET  http://localhost:8002/health

# Generate Description Service
POST http://localhost:8003/api/v1/generate
GET  http://localhost:8003/health
```

## 🔑 Variables de Entorno

### Backend
```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/orchestration_db
DESCRIBE_IMAGE_SERVICE_URL=http://describe-image-service:8001
EXTRACT_WEBCONTENT_SERVICE_URL=http://extract-webcontent-service:8002
GENERATE_DESCRIPTION_SERVICE_URL=http://generate-description-service:8003
```

### Servicios AI
```env
# Para Generate Description Service
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Para Describe Image Service
MODEL_CACHE_DIR=/app/models
```

## 📊 Ventajas de esta Arquitectura

✅ **Escalabilidad independiente** - Cada servicio puede escalar según demanda
✅ **Despliegue optimizado** - GPU solo donde se necesita
✅ **Tolerancia a fallos** - Un servicio caído no afecta los otros
✅ **Desarrollo paralelo** - Equipos pueden trabajar en servicios independientes
✅ **Costos optimizados** - Pagar GPU solo para servicios que la requieren
✅ **CI/CD granular** - Deploy solo lo que cambió

## 🚀 Próximos Pasos

1. Configurar secretos en GitHub (API keys, RunPod tokens)
2. Personalizar workflows de deployment
3. Configurar monitoring y logging
4. Implementar service discovery (opcional)
5. Agregar tests automatizados por servicio
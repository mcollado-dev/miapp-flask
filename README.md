# 🚀 Desarrollo y Despliegue Automatizado de una Aplicación Flask  
### Proyecto FCT — ASIR 2º | Curso 2024/2025

**Autor:** Manuel Collado Ponce de León  
**Centro:** IES Zaidín-Vergeles  
**Ciclo:** Administración de Sistemas Informáticos en Red (ASIR)

---

## 📋 Descripción del Proyecto

Este repositorio contiene **todo el desarrollo e infraestructura** del proyecto FCT:

> **Implementación completa de un entorno DevOps profesional para el desarrollo, análisis, automatización y despliegue de una aplicación web Flask utilizando Docker, Jenkins y SonarQube.**

La aplicación gestiona usuarios con autenticación segura, control de roles y estadísticas dinámicas, desplegándose automáticamente mediante un pipeline CI/CD totalmente funcional.

---

## 🎯 Objetivos

- Desarrollar una aplicación web real con **Flask** y **MariaDB**
- Crear una **infraestructura distribuida**
- Implementar un **pipeline CI/CD con Jenkins**
- Analizar calidad del código usando **SonarQube**
- Automatizar despliegue mediante **Docker**
- Garantizar **seguridad** en datos y credenciales
- Documentar todo el proceso para su replicabilidad

---

## ⚙️ Tecnologías Utilizadas

| Tecnología | Uso |
|-------------|-----|
| **Python 3.11** | Lenguaje principal |
| **Flask 3.1.2** | Framework web |
| **MariaDB** | Base de datos relacional |
| **SQLAlchemy** | ORM |
| **Werkzeug** | Hash seguro de contraseñas |
| **Flask-WTF** | Gestión de formularios + CSRF |
| **Matplotlib** | Gráficos dinámicos |
| **Docker** | Contenerización |
| **Jenkins** | CI/CD |
| **SonarQube** | Control de calidad |
| **Git / GitHub** | Versionado |
| **Bootstrap 5** | Interfaz web |

---

## 🏗️ Arquitectura de la Infraestructura

El proyecto se ejecuta sobre **5 máquinas virtuales** independientes:

| Máquina | IP | Rol |
|---------|----|------|
| `debianserver` | 192.168.56.100 | Jenkins Master |
| `debianagent` | 192.168.56.101 | Jenkins Agent |
| `sonarqube` | 192.168.56.104 | SonarQube Server |
| `debianMariaDB` | 192.168.56.105 | MariaDB |
| `debianWordpress` | 192.168.56.106 | Servidor de despliegue Docker |

Comunicación por red privada **Host-Only (192.168.56.x)**.

---

## 📁 Estructura del Proyecto

miapp-flask/
├── app.py # Aplicación principal Flask
├── models.py # Modelo de datos SQLAlchemy
├── test_app.py # Tests unitarios (pytest)
├── requirements.txt # Dependencias Python
├── Dockerfile # Imagen Docker
├── Jenkinsfile # Pipeline CI/CD
├── templates/ # HTML (Jinja2 + Bootstrap)
│ ├── base.html
│ ├── index.html
│ ├── login.html
│ ├── registro.html
│ ├── estadisticas.html
│ ├── funciones.html
│ ├── documentacion.html
│ └── detalles.html
└── static/
└── style.css


---

## ✅ Características de la Aplicación

- Registro seguro de usuarios
- Login con contraseñas **hasheadas**
- Control por **roles**:
  - Administrador
  - Colaborador
  - Usuario
- Área de estadísticas protegida
- Gráficos dinámicos de distribución de roles
- Protección **CSRF**
- Sistema de sesiones
- Validaciones completas de formularios

---

## 🧪 Pruebas Automatizadas

Los tests están implementados con **pytest + pytest-cov**.

- Validación de formularios
- Autenticación segura
- Extracción automática de token CSRF
- Verificación de HTML
- Generación de reporte de cobertura (`coverage.xml`)

La cobertura es enviada automáticamente a **SonarQube**.

---

## 🐳 Docker

### Dockerfile

- Imagen base: `python:3.11-slim`
- Instalación de dependencias
- Exposición del puerto `80`
- Arranque automático de Flask

### Build manual

```bash
docker build -t miapp-flask .
docker run -d -p 80:80 miapp-flask

---

##🔄 Pipeline CI/CD de Jenkins

El pipeline completo ejecuta:

-✅ Checkout desde GitHub

-🧪 Ejecución de Tests + Coverage

-🔍 Análisis estático con SonarQube

-✅ Validación Quality Gate

-🐳 Build de imagen Docker

-💾 Verificación conexión a MariaDB

-🚀 Deploy remoto automático

-✅ Verificación de servicio activo

Si cualquier fase falla → el pipeline se detiene.

---

##📦 Despliegue Automático

Despliegue al servidor debianWordpress (192.168.56.106) mediante:

docker save miapp-flask:latest | bzip2 | ssh usuario@192.168.56.106 'bunzip2 | docker load'
docker stop miapp-flask || true
docker rm miapp-flask || true
docker run -d --name miapp-flask -p 8081:80 miapp-flask

---

##📊 Gestión visual con Portainer

Se ha integrado Portainer CE para:

-Visualización de contenedores activos

-Gestión de imágenes Docker

-Administración de redes y volúmenes

-Monitorización de logs

---

##▶️ Ejecución Local

python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python app.py


Acceso: http://localhost:80

---

##📥 Flujo de trabajo GitHub

- 1.Desarrollo local

- 2.Commit

git add .
git commit -m "mensaje"
git push


- 3.Jenkins detecta cambios

- 4.Pipeline automático

- 5.Despliegue sin intervención manual

---

##🎓 Conclusiones

Este proyecto demuestra dominio en:

-Desarrollo web profesional con Flask

-Automatización DevOps completa

-Arquitecturas distribuidas

-Control de calidad de código

-Seguridad en aplicaciones web

-Gestión de bases de datos

-Docker & Jenkins

-Entornos reales CI/CD

La solución es escalable, mantenible y alineada con estándares profesionales, válida como base para proyectos productivos reales.

---

##📜 Licencia

Este proyecto forma parte del Trabajo de Fin de FCT — ASIR 2024/2025.
Uso educativo y demostrativo.
---

# Sistema de Gestión de Alquileres Vehiculares - Rentar (Grupo J)

Código fuente correspondiente al Trabajo Práctico de **Desarrollo de Software en Sistemas Distribuidos** (Hito 1).

El sistema está compuesto por un backend modularizado construido con **FastAPI** y un frontend desarrollado como Single Page Application (SPA) con **React** y **Vite**.

## ⚙️ Requisitos Previos
Para ejecutar este proyecto en tu entorno local, asegurate de tener instalado:
* [Python 3.10+](https://www.python.org/downloads/)
* [Node.js 18+](https://nodejs.org/)
* Git / GitHub Desktop

---

## Instalación y Ejecución

El proyecto está dividido en dos carpetas principales. Se deben levantar ambas consolas en paralelo para que el sistema funcione.

### 1. Backend (FastAPI)
Abre una terminal y navega hasta la raíz del proyecto.

```bash
# 1. Entrar a la carpeta del backend
cd backend

# 2. Crear un entorno virtual (Recomendado)
python -m venv venv

# 3. Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# 4. Instalar las dependencias (FastAPI, SQLAlchemy, Strawberry, etc.)
pip install -r requirements.txt

# 5. Levantar el servidor
uvicorn app.main:app --reload
```
Una vez levantado, el backend estará disponible en:
* **API Base:** `http://localhost:8000`
* **Documentación REST (Swagger):** `http://localhost:8000/docs`
* **Consola GraphQL:** `http://localhost:8000/graphql`

*(Nota: La base de datos SQLite `rentar.db` se generará automáticamente en la carpeta backend al levantar el servidor por primera vez).*

### 2. Frontend (React + Vite)
Abrí una nueva terminal (sin cerrar la del backend) y navega a la raíz del proyecto.

```bash
# 1. Entrar a la carpeta del frontend
cd frontend

# 2. Instalar los paquetes de Node
npm install

# 3. Levantar el servidor de desarrollo
npm run dev
```
La interfaz web estará disponible en `http://localhost:5173`.

---

## Branching
**IMPORTANTE:** No hacer commits directamente sobre la rama `main`. 
1. Clona el repositorio.
2. Crea una rama nueva para tu funcionalidad: `git checkout -b feature/nombre-de-tu-tarea` (o desde GitHub Desktop).
3. Desarrolla y prueba tus cambios.
4. Sube tu rama y abre un **Pull Request** hacia `main` para que el equipo lo revise.
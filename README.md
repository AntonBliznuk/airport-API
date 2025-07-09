# ✈️ airport-API

A clean and production-ready RESTful API for managing airports, flights, users, and ticket orders — featuring JWT authentication, Cloudinary media storage, brute-force login protection, and fully Dockerized local development.

---

## 🚀 Features

- ✅ **JWT Authentication** — Register, login, logout with secure token handling
- ✅ **Brute-force Login Protection** — Throttling for login attempts
- ✅ **Cloudinary Image Storage** — Store and serve media efficiently
- ✅ **Dynamic Price Calculation** — Prices set via logic & config (`settings.py`)
- ✅ **Search Support** — Powerful filtering for flights and orders
- ✅ **Custom Permissions** — Fine-grained access control (admin/user)
- ✅ **Swagger Documentation** — Auto-generated via `drf-spectacular`
- ✅ **Dockerized Setup** — Easy local development using Docker Compose
- ✅ **Environment Separation** — Clear split between dev and prod configs
- ✅ **DB Schema Diagram** — Visual reference for the database schema

---

## 🧱 Tech Stack

- **Backend**: Django 5.2, Django REST Framework
- **Auth**: djangorestframework-simplejwt
- **Database**: PostgreSQL
- **Media**: Cloudinary
- **Docs**: drf-spectacular
- **Dev Tools**: Docker, Docker Compose, Ruff, Pre-commit

---

## 📦 Local Installation

> 🐳 Make sure [Docker](https://docs.docker.com/get-docker/) is installed.

1. **Clone the repo**:
```bash
git clone https://github.com/yourusername/airport-API.git
cd airport-API
```
2.	Create your environment config:
```bash
cp .env.example .env
```
✏️ Modify .env with your own credentials (especially SECRET_KEY and Cloudinary config).
3.	Build the dev container:
```bash
docker-compose -f docker-compose.dev.yml build
```
4.	Run the project:
```bash
docker-compose -f docker-compose.dev.yml up
```
5.	Access the app:

API-base: http://0.0.0.0:8000

Swagger UI: http://0.0.0.0:8000/api/doc/swagger/

Redoc: http://0.0.0.0:8000/api/doc/redoc/


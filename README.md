# Quiz Management System

A Django-based quiz application with admin panel and REST API.

**Live Demo:** [https://mcq-django.onrender.com](https://mcq-django.onrender.com)

---

## Features

- Create quizzes with MCQ, True/False, and Text questions
- One-time submission per email
- Auto-scoring with admin-only results view
- 24-hour URL expiration
- Responsive quiz interface

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5.0, Django REST Framework |
| Database | PostgreSQL (Neon) |
| Deployment | Render.com |
| Static Files | WhiteNoise |

---

## Quick Start

```bash
# Clone repo
git clone https://github.com/Mohd-Saddam/mcq_django.git
cd mcq_django/quiz_system

# Setup environment
python -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt

# Configure database
cp .env.example .env  # Edit with your settings

# Run migrations
python manage.py migrate
python manage.py createsuperuser

# Start server
python manage.py runserver
```

**Access:**
- Admin: http://127.0.0.1:8000/admin/
- API: http://127.0.0.1:8000/api/

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/quizzes/` | List active quizzes |
| GET | `/api/quizzes/{id}/` | Get quiz details |
| POST | `/api/quizzes/{id}/submit/` | Submit answers |
| POST | `/api/quizzes/{id}/check-email/` | Check email status |

---

## Project Structure

```
quiz_system/
├── quiz_system/     # Django settings
├── quizzes/         # Main app (models, views, serializers)
├── templates/       # HTML templates
└── static/          # Static files
```

---

## Deployment (Render)

1. Fork/push to GitHub
2. Create Web Service on Render
3. Set environment variables:
   - `SECRET_KEY`, `DEBUG=False`
   - `DATABASE_URL` (Neon PostgreSQL)
   - `ALLOWED_HOSTS=.onrender.com`
4. Build: `./build.sh`
5. Start: `gunicorn quiz_system.wsgi:application`

---

## Author

**Mohd Saddam**  
GitHub: [@Mohd-Saddam](https://github.com/Mohd-Saddam)

---

## License

MIT License


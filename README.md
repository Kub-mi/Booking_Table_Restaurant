# Booking Table Restaurant

A full-featured Django web application for managing restaurant table reservations. The project includes a responsive Bootstrap-powered front end, an authenticated user area for managing bookings, and a Django admin interface for content management.

## Features

- Landing page with restaurant information, services, team members, and contact form.
- About page describing the restaurant story and staff.
- Authenticated reservation workflow with availability filtering and booking management.
- Personal dashboard for users with reservation history and profile editing.
- Django admin for managing tables, reservations, content blocks, and contact inquiries.
- Dockerized development environment with PostgreSQL.

## Tech stack

- Python 3.12, Django 5
- PostgreSQL (via `psycopg` driver)
- Bootstrap 5
- Docker & Docker Compose

## Getting started

### Prerequisites

- Python 3.12+
- PostgreSQL 15+
- (Optional) Docker & Docker Compose v2

### Environment variables

Create an `.env` file based on the provided template:

```bash
cp .env_sample .env
```

Update the values with secure credentials. The most important variables are:

- `SECRET_KEY`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

### Local development

Install dependencies and apply migrations:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The site will be available at `http://127.0.0.1:8000/`. The admin panel is exposed at `http://127.0.0.1:8000/admin/`.

### Using Docker

Build and start the services:

```bash
docker compose up --build
```

The command launches both the Django application and a PostgreSQL instance. Apply migrations and create a superuser inside the running container:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### Running tests

```bash
python manage.py test
```

## Project structure

```
.
├── config/               # Django project configuration
├── core/                 # Public site pages and contact form
├── reservations/         # Reservation models, forms, and views
├── users/                # Custom user model and profile management
├── templates/            # HTML templates (Bootstrap based)
├── static/               # Static assets (CSS)
├── docker-compose.yml    # Docker services definition
├── Dockerfile            # Docker image definition
└── README.md
```

## Admin management

Use the Django admin to manage:

- **Restaurant information**: name, description, contact details, mission statement.
- **Services**: marketing blocks shown on the landing page.
- **Team members**: staff displayed on the landing and about pages.
- **Tables & reservations**: manage availability and confirm/cancel bookings.
- **Contact submissions**: review messages submitted from the contact form.

## License

This project is provided for educational purposes. Adapt and extend it to fit your own restaurant reservation workflows.

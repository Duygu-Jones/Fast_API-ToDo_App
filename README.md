# FastAPI Todo App

A full-stack todo list application built with FastAPI. Users can register, log in, and manage their tasks through a clean web interface. The app includes JWT-based authentication, role-based access control, and a PostgreSQL backend.

---

## Features

- **User authentication** — register, login and logout with JWT tokens
- **Todo management** — create, edit, delete and mark tasks as complete
- **Priority levels** — assign priority from 1 to 5 for each task
- **Admin panel** — admin users can view and delete all todos in the system
- **Profile settings** — users can update their password and phone number
- **Interactive UI** — Bootstrap-based frontend with Jinja2 templates
- **API documentation** — automatic Swagger and ReDoc docs via FastAPI

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL (SQLite for development) |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Frontend | Jinja2 templates, Bootstrap |
| Server | Uvicorn |
| Testing | pytest |

---

## Project Structure

```
11_FastAPI_todo_app/
├── main.py               # App entry point and router registration
├── models.py             # SQLAlchemy models (Users, Todos)
├── database.py           # DB connection and session setup
├── requirements.txt      # Dependencies
├── alembic.ini           # Migration config
├── routers/
│   ├── auth.py           # Register and login endpoints
│   ├── todos.py          # Todo CRUD endpoints
│   ├── users.py          # User profile endpoints
│   └── admin.py          # Admin-only endpoints
├── templates/            # Jinja2 HTML templates
├── static/               # CSS and JavaScript files
├── alembic/              # Database migrations
│   └── versions/
└── test/                 # Unit and integration tests
    ├── utils.py
    ├── test_auth.py
    ├── test_todos.py
    ├── test_users.py
    └── test_admin.py
```

---

## Database Models

**Users**
```
id, email, username, first_name, last_name,
hashed_password, is_active, role, phone_number
```

**Todos**
```
id, title, description, priority (1-5),
complete, owner_id (FK → users.id)
```

---

## API Endpoints

### Auth — `/auth`
| Method | Path | Description |
|---|---|---|
| GET | `/auth/login-page` | Render login form |
| GET | `/auth/register-page` | Render register form |
| POST | `/auth/` | Create new user |
| POST | `/auth/token` | Login and get access token |

### Todos — `/todos`
| Method | Path | Description |
|---|---|---|
| GET | `/todos/` | Get all todos for current user |
| GET | `/todos/todo/{id}` | Get a specific todo |
| POST | `/todos/todo` | Create new todo |
| PUT | `/todos/todo/{id}` | Update a todo |
| DELETE | `/todos/todo/{id}` | Delete a todo |

### User — `/user`
| Method | Path | Description |
|---|---|---|
| GET | `/user/` | Get current user info |
| PUT | `/user/password` | Change password |
| PUT | `/user/phonenumber/{phone}` | Update phone number |

### Admin — `/admin`
| Method | Path | Description |
|---|---|---|
| GET | `/admin/todo` | Get all todos (admin only) |
| DELETE | `/admin/todo/{id}` | Delete any todo (admin only) |

---

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 12+ (or SQLite for local development)
- pip

### Installation

**1. Clone the repository**
```bash
git clone <repo-url>
cd 11_FastAPI_todo_app
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up the database**

For PostgreSQL, create a database and update the connection string in `database.py`:
```python
SQLALCHEMY_DATABASE_URL = 'postgresql://username:password@localhost/TodoAppDatabase'
```

If you prefer SQLite for local development, comment out the PostgreSQL line and uncomment the SQLite one in `database.py`.

**5. Run database migrations**
```bash
alembic upgrade head
```

**6. Start the server**
```bash
uvicorn main:app --reload
```

The app will be available at `http://localhost:8000`.

---

## Accessing the App

| URL | Description |
|---|---|
| `http://localhost:8000` | Web interface (redirects to todos) |
| `http://localhost:8000/docs` | Swagger UI (interactive API docs) |
| `http://localhost:8000/redoc` | ReDoc (alternative API docs) |
| `http://localhost:8000/healthy` | Health check endpoint |

---

## Running Tests

```bash
# Run all tests
pytest test/

# Run a specific file with verbose output
pytest test/test_auth.py -v
```

Tests use a separate SQLite database and include fixtures that clean up after each run.

---

## Security Notes

> The following settings are fine for development but **must be changed before deploying to production**.

- **JWT secret key** — hardcoded in `auth.py`, move this to an environment variable
- **Database credentials** — stored in `database.py`, use a `.env` file instead
- **Token expiry** — currently set to 20 minutes, adjust based on your needs

A simple way to manage this is with `python-dotenv` (already listed in requirements):

```bash
# .env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/TodoAppDatabase
```

---

## Input Validation

The app validates all incoming data using Pydantic:

- Title: minimum 3 characters
- Description: 3–100 characters
- Priority: integer between 1 and 5
- Password: minimum 6 characters
- Email: must be a valid email format

---

## Author

**Duygu Jones**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Duygu%20Jones-blue?logo=linkedin)](https://www.linkedin.com/in/duygujones/)
[![GitHub](https://img.shields.io/badge/GitHub-Duygu--Jones-black?logo=github)](https://github.com/Duygu-Jones/)

---

## License

This project is open source and available for personal and educational use.

# A take-home Django API project for a position

## Requirements

- Docker
- Docker Compose

> You **do not need** to install Python or Poetry locally. Everything runs inside Docker.

---

## Useful Commands (via `make`)

### Core (Django + PostgreSQL)

```
make up                # Build and run the app and database containers
make shell             # Open a shell in the app container
make migrate           # Run Django migrations
make makemigrations    # Create new migrations
make createsuperuser   # Create a Django superuser
make down              # Stop and remove containers and volumes
```

---

## Testing

Run your test suite using `pytest`:

```
make test
```

Tests run inside the container using the same PostgreSQL database.

---

## Maintenance

```
make logs              # Tail logs from all containers
```

---

## Notes

- All Python dependencies are managed by [Poetry](https://python-poetry.org/) **inside** the container.
- `make` commands wrap Docker Compose for improved developer experience.


---

## Authentication

This project uses **[DRF Token Authentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)**.

### 🔐 Get your token

You need a user in the system. You can create one via:

- The Django **admin site**
- The Django **shell**
- Or, as a shortcut, by creating a superuser:

```bash
make createsuperuser
```

Then, request a token:

```bash
curl -X POST http://localhost:8000/api/token/ \
     -d "username=your_username" \
     -d "password=your_password"
```

You’ll get a JSON response like:

```json
{"token": "abc123..."}
```

### 🔒 Authenticate your requests

Include the token in your requests using the `Authorization` header:

```http
Authorization: Token abc123...
```

You can now access any protected endpoints.

# A Take-Home Django API Project

## Requirements
- **Docker**  
- **Docker Compose**

> You **do not need** to install Python or Poetry locally. Everything runs inside Docker.

---

## Useful Commands (via `make`)

### Core (Django + PostgreSQL)
```bash
make up                # Build and run the app and database containers
make down              # Stop and remove containers and volumes
make build             # Rebuild images without starting the stack
make shell             # Open a bash shell in the app container
make djshell           # Open the Django shell (manage.py shell)
make migrate           # Apply migrations
make makemigrations    # Create new migrations
make createsuperuser   # Create a Django superuser
```

---

## Development Tools

```
make lint              # Run Ruff to lint the codebase
make format            # Run Ruff to auto-format the codebase
```


## Database Utilities
```
make populate-test-db  # Populate the test database with example data
```

## Testing

```
make test              # Run the full test suite with pytest
```

Tests run inside the container against the same PostgreSQL service.

Need something more granular? Drop into the container and run pytest yourself:

```
make shell
py.test --reuse-db -s <path_test_file> 
```

## Logs

```
make logs              # Tail logs from all containers
```

---

## Notes

- All Python dependencies are managed by [Poetry](https://python-poetry.org/) **inside** the container.
- Each `make` target is a thin wrapper around Docker Compose for a smoother DX.


---

## Authentication

This project uses **[DRF Token Authentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)**.

### 🔐 Get a token

1. Ensure you have a user in the system. Create one via:
* Django admin (/admin/)
* Django shell (make djshell)
* Swagger UI (http://localhost:8000/schema/swagger-ui/)

Or simply create a superuser:
```bash
make createsuperuser
```

2.  request a token:

```bash
curl -X POST http://localhost:8000/api/token/ \
     -d "username=<your_username>" \
     -d "password=<your_password>"
```

Response example:

```json
{"token": "abc123..."}
```

### 🔒 Authenticate your requests

Add the token in the`Authorization` header:

```http
Authorization: Token abc123...
```
You can now access protected endpoints. Alternatively, use the Swagger UI at http://localhost:8000/schema/swagger-ui/.

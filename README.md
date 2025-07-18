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
make down              # Stop and remove containers
make build             # Rebuild images without starting the stack
make shell             # Open a bash shell in the app container
make djshell           # Open the Django shell (manage.py shell)
make migrate           # Apply migrations
make makemigrations    # Create new migrations
make createsuperuser   # Create a Django superuser
```

---

## Development Tools

```bash
make lint              # Run Ruff to lint the codebase
make format            # Run Ruff to auto-format the codebase
```


## Database Utilities
```bash
make populate-test-db  # Populate the test database with example data
```

## Testing

```bash
make test              # Run the full test suite with pytest
```

Tests run inside the container against the same PostgreSQL service.

Need something more granular? Drop into the container and run Pytest yourself:

```
make shell
py.test --reuse-db -s <path_test_file> 
```

## Logs

```
make logs              # Tail logs from all containers
```


## Notes

- All Python dependencies are managed by [Poetry](https://python-poetry.org/) **inside** the container.
- Each `make` target is a thin wrapper around Docker Compose for a smoother DX.


## Authentication

This project uses **[DRF Token Authentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)**.

### Get a token

1. Ensure you have a user in the system. Create one via:
- Django admin (/admin/)
- Django shell (make djshell)
- Swagger UI (http://localhost:8000/schema/swagger-ui/)

Or simply create a superuser:
```bash
make createsuperuser
```

2.  Request a token:

```bash
curl -X POST http://localhost:8000/api/token/ \
     -d "username=<your_username>" \
     -d "password=<your_password>"
```

Response example:

```json
{"token": "abc123..."}
```

### Authenticate your requests

Add the token in the`Authorization` header:

```http
Authorization: Token abc123...
```
You can now access protected endpoints.

### API Documentation
The OpenAPI schema is served at `/schema/` and the Swagger UI at `/schema/swagger-ui/`.

## Roadmap for Production Readiness
This project provides a solid foundation for a simple API, but to be suitable for real-world use in production 
environments, several improvements should be made. 
Below is a suggested roadmap outlining key areas of enhancement:

### Environment-Specific Settings
Currently, only `base` and `local` settings exist. To support a real deployment workflow, the following should be added:

- `staging.py` — Mirrors production config, used for pre-release validation.
- `production.py` — Configuration for the live environment serving real users.

Secret management — Use AWS Secrets Manager or similar to avoid hardcoding sensitive data.

### Continuous Integration / Continuous Deployment
Introduce GitHub Actions (or another CI system) with the following stages:
1. Lint: using `ruff` for example (as currently with `make lint`)
2. Tests & Coverage: `pytest --cov`
3. Build & Push: Docker image built and pushed to a registry (e.g. AWS Elastic Container Registry - ECR)
4. Deploy: Automatic to staging on every push to `main`; deploy to production triggered by tagging a release on `main`

Include quality gates to prevent merging if:
- Tests fail
- Coverage falls below a minimum threshold (e.g. 90%)

### Concurrency Handling for Transactions
The following critical section in `WithdrawView` is **theoretically vulnerable to race conditions** under heavy load:

```python
with transaction.atomic():
    account.balance -= amount
    account.save()
    Transaction.objects.create(...)
```

Even within a transaction, two concurrent requests might read the same balance before either updates it, potentially leading to a negative balance.

**Recommended solution:**  
Use a [Redis distributed lock](https://redis.io/glossary/redis-lock/) **per account ID**, ensuring only one request can mutate the balance of a given account at a time.

### Healthcheck Endpoint

Add a simple ping endpoint. This allows orchestration systems (Kubernetes, ECS, etc.) to monitor the instance’s health and restart if needed.
The healthcheck should include a database connectivity check to ensure the application can reach the database and that it's responsive.

Example:
- GET `/ping/` → 200 OK  
- Response: `{"pong": true, "db": "ok"}`

### Production WSGI/ASGI Server
The app currently runs using Django's built-in development server (runserver). This is not suitable for production.

For production environments, use a proper WSGI or ASGI server such as:

* gunicorn (common for WSGI deployments)

* uvicorn (if switching to ASGI for async support)

This ensures performance, stability, and proper process management under load.

More info: https://docs.djangoproject.com/en/5.2/howto/deployment/


### Monitoring & Observability
- Integrate APM tools like Sentry (for errors + performance).
- Export Prometheus metrics (e.g. with django-prometheus) and create/use dashboards via Grafana

## Optional Enhancements

### Performance Profiling
Add profiling middleware during dev to analyze bottlenecks, for example [django-silk](https://github.com/jazzband/django-silk)

### Reusable Test Fixtures with Factory Boy

Replace repetitive test setup with [Factory Boy](https://factoryboy.readthedocs.io/en/stable/) factories. Example:

```python
class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account
    balance = Decimal("100.00")
```

Use these factories across tests to reduce duplication and improve maintainability.

### Clean Architecture for Business Logic
Currently, business logic (e.g. withdrawals, deposits) lives directly in the views. This is acceptable given the current simplicity of the use cases.

However, as soon as the business logic grows more complex, it's strongly recommended to adopt a clean architecture approach:
- Move business logic into use case classes
- Keep views as thin controllers that delegate to those use cases

This makes the logic reusable, easier to test, and decoupled from the HTTP layer.

### Separate Databases for Local and Tests

| Context   | URL (example)               | Purpose                                 |
|-----------|-----------------------------|------------------------------------------|
| **local** | `postgres://…:5432/app`     | Dummy data for manual testing and dev.   |
| **test**  | `postgres://…:5433/app_test`| Used during test runs; minimal or zero fixtures. |

This separation allows local development to use realistic data scenarios, while keeping the test environment clean, fast, and predictable.

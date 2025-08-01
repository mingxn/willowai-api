# FastAPI Best Practices

Opinionated list of best practices and conventions I use in startups.

For the last several years in production, we have been making good and bad decisions that impacted our developer experience dramatically. Some of them are worth sharing.

## Contents

*   [Project Structure](#project-structure)
*   [Async Routes](#async-routes)
    *   [I/O Intensive Tasks](#io-intensive-tasks)
    *   [CPU Intensive Tasks](#cpu-intensive-tasks)
*   [Pydantic](#pydantic)
    *   [Excessively use Pydantic](#excessively-use-pydantic)
    *   [Custom Base Model](#custom-base-model)
    *   [Decouple Pydantic BaseSettings](#decouple-pydantic-basesettings)
*   [Dependencies](#dependencies)
    *   [Beyond Dependency Injection](#beyond-dependency-injection)
    *   [Chain Dependencies](#chain-dependencies)
    *   [Decouple & Reuse dependencies. Dependency calls are cached](#decouple--reuse-dependencies-dependency-calls-are-cached)
    *   [Prefer async dependencies](#prefer-async-dependencies)
*   [Miscellaneous](#miscellaneous)
    *   [Follow the REST](#follow-the-rest)
    *   [FastAPI response serialization](#fastapi-response-serialization)
    *   [If you must use sync SDK, then run it in a thread pool.](#if-you-must-use-sync-sdk-then-run-it-in-a-thread-pool)
    *   [ValueErrors might become Pydantic ValidationError](#valueerrors-might-become-pydantic-validationerror)
    *   [Docs](#docs)
    *   [Set DB keys naming conventions](#set-db-keys-naming-conventions)
    *   [Migrations. Alembic](#migrations-alembic)
    *   [Set DB naming conventions](#set-db-naming-conventions)
    *   [SQL-first. Pydantic-second](#sql-first-pydantic-second)
    *   [Set tests client async from day 0](#set-tests-client-async-from-day-0)
    *   [Use ruff](#use-ruff)
*   [Bonus Section](#bonus-section)

## Project Structure

There are many ways to structure a project, but the best structure is one that is consistent, straightforward, and free of surprises.

Many example projects and tutorials divide the project by file type (e.g., crud, routers, models), which works well for microservices or projects with fewer scopes. However, this approach didn't fit our monolith with many domains and modules.

The structure I found more scalable and evolvable for these cases is inspired by Netflix's Dispatch, with some minor modifications.

```
 fastapi_project
 ├── alembic/
 ├── src
 │   ├── auth
 │   │   ├── router.py
 │   │   ├── schemas.py # pydantic models
 │   │   ├── models.py # db models
 │   │   ├── dependencies.py
 │   │   ├── config.py # local configs
 │   │   ├── constants.py
 │   │   ├── exceptions.py
 │   │   ├── service.py
 │   │   └── utils.py
 │   ├── aws
 │   │   ├── client.py # client model for external service communication
 │   │   ├── schemas.py
 │   │   ├── config.py
 │   │   ├── constants.py
 │   │   ├── exceptions.py
 │   │   └── utils.py
 │   └── posts
 │       ├── router.py
 │       ├── schemas.py
 │       ├── models.py
 │       ├── dependencies.py
 │       ├── constants.py
 │       ├── exceptions.py
 │       ├── service.py
 │       └── utils.py
 │   ├── config.py # global configs
 │   ├── models.py # global models
 │   ├── exceptions.py # global exceptions
 │   ├── pagination.py # global module e.g. pagination
 │   ├── database.py # db connection related stuff
 │   └── main.py
 ├── tests/
 │   ├── auth
 │   ├── aws
 │   └── posts
 ├── templates/
 │   └── index.html
 ├── requirements
 │   ├── base.txt
 │   ├── dev.txt
 │   └── prod.txt
 ├── .env
 ├── .gitignore
 ├── logging.ini
 └── alembic.ini
```

*   Store all domain directories inside `src` folder
    *   `src/` - highest level of an app, contains common models, configs, and constants, etc.
    *   `src/main.py` - root of the project, which inits the FastAPI app
*   Each package has its own `router`, `schemas`, `models`, etc.
    *   `router.py` - is a core of each module with all the endpoints
    *   `schemas.py` - for pydantic models
    *   `models.py` - for db models
    *   `service.py` - module specific business logic
    *   `dependencies.py` - router dependencies
    *   `constants.py` - module specific constants and error codes
    *   `config.py` - e.g. env vars
    *   `utils.py` - non-business logic functions, e.g. response normalization, data enrichment, etc.
    *   `exceptions.py` - module specific exceptions, e.g. `PostNotFound`, `InvalidUserData`
*   When package requires services or dependencies or constants from other packages - import them with an explicit module name
    ```python
    from src.auth import constants as auth_constants
    from src.notifications import service as notification_service
    from src.posts.constants import ErrorCode as PostsErrorCode # in case we have Standard ErrorCode in constants module of each package
    ```

## Async Routes

### I/O Intensive Tasks

FastAPI allows you to define async routes, which is a great way to handle I/O-intensive tasks without blocking the event loop. This is especially useful when dealing with external services, databases, or any other operation that involves waiting for a response.

```python
from fastapi import APIRouter


router = APIRouter()


@router.get("/posts")
async def get_posts():
    # some async db logic
    return posts
```

### CPU Intensive Tasks

However, it's important to note that async routes are not suitable for CPU-intensive tasks. This is because they can still block the event loop, preventing other requests from being processed.

If you have a CPU-intensive task, it's best to run it in a separate process or thread pool to avoid blocking the event loop. FastAPI provides a convenient way to do this using `run_in_threadpool`.

```python
from fastapi.concurrency import run_in_threadpool


def my_cpu_intensive_task():
    # some cpu intensive logic
    return result


@router.get("/posts")
async def get_posts():
    result = await run_in_threadpool(my_cpu_intensive_task)
    return result
```

## Pydantic

### Excessively use Pydantic

Pydantic is a powerful data validation library that is used extensively in FastAPI. It allows you to define data models as Python classes and validate incoming data against them.

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(min_length=3)
    email: str
```

### Custom Base Model

It's a good practice to create a custom base model that all other models inherit from. This allows you to add custom functionality to all of your models, such as converting camelCase to snake_case.

```python
from pydantic import BaseModel


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


class CustomModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
```

### Decouple Pydantic BaseSettings

FastAPI provides a convenient way to manage application settings using Pydantic's `BaseSettings`. However, it's important to decouple your settings from the FastAPI application itself. This makes it easier to test your application and reuse your settings in other contexts.

```python
# config.py
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "My App"
    db_url: str


settings = Settings()
```

## Dependencies

### Beyond Dependency Injection

FastAPI's dependency injection system is a powerful tool that can be used for more than just injecting dependencies. It can also be used to run code before a request is processed, which is useful for tasks such as authentication, logging, and database session management.

```python
from fastapi import Depends, HTTPException


async def get_current_user(token: str = Depends(oauth2_scheme)):
    # some auth logic
    return user


@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

### Chain Dependencies

Dependencies can also be chained together, allowing you to create complex dependency graphs. This is useful for creating reusable components that can be shared across multiple routes.

```python
from fastapi import Depends


async def get_db_session():
    # some db session logic
    return session


async def get_user_service(session = Depends(get_db_session)):
    return UserService(session)


@router.get("/users")
async def get_users(user_service: UserService = Depends(get_user_service)):
    return user_service.get_users()
```

### Decouple & Reuse dependencies. Dependency calls are cached

It's a good practice to decouple your dependencies from your routes. This makes it easier to test your routes and reuse your dependencies in other contexts.

```python
# dependencies.py
from fastapi import Depends


async def get_db_session():
    # some db session logic
    return session


# router.py
from fastapi import APIRouter, Depends
from . import dependencies


router = APIRouter()


@router.get("/users")
async def get_users(session = Depends(dependencies.get_db_session)):
    # some db logic
    return users
```

### Prefer async dependencies

It's a good practice to use async dependencies whenever possible. This allows you to take advantage of FastAPI's async capabilities and avoid blocking the event loop.

```python
from fastapi import Depends


async def get_db_session():
    # some async db logic
    return session


@router.get("/users")
async def get_users(session = Depends(get_db_session)):
    # some db logic
    return users
```

## Miscellaneous

### Follow the REST

When designing your API, it's a good practice to follow the principles of REST. This includes using the correct HTTP methods for each operation, using status codes to indicate the outcome of a request, and using a consistent URL structure.

### FastAPI response serialization

FastAPI automatically serializes your response data to JSON. However, you can also use a custom response class to serialize your data to other formats, such as XML or YAML.

### If you must use sync SDK, then run it in a thread pool.

If you need to use a synchronous SDK, it's important to run it in a thread pool to avoid blocking the event loop. FastAPI provides a convenient way to do this using `run_in_threadpool`.

### ValueErrors might become Pydantic ValidationError

When raising a `ValueError` inside a Pydantic model, it will be converted to a `ValidationError`. This can be useful for providing more specific error messages to your users.

### Docs

FastAPI automatically generates interactive API documentation for your application. It's a good practice to add descriptions to your routes and parameters to provide more information to your users.

### Set DB keys naming conventions

It's a good practice to set a consistent naming convention for your database keys. This makes it easier to work with your database and avoid naming conflicts.

### Migrations. Alembic

Alembic is a powerful database migration tool that is used extensively in the Python community. It allows you to manage your database schema changes in a consistent and repeatable way.

### Set DB naming conventions

It's a good practice to set a consistent naming convention for your database tables and columns. This makes it easier to work with your database and avoid naming conflicts.

### SQL-first. Pydantic-second

When designing your database schema, it's a good practice to start with the SQL schema first and then create your Pydantic models. This ensures that your Pydantic models are consistent with your database schema.

### Set tests client async from day 0

When writing tests for your FastAPI application, it's a good practice to use an async test client from day one. This allows you to take advantage of FastAPI's async capabilities and avoid blocking the event loop.

### Use ruff

Ruff is a fast Python linter that can help you to identify and fix common programming errors. It's a good practice to use a linter to ensure that your code is clean and consistent.

## Bonus Section

*   [FastAPI Pagination](https'://github.com/uriyyo/fastapi-pagination)
*   [Full Stack FastAPI PostgreSQL](https://github.com/tiangolo/full-stack-fastapi-postgresql)
*   [Awesome FastAPI](https://github.com/mjhea0/awesome-fastapi)

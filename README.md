# FastAPI Auth JWT

<p align="center">
<img src="https://raw.githubusercontent.com/deepmancer/fastapi-auth-jwt/main/fastapi_auth_jwt_logo.png" alt="FastAPI Auth JWT" style="width: 80%;">
</p>

<p align="center">
    <em>Seamless, production-ready JWT authentication for your FastAPI applications.</em>
</p>

<p align="center">
    <a href="https://github.com/deepmancer/fastapi-auth-jwt/actions" target="_blank">
        <img src="https://github.com/deepmancer/fastapi-auth-jwt/workflows/Build/badge.svg" alt="Build Status">
    </a>
    <a href="https://pypi.org/project/fastapi-auth-jwt/" target="_blank">
        <img src="https://img.shields.io/pypi/v/fastapi-auth-jwt.svg" alt="PyPI Version">
    </a>
    <a href="https://codecov.io/gh/deepmancer/fastapi-auth-jwt" target="_blank">
        <img src="https://codecov.io/gh/deepmancer/fastapi-auth-jwt/branch/main/graph/badge.svg" alt="Coverage">
    </a>
    <a href="https://github.com/deepmancer/fastapi-auth-jwt/blob/main/LICENSE" target="_blank">
        <img src="https://img.shields.io/github/license/deepmancer/fastapi-auth-jwt.svg" alt="License">
    </a>
</p>

---

| **Source Code** | **Documentation** | **PyPI** | **Live Demos** |
|:----------------|:------------------|:---------|:---------------|
| <a href="https://github.com/deepmancer/fastapi-auth-jwt" target="_blank">GitHub</a> | <a href="https://deepmancer.github.io/fastapi-auth-jwt/" target="_blank">Docs</a> | <a href="https://pypi.org/project/fastapi-auth-jwt/" target="_blank">PyPI</a> | <a href="https://github.com/deepmancer/fastapi-auth-jwt/tree/main/examples" target="_blank">Examples</a> |

---

## Table of Contents
- [🌟 Why FastAPI Auth JWT?](#-why-fastapi-auth-jwt)
- [📦 Installation](#-installation)
- [🚀 Getting Started](#-getting-started)
    - [🛠️ 1. Define a User Model](#️-1-define-a-user-model)
    - [⚙️ 2. Configure Authentication Settings](#️-2-configure-authentication-settings)
    - [🔧 3. Initialize the Authentication Backend](#-3-initialize-the-authentication-backend)
    - [🔌 4. Add Middleware to FastAPI](#-4-add-middleware-to-fastapi)
    - [📚 5. Define Your Routes](#-5-define-your-routes)
- [🧰 Redis Extension](#-redis-extension)
- [⚙️ Key Components \& Configurations](#️-key-components--configurations)
- [📂 Example Projects](#-example-projects)
- [📚 Documentation](#-documentation)
- [🛡️ License](#️-license)
- [⭐ Get Involved](#-get-involved)

---

## 🌟 Why FastAPI Auth JWT?

**FastAPI Auth JWT** empowers developers to implement secure, reliable, and efficient JWT-based authentication in their FastAPI applications. With minimal setup and deep customization options, it helps projects of all sizes establish trust, protect sensitive endpoints, and scale seamlessly. 

- 🚀 **Quick Setup**: Integrate JWT authentication into new or existing FastAPI projects in just a few lines.
- 🛠️ **Configurable & Extensible**: Easily adapt authentication rules, user schemas, and token lifetimes to meet dynamic requirements.
- 🔄 **Sync & Async Compatible**: Whether your routes are synchronous or asynchronous, the middleware and backend integrate smoothly.
- 💾 **Multiple Storage Backends**: Start with in-memory caching for simplicity, then scale transparently to Redis for high-availability, distributed architectures.
- ✅ **Thoroughly Tested & Documented**: A well-structured codebase with comprehensive tests and clear documentation means you can rely on stable, predictable behavior.

---

## 📦 Installation

**Basic Installation**:
```bash
pip install fastapi-auth-jwt
```

**With Redis Support**:
```bash
pip install fastapi-auth-jwt[redis]
```

**From Source**:
1. Clone the repository:
    ```bash
    git clone https://github.com/deepmancer/fastapi-auth-jwt.git
    ```
2. Navigate to the directory:
    ```bash
    cd fastapi-auth-jwt
    ```
3. Install the package:
    ```bash
    pip install .
    ```

**Requirements**:  
- Python 3.8+  
- FastAPI 0.65.2+  

---

## 🚀 Getting Started

Below is a high-level example to get you started. For more advanced use cases and patterns, refer to the [examples](#-example-projects) section and the [official docs](#-documentation).

### 🛠️ 1. Define a User Model
Create a simple Pydantic model representing your user entity.

```python
from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    username: str
    password: str
    token: Optional[str] = Field(None)
```

### ⚙️ 2. Configure Authentication Settings
Specify your JWT signing secrets, algorithms, and token expiration times.

```python
from pydantic import BaseModel

class AuthenticationSettings(BaseModel):
    secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    expiration_seconds: int = 3600  # 1 hour
```

### 🔧 3. Initialize the Authentication Backend
Integrate the `JWTAuthBackend` using your settings and user schema.

```python
from fastapi_auth_jwt import JWTAuthBackend

auth_backend = JWTAuthBackend(
    authentication_config=AuthenticationSettings(),
    user_schema=User
)
```

### 🔌 4. Add Middleware to FastAPI
Hook the authentication middleware into your application.

```python
from fastapi import FastAPI
from fastapi_auth_jwt import JWTAuthenticationMiddleware

app = FastAPI()

app.add_middleware(
    JWTAuthenticationMiddleware,
    backend=auth_backend,
    exclude_urls=["/sign-up", "/login"],  # Public endpoints
)
```

### 📚 5. Define Your Routes
Secure routes automatically validate tokens before accessing the request state.

```python
@app.post("/sign-up")
async def sign_up(user: User):
    # Implement user creation logic here
    return {"message": "User created"}

@app.post("/login")
async def login(user: User):
    token = await auth_backend.create_token(
        {"username": user.username, "password": user.password},
        expiration=3600
    )
    return {"token": token}

@app.get("/profile-info")
async def get_profile_info(request):
    user = request.state.user
    return {"username": user.username}

@app.post("/logout")
async def logout(request):
    user = request.state.user
    await auth_backend.invalidate_token(user.token)
    return {"message": "Logged out"}
```

---

## 🧰 Redis Extension

For production environments that require robust session management, enable Redis-backed storage:

```python
from fastapi_auth_jwt import RedisConfig, JWTAuthBackend

redis_config = RedisConfig(
    host="localhost",
    port=6379,
    db=0
)

auth_backend_redis = JWTAuthBackend(
    authentication_config=AuthenticationSettings(),
    user_schema=User,
    storage_config=redis_config,
)

app.add_middleware(
    JWTAuthenticationMiddleware,
    backend=auth_backend_redis,
    exclude_urls=["/sign-up", "/login"]
)
```

---

## ⚙️ Key Components & Configurations

**AuthenticationSettings**:  
- `secret`: JWT signing secret.  
- `jwt_algorithm`: Algorithm for token signing (default: `"HS256"`).  
- `expiration_seconds`: Token validity period in seconds.

**StorageConfig**:  
- `storage_type`: Set to `MEMORY` or `REDIS` for distributed environments.

**RedisConfig**:  
- `host`, `port`, `db`: Core Redis connection parameters.  
- `password`: Optional if your Redis server requires it.

With these configurations, you can tailor your authentication layer to match your exact operational needs—be it local development, CI/CD pipelines, or full-scale production deployments.

---

## 📂 Example Projects

Check out the [examples directory](https://github.com/deepmancer/fastapi-auth-jwt/tree/main/examples) for ready-to-run scenarios, including both standard and Redis-backed workflows. Each example demonstrates best practices for integrating JWT authentication into real-world FastAPI applications.

---

## 📚 Documentation

Extensive and continuously updated documentation is available at the [official docs](https://deepmancer.github.io/fastapi-auth-jwt/). There you will find detailed setup guides, API references, configuration tips, and troubleshooting advice.

---

## 🛡️ License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/deepmancer/fastapi-auth-jwt/blob/main/LICENSE) file for more details.

---

## ⭐ Get Involved

Your feedback and contributions are welcome! Here’s how you can support and shape the future of **FastAPI Auth JWT**:

- ⭐ **Star** this repository to stay informed and show appreciation.
- 🖇️ **Fork** the project and experiment with new ideas.
- 🐛 **Report Issues** or request enhancements via [GitHub Issues](https://github.com/deepmancer/fastapi-auth-jwt/issues).
- 🤝 **Contribute** code, documentation, or examples to help others learn and succeed.
- 📬 **Reach Out** with questions, suggestions, or integration stories.

--- 

With **FastAPI Auth JWT**, you can implement secure, stable, and scalable JWT authentication in minutes—focusing on building great features instead of reinventing authentication logic.

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from os import getenv

from fastapi import Header, HTTPException, Request
from jose import JWTError, jwt


@dataclass
class User:
    subject: str
    role: str
    permissions: set[str]
    tenant_id: str


ROLE_PERMISSIONS = {
    "executive": {"read:all", "agent:run", "workflow:run", "contract:read", "ml:score"},
    "operations": {"read:operations", "agent:run", "workflow:run", "ml:score"},
    "support": {"read:support", "agent:run", "ml:score"},
    "auditor": {"read:audit", "contract:read"},
}

RATE_BUCKETS: dict[str, list[float]] = {}
RATE_LIMIT = 120
RATE_WINDOW_SECONDS = 60


def get_current_user(authorization: str | None = Header(default=None)) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    token = authorization.replace("Bearer ", "")
    if token.startswith("demo."):
        return _demo_user(token)
    return _jwt_user(token)


def _demo_user(token: str) -> User:
    parts = token.split(".")
    role = parts[-1] if parts else ""
    tenant_id = parts[-2] if len(parts) >= 2 else "demo-tenant"
    if role not in ROLE_PERMISSIONS:
        raise HTTPException(status_code=403, detail="Unknown role")
    return User(subject="demo-user", role=role, permissions=ROLE_PERMISSIONS[role], tenant_id=tenant_id)


def _jwt_user(token: str) -> User:
    secret = getenv("JWT_SECRET", "xeip-local-dev-secret")
    issuer = getenv("JWT_ISSUER")
    audience = getenv("JWT_AUDIENCE")
    options = {"verify_aud": bool(audience), "verify_iss": bool(issuer)}
    try:
        claims = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience=audience,
            issuer=issuer,
            options=options,
        )
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid JWT") from exc
    role = claims.get("role")
    tenant_id = claims.get("tenant_id")
    subject = claims.get("sub", "jwt-user")
    if role not in ROLE_PERMISSIONS or not tenant_id:
        raise HTTPException(status_code=403, detail="JWT missing valid role or tenant")
    return User(subject=subject, role=role, permissions=ROLE_PERMISSIONS[role], tenant_id=tenant_id)


def rate_limit(request: Request) -> None:
    key = request.client.host if request.client else "unknown"
    now = time.time()
    bucket = [stamp for stamp in RATE_BUCKETS.get(key, []) if now - stamp < RATE_WINDOW_SECONDS]
    if len(bucket) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    bucket.append(now)
    RATE_BUCKETS[key] = bucket


def mask_pii(text: str) -> str:
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[email]", text)
    text = re.sub(r"\b(?:\+?\d[\d -]{7,}\d)\b", "[phone]", text)
    text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[ssn]", text)
    return text


def validate_prompt(query: str) -> dict:
    red_flags = [
        "ignore previous",
        "system prompt",
        "exfiltrate",
        "developer message",
        "bypass rbac",
        "disable security",
        "reveal hidden",
        "print secrets",
    ]
    lowered = query.lower()
    matches = [flag for flag in red_flags if flag in lowered]
    return {"allowed": not matches, "risk_flags": matches, "score": 0.22 if matches else 0.98}


def security_headers() -> dict[str, str]:
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Content-Security-Policy": "default-src 'self'",
    }

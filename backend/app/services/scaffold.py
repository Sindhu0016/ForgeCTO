"""Generate a FastAPI scaffold ZIP from project artifacts."""

from __future__ import annotations

import io
import re
import zipfile
from typing import Any


def _safe_ident(name: str, fallback: str = "Item") -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", (name or fallback).strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        cleaned = fallback
    if cleaned[0].isdigit():
        cleaned = f"T_{cleaned}"
    return cleaned


def _py_type(sql_type: str) -> str:
    t = (sql_type or "str").lower()
    if "int" in t:
        return "int"
    if "bool" in t:
        return "bool"
    if "float" in t or "numeric" in t or "decimal" in t or "double" in t:
        return "float"
    if "date" in t or "time" in t:
        return "str"
    if "uuid" in t:
        return "str"
    return "str"


def _sa_type(sql_type: str) -> str:
    t = (sql_type or "text").lower()
    if "uuid" in t:
        return "Uuid"
    if "int" in t:
        return "Integer"
    if "bool" in t:
        return "Boolean"
    if "float" in t or "numeric" in t or "decimal" in t:
        return "Float"
    if "timestamp" in t or "datetime" in t:
        return "DateTime"
    return "Text"


def build_scaffold_files(idea: str, artifacts: dict[str, Any]) -> dict[str, str]:
    arts = artifacts or {}
    schema = arts.get("database_schema") or {}
    entities = schema.get("entities") or []
    endpoints = arts.get("api_endpoints") or []
    title = (arts.get("plan") or {}).get("title") or "CTO Scaffold"
    ddl = schema.get("ddl") or "-- No DDL in pack"

    # models.py
    model_chunks = [
        '"""Auto-generated SQLAlchemy models (stubs)."""',
        "",
        "import uuid",
        "from sqlalchemy import Boolean, DateTime, Float, Integer, Text, Uuid",
        "from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column",
        "",
        "",
        "class Base(DeclarativeBase):",
        "    pass",
        "",
    ]
    for ent in entities:
        cls = _safe_ident(str(ent.get("name") or "Item").title().replace("_", ""), "Item")
        table = _safe_ident(str(ent.get("name") or "items").lower(), "items")
        model_chunks.append(f"class {cls}(Base):")
        model_chunks.append(f'    __tablename__ = "{table}"')
        fields = ent.get("fields") or [{"name": "id", "type": "uuid"}]
        for field in fields:
            fname = _safe_ident(str(field.get("name") or "field"), "field")
            sa = _sa_type(str(field.get("type") or "text"))
            if fname == "id":
                model_chunks.append(
                    f"    {fname}: Mapped[object] = mapped_column({sa}, primary_key=True, default=uuid.uuid4)"
                )
            else:
                model_chunks.append(f"    {fname}: Mapped[object | None] = mapped_column({sa}, nullable=True)")
        model_chunks.append("")

    if not entities:
        model_chunks.extend(
            [
                "class Placeholder(Base):",
                '    __tablename__ = "placeholders"',
                "    id: Mapped[object] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)",
                "",
            ]
        )

    # schemas.py
    schema_chunks = [
        '"""Auto-generated Pydantic schemas (stubs)."""',
        "",
        "from pydantic import BaseModel",
        "",
    ]
    for ent in entities or [{"name": "Placeholder", "fields": [{"name": "id", "type": "uuid"}]}]:
        cls = _safe_ident(str(ent.get("name") or "Item").title().replace("_", ""), "Item")
        schema_chunks.append(f"class {cls}Create(BaseModel):")
        fields = [f for f in (ent.get("fields") or []) if f.get("name") != "id"]
        if not fields:
            schema_chunks.append("    pass")
        for field in fields[:8]:
            fname = _safe_ident(str(field.get("name") or "field"), "field")
            schema_chunks.append(f"    {fname}: {_py_type(str(field.get('type') or 'str'))} | None = None")
        schema_chunks.append("")
        schema_chunks.append(f"class {cls}Read({cls}Create):")
        schema_chunks.append("    id: str")
        schema_chunks.append("")

    # routers
    route_chunks = [
        '"""Auto-generated FastAPI route stubs."""',
        "",
        "from fastapi import APIRouter",
        "",
        "router = APIRouter(prefix=\"/api/v1\", tags=[\"scaffold\"])",
        "",
    ]
    seen: set[str] = set()
    for ep in endpoints:
        method = str(ep.get("method") or "GET").upper()
        path = str(ep.get("path") or "/items")
        # strip /api/v1 prefix if present since router has it
        if path.startswith("/api/v1"):
            path = path[len("/api/v1") :] or "/"
        summary = str(ep.get("summary") or method + " " + path)
        fn = _safe_ident(re.sub(r"[^a-zA-Z0-9]+", "_", f"{method}_{path}").lower(), "handler")
        if fn in seen:
            fn = f"{fn}_{len(seen)}"
        seen.add(fn)
        route_chunks.append(f'@router.api_route("{path}", methods=["{method}"], summary="{summary[:80]}")')
        route_chunks.append(f"async def {fn}():")
        route_chunks.append(f'    return {{"ok": True, "stub": "{method} {path}"}}')
        route_chunks.append("")

    if not endpoints:
        route_chunks.extend(
            [
                '@router.get("/health")',
                "async def scaffold_health():",
                '    return {"ok": True}',
                "",
            ]
        )

    main_py = '''"""Minimal FastAPI app generated by ForgeCTO."""

from fastapi import FastAPI

from app.routers.api import router as api_router

app = FastAPI(title=%s, version="0.1.0")
app.include_router(api_router)


@app.get("/")
async def root():
    return {"name": %s, "docs": "/docs"}
''' % (
        repr(title),
        repr(title),
    )

    readme = f"""# {title}

Scaffold generated by **ForgeCTO** from your CTO pack.

## Idea

{idea}

## Run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

Open http://127.0.0.1:8080/docs

## Notes

- Models and routes are **stubs** derived from the Database and API tabs.
- Replace stubs with real business logic before production.

## SQL DDL (reference)

```sql
{ddl[:4000]}
```
"""

    init_app = '"""Generated ForgeCTO scaffold package."""\n'
    init_routers = '"""Routers package."""\n'

    return {
        "README.md": readme,
        "requirements.txt": "fastapi==0.115.6\nuvicorn[standard]==0.34.0\nsqlalchemy==2.0.36\npydantic==2.10.3\n",
        "app/__init__.py": init_app,
        "app/main.py": main_py,
        "app/models.py": "\n".join(model_chunks) + "\n",
        "app/schemas.py": "\n".join(schema_chunks) + "\n",
        "app/routers/__init__.py": init_routers,
        "app/routers/api.py": "\n".join(route_chunks) + "\n",
    }


def build_scaffold_zip(idea: str, artifacts: dict[str, Any]) -> bytes:
    files = build_scaffold_files(idea, artifacts)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, content in files.items():
            zf.writestr(path, content)
    return buf.getvalue()

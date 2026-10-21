import hmac
import json
import os
import re
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Request, Response, Header, HTTPException
from fastapi.responses import JSONResponse
from vercel import blob

app = FastAPI()

TOKEN = os.environ.get("ADMIN_TOKEN") or "change-me-in-production"
PSEUDO_RE = re.compile(r"^[a-z0-9_-]{2,20}$")
MAX_BODY = 1_000_000
SAVES_PREFIX = "saves/"

def is_admin(authorization: Optional[str]) -> bool:
    if not authorization:
        return False
    return hmac.compare_digest(authorization, f"Bearer {TOKEN}")

def valid_pseudo(p: str) -> bool:
    return bool(PSEUDO_RE.fullmatch(p.lower()))

@app.get("/api/save/{pseudo}")
async def get_save(pseudo: str):
    p = pseudo.lower()
    if not valid_pseudo(p):
        return JSONResponse({"erreur": "pseudo invalide"}, status_code=400)

    pathname = f"{SAVES_PREFIX}{p}.json"
    try:
        result = await blob.get_blob(pathname, access="private")
        data = json.loads(result.body.decode("utf-8"))
        return JSONResponse(data)
    except Exception:
        return JSONResponse({"erreur": "aucune sauvegarde"}, status_code=404)

@app.put("/api/save/{pseudo}")
async def put_save(pseudo: str, request: Request):
    p = pseudo.lower()
    if not valid_pseudo(p):
        return JSONResponse({"erreur": "pseudo invalide"}, status_code=400)

    body = await request.body()
    if not body or len(body) > MAX_BODY:
        return JSONResponse({"erreur": "taille invalide"}, status_code=413)

    try:
        d = json.loads(body)
        if not isinstance(d, dict) or not isinstance(d.get("sets"), dict):
            raise ValueError()
    except Exception:
        return JSONResponse({"erreur": "JSON invalide"}, status_code=400)

    pathname = f"{SAVES_PREFIX}{p}.json"
    await blob.put_blob(
        pathname,
        body,
        access="private",
        content_type="application/json",
        add_random_suffix=False,
        allow_overwrite=True,
    )
    return Response(status_code=204)

@app.get("/api/admin/saves")
async def admin_saves(authorization: Optional[str] = Header(None)):
    if not is_admin(authorization):
        return JSONResponse({"erreur": "accès refusé"}, status_code=403)

    sauvegardes = []
    try:
        async for b in blob.query_blobs(prefix=SAVES_PREFIX):
            name = b.pathname.removeprefix(SAVES_PREFIX)
            if not name.endswith(".json"):
                continue
            p = name[:-5]
            if not valid_pseudo(p):
                continue
            try:
                result = await blob.get_blob(b.pathname, access="private")
                data = json.loads(result.body.decode("utf-8"))
                maj = getattr(b, "uploaded_at", None) or datetime.now(timezone.utc).isoformat(timespec="seconds")
                if hasattr(maj, "isoformat"):
                    maj = maj.isoformat(timespec="seconds")
                sauvegardes.append({"pseudo": p, "updated": str(maj), "data": data})
            except Exception:
                continue
    except Exception:
        pass

    sauvegardes.sort(key=lambda s: s["updated"], reverse=True)
    return JSONResponse({"saves": sauvegardes})

@app.delete("/api/admin/saves/{pseudo}")
async def admin_delete_save(pseudo: str, authorization: Optional[str] = Header(None)):
    if not is_admin(authorization):
        return JSONResponse({"erreur": "accès refusé"}, status_code=403)

    p = pseudo.lower()
    if not valid_pseudo(p):
        return JSONResponse({"erreur": "pseudo invalide"}, status_code=400)

    pathname = f"{SAVES_PREFIX}{p}.json"
    try:
        await blob.head_blob(pathname)  # delete_blob réussit même si le blob n'existe pas : on vérifie d'abord
    except blob.BlobNotFoundError:
        return JSONResponse({"erreur": "joueur introuvable"}, status_code=404)

    await blob.delete_blob(pathname)
    return Response(status_code=204)

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
OUTPUT_DIR = os.path.dirname(BACKEND_DIR)

for p in [CURRENT_DIR, BACKEND_DIR, OUTPUT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend.app.config import settings
    from backend.app.database import init_db
    from backend.app.schemas import HealthResponse
    from backend.app.routers import auth, tokens, viral_lab, scripts, tts, storyboard, kanban, media
    from backend.app.mcp.server import mcp_server
except ImportError:
    from app.config import settings
    from app.database import init_db
    from app.schemas import HealthResponse
    from app.routers import auth, tokens, viral_lab, scripts, tts, storyboard, kanban, media
    from app.mcp.server import mcp_server

STATIC_DIR = os.path.join(OUTPUT_DIR, "static")
FRONTEND_DIR = os.path.join(OUTPUT_DIR, "front-clonado")

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(os.path.join(STATIC_DIR, "audio"), exist_ok=True)
    os.makedirs(os.path.join(STATIC_DIR, "previews"), exist_ok=True)
    await init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="API do DarkLAB AI Studio Reconstruído (Fases 1 a 6)",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão dos Routers do Núcleo
app.include_router(auth.router)
app.include_router(tokens.router)
app.include_router(viral_lab.router)
app.include_router(scripts.router)
app.include_router(tts.router)
app.include_router(storyboard.router)
app.include_router(kanban.router)
app.include_router(media.router)

# --- MCP ENDPOINTS ---
@app.get("/api/mcp/tools", tags=["MCP Server"])
async def list_mcp_tools():
    return {"tools": mcp_server.list_tools()}

@app.post("/api/mcp/call", tags=["MCP Server"])
async def call_mcp_tool(req: dict):
    name = req.get("name", "")
    arguments = req.get("arguments", {})
    return mcp_server.call_tool(name, arguments)

# --- HEALTH CHECK ---
@app.get("/api/health", response_model=HealthResponse, tags=["Monitoramento"])
async def health_check():
    return HealthResponse(
        status="ok",
        app=settings.APP_NAME,
        version="1.0.0",
        environment=settings.APP_ENV,
        database="sqlite_async"
    )

# --- STUBS DE PERFUMARIA (200 com shape válido) ---
@app.post("/public/waitlist", tags=["Perfumaria"])
async def public_waitlist(req: dict):
    return {"success": True, "message": "Cadastrado na lista de espera."}

@app.get("/public/platform-settings", tags=["Perfumaria"])
async def platform_settings():
    return {"maintenance": False, "version": "1.0.0", "features": {"viral_lab": True, "tts": True}}

@app.get("/public/locale", tags=["Perfumaria"])
async def public_locale():
    return {"locale": "pt-BR", "supported": ["pt-BR", "en"]}

@app.post("/affiliate/me/referrer", tags=["Perfumaria"])
async def affiliate_referrer(req: dict):
    return {"status": "attached", "referrer": None}

@app.get("/affiliate/capture", tags=["Perfumaria"])
async def affiliate_capture(ref: str = "", visit: str = ""):
    return {"status": "captured", "ref": ref}

# Arquivos Estáticos (relativos)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Frontend SPA integrado (relativo)
if os.path.exists(FRONTEND_DIR):
    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

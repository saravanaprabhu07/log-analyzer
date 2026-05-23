"""
Intelligent Log Analyzer
A lightweight, REST API-based system for parsing, analyzing, and categorizing server logs

Author: B.Sc. Computer Science Student
Version: 1.0.0
License: MIT
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from core.logger import get_logger
from models.database import init_db
from routes.logs import router as logs_router
from middleware import setup_middleware, setup_exception_handlers

# Initialize logging
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown tasks"""
    logger.info("=" * 70)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug Mode: {settings.debug}")
    logger.info(f"Database: {settings.database_url}")
    logger.info("=" * 70)

    try:
        init_db()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

    yield

    logger.info(f"Shutting down {settings.app_name}")

# Create FastAPI application
app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    description="""
    # Intelligent Log Analyzer REST API

    A lightweight, production-ready REST API for intelligent log analysis and categorization.

    ## Features
    - 📤 **File Upload**: Upload server logs via REST API
    - 🔍 **Automatic Parsing**: Multi-format log parsing with regex patterns
    - 📊 **Error Categorization**: Automatic classification of errors into categories
    - ⚕️ **Health Score**: System health scoring algorithm
    - 💾 **Persistent Storage**: SQLite database with historical data
    - 📈 **Statistics & Analytics**: Comprehensive log statistics and trend analysis
    - 🔐 **Secure**: Input validation, error handling, and logging
    - 📚 **API Documentation**: Interactive Swagger UI

    ## Quick Start
    1. Upload a log file via `/api/v1/logs/upload`
    2. Retrieve analysis via `/api/v1/logs/analysis/{log_file_id}`
    3. Query statistics via `/api/v1/logs/stats`

    ## Supported Log Formats
    - Standard format (YYYY-MM-DD HH:MM:SS LEVEL MESSAGE)
    - Apache format
    - Syslog format
    - JSON logs

    ## Health Score Calculation
    ```
    Health Score = (Good Logs / Total Logs) × 100 - Error Penalty - Warning Penalty
    Where:
    - Good Logs = INFO + DEBUG entries
    - Error Penalty = (ERROR count / total) × 30
    - Warning Penalty = (WARNING count / total) × 10
    ```

    ## Error Categories
    - **Database**: Connection, query, and database-related errors
    - **Network**: Network connectivity and socket errors
    - **Authentication**: Auth and permission-related errors
    - **File System**: File and directory access errors
    - **API**: API and HTTP-related errors
    - **Memory**: Out-of-memory and memory allocation errors
    - **Configuration**: Configuration and parameter errors
    - **Performance**: Timeout and performance-related issues
    - **System**: System and kernel-level errors
    """,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "Logs",
            "description": "Log file upload, retrieval, and analysis endpoints",
        },
        {
            "name": "Health",
            "description": "System and application health endpoints",
        },
    ],
)


# CORS Middleware
# If wildcard origin is allowed, do not allow credentials for security
_allow_credentials = (
    settings.allow_credentials if "*" not in settings.allowed_origins else False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup custom middleware
setup_middleware(app)

# Setup exception handlers
setup_exception_handlers(app)


# API Endpoints
@app.get("/", response_class=HTMLResponse, tags=["Root"])
def root() -> str:
    """Root endpoint - landing page for the dashboard."""
    return """
    <!DOCTYPE html>
    <html lang=\"en\">
      <head>
        <meta charset=\"UTF-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
        <title>Intelligent Log Analyzer</title>
        <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
        <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
        <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap\" rel=\"stylesheet\">
        <style>
          :root {
            color-scheme: dark;
            color: #0f172a;
            background: radial-gradient(circle at top, #eff6ff 0%, #f8fbff 40%, #e2e8f0 100%);
            font-family: 'Inter', system-ui, sans-serif;
          }
          * { box-sizing: border-box; }
          body { margin: 0; padding: 0; }
          .page { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 40px 24px; }
          .card { width: 100%; max-width: 1100px; background: rgba(255,255,255,0.96); border-radius: 32px; box-shadow: 0 40px 120px rgba(15,23,42,0.11); overflow: hidden; border: 1px solid rgba(15,23,42,0.08); }
          .hero { display: grid; grid-template-columns: 1fr 380px; gap: 32px; padding: 50px; }
          .hero h1 { margin: 0; font-size: clamp(3rem, 4vw, 4.8rem); line-height: 1.02; letter-spacing: -0.05em; }
          .hero p { margin: 24px 0 0; font-size: 1.05rem; line-height: 1.85; color: #475569; max-width: 680px; }
          .buttons { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 32px; }
          .button { display: inline-flex; align-items: center; justify-content: center; min-width: 170px; padding: 15px 22px; border-radius: 14px; font-weight: 700; text-decoration: none; transition: transform 0.2s ease, box-shadow 0.2s ease; }
          .button.primary { background: linear-gradient(135deg, #2563eb 0%, #22d3ee 100%); color: #fff; }
          .button.secondary { background: #eef2ff; color: #0f172a; }
          .button:hover { transform: translateY(-2px); box-shadow: 0 18px 40px rgba(37,99,235,0.18); }
          .summary { display: grid; gap: 18px; grid-template-columns: repeat(2, minmax(0, 1fr)); margin: 0; padding: 0 10px; list-style: none; }
          .summary li { background: #f8fbff; border: 1px solid #dbeafe; border-radius: 20px; padding: 20px; color: #334155; }
          .summary strong { display: block; margin-bottom: 8px; font-size: 0.95rem; color: #1d4ed8; }
          .hero-sidebar { padding: 28px; border-radius: 28px; background: linear-gradient(180deg, rgba(59,130,246,0.14), rgba(255,255,255,0.85)); box-shadow: inset 0 0 0 1px rgba(59,130,246,0.08); }
          .hero-sidebar h2 { margin-top: 0; font-size: 1.4rem; }
          .hero-sidebar p { margin: 14px 0 0; color: #334155; line-height: 1.7; }
          .feature-grid { display: grid; gap: 18px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); padding: 40px 50px 48px; background: #f8fafc; }
          .feature-card { border-radius: 24px; padding: 24px; background: #fff; border: 1px solid #e2e8f0; box-shadow: 0 10px 30px rgba(15,23,42,0.06); }
          .feature-card h3 { margin-top: 0; font-size: 1.05rem; }
          .feature-card p { margin: 12px 0 0; color: #475569; line-height: 1.7; }
          @media (max-width: 900px) {
            .hero { grid-template-columns: 1fr; padding: 32px 24px; }
            .hero-sidebar { padding: 22px; }
          }
        </style>
      </head>
      <body>
        <div class=\"page\">
          <div class=\"card\">
            <div class=\"hero\">
              <div>
                <span class=\"eyebrow\" style=\"display:inline-flex;padding:10px 16px;border-radius:999px;background:#e0f2fe;color:#0369a1;font-weight:700;text-transform:uppercase;letter-spacing:.12em;font-size:.8rem;\">Intelligent Log Analyzer</span>
                <h1>Smart log monitoring, analytics, and troubleshooting in one dashboard</h1>
                <p>Upload server logs, track health scores, detect error trends, and inspect recent events through a polished centralized interface.</p>
                <div class=\"buttons\">
                  <a class=\"button primary\" href=\"/app/\">Open Dashboard</a>
                  <a class=\"button secondary\" href=\"/docs\">View API Docs</a>
                </div>
                <ul class=\"summary\">
                  <li><strong>Live Uploads</strong> Drag and drop log file upload with instant parsing.</li>
                  <li><strong>Insights</strong> Health score, severity trends, and analytics at a glance.</li>
                  <li><strong>Search</strong> Filter logs and find issues by keyword and time range.</li>
                  <li><strong>Persistent</strong> SQLite storage for historical log analysis.</li>
                </ul>
              </div>
              <div class=\"hero-sidebar\">
                <h2>Get started fast</h2>
                <p>Open the dashboard to upload logs, review system health, and visualize error categories. Use the API docs for programmatic integration.</p>
              </div>
            </div>
            <div class=\"feature-grid\">
              <div class=\"feature-card\">
                <h3>Upload & Parse</h3>
                <p>Send log files via the UI or API and automatically parse entries into structured records.</p>
              </div>
              <div class=\"feature-card\">
                <h3>Health Monitoring</h3>
                <p>View a system health score driven by error, warning, and info event ratios.</p>
              </div>
              <div class=\"feature-card\">
                <h3>Error Trends</h3>
                <p>Discover emerging issues with trends, categories, and metrics across logs.</p>
              </div>
              <div class=\"feature-card\">
                <h3>Fast API</h3>
                <p>Access a robust REST API for uploads, search, analytics, and status checks.</p>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>
    """


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint for monitoring

    Returns service status and database connectivity
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "connected",
        "environment": settings.environment,
    }


@app.get("/api/v1/health", tags=["Health"])
def api_health():
    """API v1 health endpoint"""
    return {
        "status": "healthy",
        "api_version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Mount frontend static assets
app.mount(
    "/app",
    StaticFiles(directory="frontend", html=True),
    name="frontend",
)

# Include routers
app.include_router(
    logs_router,
    prefix=f"{settings.api_v1_prefix}/logs",
    tags=["Logs"],
)


# Custom OpenAPI schema
def custom_openapi():
    """Customize OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
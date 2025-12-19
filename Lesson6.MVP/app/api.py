from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.config import get_settings
from database.database import init_db
from routes.home import home_route
from routes.user import user_route
from routes.prediction import prediction_route
from routes.ml import ml_route
import uvicorn
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc"

    )


    app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    app.include_router(home_route, tags=['Home']) 
    app.include_router(user_route, prefix='/api/users', tags=['Users']) 
    app.include_router(prediction_route, prefix='/api/predictions', tags=['Predictions'])
    app.include_router(ml_route, prefix='/api/ml', tags=['ML'])

    return app

app = create_application()

@app.on_event("startup")
def on_startup():
    try:
        logger.info('Initialization database...')
        init_db()
        logger.info('Application startup completed successfully')
    except Exception as e:
        logger.error(f"Startup FAILED: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    logger.info('Application shutting down...')

if __name__ == '__main__':
    uvicorn.run(
        'api:app',
        host='0.0.0.0',
        port=8080,
        #reload=True,
        log_level="info"
    )
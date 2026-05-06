# ---- Imports ---- #
from celery import Celery
from src.core.di.settings import get_settings

# ---- Settings ---- #
settings = get_settings()



# ---- Celery Instance ---- #
celery_app = Celery(
    main=settings.app_name,
    broker=settings.redis_broker_url,
    backend=settings.redis_backend_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

## ---- Autodiscover Tasks ---- #
celery_app.autodiscover_tasks(
    ["src.infra.queue"]
)
from celery import Celery

celery_app = Celery(
    "cognicortrx",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

# Task Imports
import app.workers.tasks
import app.workers.workflow_executor
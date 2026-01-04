from app.workers.celery_app import celery_app
import time

@celery_app.task(name="task_process_example")
def process_task(task_id: int):
    print(f"Starting background processing for task {task_id}")
    time.sleep(5)
    print(f"Task {task_id} finished procesing")
    return {"task_id": task_id, "status": "done"}
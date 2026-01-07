from app.workers.celery_app import celery_app
import time

@celery_app.task(name="task_process_one")
def task_process_one(*args, **kwargs):
    print("Task 1 started")
    time.sleep(2)
    print("Task 1 finished")

@celery_app.task(name="task_process_two")
def task_process_two(*args, **kwargs):
    print("Task 2 started")
    import time; time.sleep(2)
    print("Task 2 finished")

@celery_app.task(name="task_process_three")
def task_process_three(*args, **kwargs):
    print("Task 3 started")
    time.sleep(2)
    print("Task 3 finished")

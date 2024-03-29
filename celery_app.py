import os
from celery.result import AsyncResult
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TutorToolkit.settings')

app = Celery('TutorToolkit')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


def delete_task(task_id):
    app.control.revoke(task_id)
    result = AsyncResult(task_id)
    return result.status


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

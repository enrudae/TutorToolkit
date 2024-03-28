import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TutorToolkit.settings')

app = Celery('TutorToolkit')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


def delete_task(task_id):
    print(task_id)
    app.control.revoke(task_id, terminate=True)
    res = app.control.revoke(task_id, terminate=True, signal='SIGKILL')
    print(res)
    return res


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

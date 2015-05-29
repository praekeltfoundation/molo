from django.shortcuts import render, redirect
from django.http import HttpResponse

from celery_app.tasks import add
from celery.result import AsyncResult


def create_task(request):
    if request.method == 'POST':
        task = add.delay(request.POST['x'], request.POST['y'])
        print task
        return redirect('task_result', task_id=task.task_id)
    return render(request, 'create_task.html', {})


def task_result(request, task_id):
    result = AsyncResult(task_id)
    if result.ready():
        return HttpResponse('Result is: %s' % (result.result,))
    else:
        return HttpResponse('Result is not ready yet!')

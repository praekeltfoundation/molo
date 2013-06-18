from django.conf.urls import patterns, include, url

from celery_app import views


urlpatterns = patterns('',
    url(r'^$', views.create_task),
    url(r'^result/(?P<task_id>.+)/$', views.task_result, name='task_result'),
)

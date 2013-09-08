from django.conf.urls import patterns, url
from scheduler import views

urlpatterns = patterns('',
    url(r'^$', views.scheduleMsg, name='schedulemsg')
)
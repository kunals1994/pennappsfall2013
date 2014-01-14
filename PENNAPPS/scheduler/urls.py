from django.conf.urls import patterns, url
from scheduler import views

urlpatterns = patterns('',
	url(r'process/', views.process, name='process')
)
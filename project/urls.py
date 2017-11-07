"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required
from django.conf.urls.static import static
from project import settings
from log import views as myapp_views
from twitter_analysis import views as twitter_views
from reddit_analysis import views as reddit_views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',myapp_views.home,name='home'),
    url(r'^signup/',myapp_views.signup,name='signup'),
    url(r'^loggedin/',myapp_views.loggedin,name='loggedin'),
    url(r'^signin/',myapp_views.signin,name='signin'),
    url(r'^user/',myapp_views.user,name='user'),
    url(r'^logout/',myapp_views.logout_view,name='logout_view'),
    url(r'^twitter-analysis/',twitter_views.twitter_detailed_analysis,name='twitter_detailed_analysis'),
    url(r'^reddit-analysis/',reddit_views.reddit_detailed_analysis,name='reddit_detailed_analysis'),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns+=staticfiles_urlpatterns()

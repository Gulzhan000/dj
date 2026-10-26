from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('blog/create/', views.blog_create, name='create'),
    path('blog/<int:pk>/edit/', views.blog_update, name='update'),
    path('blog/<int:pk>/delete/', views.blog_delete, name='delete'),
    path('', views.blog_list, name='list'),
    path('blog/<int:pk>/', views.blog_detail, name='detail'),
]

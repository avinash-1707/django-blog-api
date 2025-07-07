from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    
    # Posts
    path('create-post/', views.create_post, name='create_post'),
    path('posts/', views.get_posts, name='get_posts'),
    path('post/<str:post_id>/', views.get_post_detail, name='get_post_detail'),
    
    # Comments
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
]
from django.urls import path

from . import views


app_name = 'blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('author/<int:author_id>', views.AuthorView.as_view(), name='author'),
    path('post/new', views.CreateView.as_view(), name='create'),
    path('post/details/<int:post_id>', views.DetailView.as_view(), name='details'),
    path('post/edit/<int:post_id>', views.UpdateView.as_view(), name='edit'),
    path('post/<int:post_id>/vote/<int:direction>', views.cast_vote, name='vote'),
]

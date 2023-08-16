from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'blog'

urlpatterns = [
     path('', views.IndexListView.as_view(), name='index'),
     path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
     path('posts/<int:id>/', views.PostDetailView.as_view(),
          name='post_detail'),
     path('posts/<int:post_id>/edit/', views.EditPostView.as_view(),
          name='edit_post'),
     path('posts/<int:post_id>/delete/', views.DeletePostView.as_view(),
          name='delete_post'),
     path('category/<slug:category_slug>/',
          views.CategoryPostsListView.as_view(), name='category_posts'),
     path('profile/<slug:username>/edit/',
          views.EditProfileListView.as_view(), name='edit_profile'),
     path('profile/<slug:username>/',
          views.ProfileListView.as_view(), name='profile'),
     path('posts/<int:post_id>/comment/',
          views.CommentCreateView.as_view(), name='add_comment'),
     path('posts/<int:post_id>/edit_comment/<comment_id>/',
          views.CommentUpdateView.as_view(), name='edit_comment'),
     path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
          views.CommentDeleteView.as_view(), name='delete_comment'),
     ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

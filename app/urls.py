from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .forms import LoginForm

urlpatterns = [

    # ==================================================
    # HOME & BLOG BROWSING
    # ==================================================
    path('', views.home, name='home'),

    path('category/<slug:slug>/', views.category_view, name='category'),

    path('author/<str:username>/', views.author_profile, name='author_profile'),

    path('profile/', views.profile_view, name='profile'),

    path('ai-generate/', views.generate_ai_blog, name='ai_generate'),

    path('about/', views.about, name='about'),

    path('search/', views.search, name='search'),

    path('ai-detection/', views.ai_detection, name='ai_detection'),

    path('humanize/', views.humanize_content, name='humanize_content'),

    path('ai-generate-stream/', views.generate_ai_blog_stream, name='ai_generate_stream'),


    # ==================================================
    # BLOG CRUD (LOGIN REQUIRED)
    # ⚠️ ORDER MATTERS (slug LAST)
    # ==================================================
    path('blog/create/', views.CreateBlogView.as_view(), name='create_blog'),

    path('blog/edit/<int:pk>/', views.UpdateBlogView.as_view(), name='edit_blog'),

    path('blog/delete/<int:pk>/', views.DeleteBlogView.as_view(), name='delete_blog'),

    # 🔴 ALWAYS KEEP SLUG ROUTE LAST
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),


    # ==================================================
    # INTERACTIONS
    # ==================================================
    path('blog/like/<int:blog_id>/', views.toggle_like, name='blog_like'),
    path('blog/comment/<int:blog_id>/', views.add_comment, name='add_comment'),
    path('comment/reply/<int:comment_id>/', views.reply_comment, name='reply_comment'),


    # ==================================================
    # AUTHENTICATION
    # ==================================================
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='blog/login.html',
            authentication_form=LoginForm,
            redirect_authenticated_user=True
        ),
        name='login'
    ),

    path('logout/', views.logout_view, name='logout'),

    path('register/', views.RegisterUserView.as_view(), name='register'),


    # ==================================================
    # PASSWORD MANAGEMENT
    # ==================================================
    path(
        'password-change/',
        auth_views.PasswordChangeView.as_view(
            template_name='blog/passwordchange.html',
            success_url='/password-change-done/'
        ),
        name='password_change'
    ),

    path(
        'password-change-done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='blog/passwordchangedone.html'
        ),
        name='password_change_done'
    ),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='blog/password_reset.html'
        ),
        name='password_reset'
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='blog/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='blog/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),

    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='blog/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]

# ==================================================
# MEDIA FILES (DEVELOPMENT ONLY)
# ==================================================
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

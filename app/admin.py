from django.contrib import admin
from .models import (
    UserProfile,
    Category,
    BlogPost,
    Comment,
    BlogLike,
    BlogView,
    TeamMember
)

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'role']   # 🔥 ADD user
    search_fields = ['name', 'user__username']
    raw_id_fields = ['user']  # 🔥 IMPORTANT (clean UI)

# ===============================
# USER PROFILE
# ===============================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'website')
    search_fields = ('user__username',)
    raw_id_fields = ('user',)


# ===============================
# CATEGORY
# ===============================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    ordering = ('name',)


# ===============================
# BLOG POST
# ===============================
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'author',
        'category',
        'created_at',
        'status',
        'is_featured',
    )

    list_filter = (
        'status',
        'category',
        'is_featured',
        'created_at',
    )

    search_fields = (
        'title',
        'content',
        'author__username',
    )

    ordering = ('-created_at',)

    list_editable = (
        'status',
        'is_featured',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    raw_id_fields = ('author',)

    fieldsets = (
        ('Blog Info', {
            'fields': ('title', 'slug', 'category', 'author')
        }),
        ('Content', {
            'fields': ('featured_image', 'content')
        }),
        ('Publication', {
            'fields': ('status', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


# ===============================
# COMMENTS
# ===============================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'blog',
        'user',
        'is_approved',
        'created_at',
    )

    list_filter = (
        'is_approved',
        'created_at',
    )

    search_fields = (
        'comment',
        'user__username',
        'blog__title',
    )

    list_editable = ('is_approved',)

    ordering = ('-created_at',)

    raw_id_fields = ('blog', 'user')


# ===============================
# BLOG LIKES
# ===============================
@admin.register(BlogLike)
class BlogLikeAdmin(admin.ModelAdmin):
    list_display = (
        'blog',
        'user',
        'liked_at',
    )

    search_fields = (
        'blog__title',
        'user__username',
    )

    ordering = ('-liked_at',)

    raw_id_fields = ('blog', 'user')


# ===============================
# BLOG VIEWS
# ===============================
@admin.register(BlogView)
class BlogViewAdmin(admin.ModelAdmin):
    list_display = (
        'blog',
        'ip_address',
        'viewed_at',
    )

    list_filter = ('viewed_at',)

    search_fields = (
        'blog__title',
        'ip_address',
    )

    ordering = ('-viewed_at',)

    raw_id_fields = ('blog',)

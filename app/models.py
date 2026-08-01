from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


# ===============================
# USER PROFILE
# ===============================
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # 🔥 NEW FIELDS
    age = models.PositiveIntegerField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username


# 🔥 AUTO CREATE PROFILE
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# ===============================
# BLOG CATEGORY
# ===============================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ===============================
# BLOG POST
# ===============================
class BlogPost(models.Model):

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blogs"
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="blogs"
    )

    title = models.CharField(max_length=250)

    slug = models.SlugField(unique=True, blank=True)

    content = models.TextField()

    featured_image = models.ImageField(
        upload_to="blogs/",
        blank=True,
        null=True
    )

    video = models.FileField(        # optional video
        upload_to="blog_videos/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )

    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):

        if not self.slug:
            unique_id = uuid.uuid4().hex[:6]
            self.slug = f"{slugify(self.title)}-{unique_id}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# ===============================
# COMMENTS
# ===============================
class Comment(models.Model):
    blog = models.ForeignKey(
        BlogPost,
        related_name='comments',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )

    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_reply(self):
        return self.parent is not None


# ===============================
# BLOG LIKES
# ===============================
class BlogLike(models.Model):
    blog = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blog', 'user')
        ordering = ['-liked_at']

    def __str__(self):
        return f"{self.user.username} liked {self.blog.title}"


# ===============================
# BLOG VIEW COUNT
# ===============================
class BlogView(models.Model):
    blog = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="views"
    )
    ip_address = models.GenericIPAddressField()
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blog', 'ip_address')
        ordering = ['-viewed_at']

    def __str__(self):
        return f"View on {self.blog.title}"

class TeamMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # 🔥 ADD THIS
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=5)
    role = models.CharField(max_length=100)
    image = models.ImageField(upload_to='team/', blank=True, null=True)

    def __str__(self):
        return self.name
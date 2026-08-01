from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count
from django.contrib.auth.models import User
from .ollama_client import generate_blog
from django.http import JsonResponse
import requests
from .utils import check_duplicate_blog
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
import re
from django.http import StreamingHttpResponse
from .ollama_client import generate_blog_stream

from .models import (
    BlogPost,
    Category,
    Comment,
    BlogLike,
    BlogView,
    TeamMember,
)
from .forms import BlogPostForm, RegisterUserForm, CommentForm


# ========================= HOME =========================
def home(request):
    blogs = (
        BlogPost.objects
        .filter(status='PUBLISHED')
        .annotate(
            total_likes=Count('likes', distinct=True),
            total_comments=Count('comments', distinct=True)
        )
        .order_by('-created_at')
    )

    categories = Category.objects.all()

    return render(request, 'blog/home.html', {
        'blogs': blogs,
        'categories': categories
    })

def about(request):
    team = TeamMember.objects.all()
    return render(request, 'blog/about.html', {'team': team})



# ========================= CATEGORY =========================
def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)

    blogs = BlogPost.objects.filter(
        category=category,
        status='PUBLISHED'
    ).order_by('-created_at')

    return render(request, 'blog/category.html', {
        'category': category,
        'blogs': blogs
    })


# ========================= BLOG DETAIL =========================
def blog_detail(request, slug):
    blog = get_object_or_404(
        BlogPost,
        slug=slug,
        status='PUBLISHED'
    )

    # View count (IP based)
    ip = request.META.get('REMOTE_ADDR', '')
    BlogView.objects.get_or_create(blog=blog, ip_address=ip)

    comments = blog.comments.filter(is_approved=True)

    is_liked = False
    if request.user.is_authenticated:
        is_liked = BlogLike.objects.filter(
            blog=blog,
            user=request.user
        ).exists()

    comment_form = CommentForm()

    return render(request, 'blog/blog_detail.html', {
        'blog': blog,
        'comments': comments,
        'is_liked': is_liked,
        'comment_form': comment_form
    })


# ========================= CREATE BLOG =========================
@method_decorator(login_required, name='dispatch')
class CreateBlogView(CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/create_blog.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):

        # 🔥 HANDLE NEW CATEGORY FIRST
        new_cat = form.cleaned_data.get('new_category')

        if new_cat and new_cat.strip() != "":
            category, created = Category.objects.get_or_create(name=new_cat.strip().title())
            form.instance.category = category

        # EXISTING LOGIC (KEEP SAME)
        form.instance.author = self.request.user

        new_content = form.cleaned_data.get("content")

        # 🔥 AI DETECTION BLOCK
        sentences = re.split(r'(?<=[.!?]) +', new_content)

        ai_score = 0

        for sentence in sentences:
            score = 0
            if len(sentence) > 120:
                score += 1
            if sentence.count(",") >= 3:
                score += 1
            if "moreover" in sentence.lower() or "furthermore" in sentence.lower():
                score += 1

            if score >= 2:
                ai_score += 1

        total = len(sentences) if sentences else 1
        ai_percent = round((ai_score / total) * 100, 2)

        if ai_percent > 8:
            return JsonResponse({
                "status": "error",
                "message": "Too much AI content! Please humanize.",
                "ai_percent": ai_percent
            })

        existing_blogs = BlogPost.objects.filter(
            status='PUBLISHED'
        ).values_list("content", flat=True)

        similarity_score = check_duplicate_blog(new_content, list(existing_blogs))

        percentage = round(similarity_score * 100, 2)

        if similarity_score >= 0.8:
            return JsonResponse({
                "status": "error",
                "message": "Blog rejected due to copyright!",
                "similarity": percentage
            })

        self.object = form.save()

        return JsonResponse({
            "status": "success",
            "message": "Blog published successfully!"
        })


# ========================= UPDATE BLOG =========================
@method_decorator(login_required, name='dispatch')
class UpdateBlogView(UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/edit_blog.html'

    def get_queryset(self):
        return BlogPost.objects.filter(author=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Blog updated successfully!")
        return reverse_lazy(
            'blog_detail',
            kwargs={'slug': self.object.slug}
        )


# ========================= DELETE BLOG =========================
@method_decorator(login_required, name='dispatch')
class DeleteBlogView(DeleteView):
    model = BlogPost
    template_name = 'blog/delete_blog.html'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        return BlogPost.objects.filter(author=self.request.user)


# ========================= LIKE (NO JS) =========================
@login_required
def toggle_like(request, blog_id):
    blog = get_object_or_404(BlogPost, id=blog_id)

    like, created = BlogLike.objects.get_or_create(
        blog=blog,
        user=request.user
    )

    if not created:
        like.delete()  # unlike

    return redirect('blog_detail', slug=blog.slug)


# ========================= ADD COMMENT =========================
@login_required
def add_comment(request, blog_id):
    blog = get_object_or_404(BlogPost, id=blog_id)

    if request.method == "POST":
        comment_text = request.POST.get("comment")

        comment = Comment.objects.create(
            blog=blog,
            user=request.user,
            comment=comment_text
        )

        # 🔥 SEND EMAIL TO BLOG AUTHOR
        subject = f"New Comment on your blog: {blog.title}"

        message = f"""
Hi {blog.author.username},

Someone commented on your blog.

Comment:
"{comment_text}"

By: {request.user.username}

Check your blog now!
"""

        recipient_email = blog.author.email

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [recipient_email],
            fail_silently=False,
        )

        return redirect('blog_detail', slug=blog.slug)


# ========================= AUTHOR PROFILE =========================
def author_profile(request, username):
    author = get_object_or_404(User, username=username)

    blogs = BlogPost.objects.filter(
        author=author,
        status='PUBLISHED'
    ).order_by('-created_at')

    return render(request, 'blog/author_profile.html', {
        'author': author,
        'blogs': blogs
    })


# ========================= USER PROFILE =========================
@login_required
def profile_view(request):
    profile = request.user.profile

    if request.method == "POST":
        profile.bio = request.POST.get("bio") or ""
        profile.website = request.POST.get("website") or ""
        profile.age = request.POST.get("age") or None
        profile.city = request.POST.get("city") or ""
        profile.phone = request.POST.get("phone") or ""
        profile.address = request.POST.get("address") or ""

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        profile.save()
        return redirect("profile")

    return render(request, 'blog/profile.html', {"profile": profile})

# ========================= REGISTER =========================
class RegisterUserView(View):
    def get(self, request):
        form = RegisterUserForm()
        return render(request, 'blog/register.html', {'form': form})

    def post(self, request):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect('login')
        return render(request, 'blog/register.html', {'form': form})


# ========================= LOGOUT =========================
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('home')

@login_required
def reply_comment(request, comment_id):
    parent = get_object_or_404(Comment, id=comment_id)
    blog = parent.blog

    if request.user != blog.author:
        return redirect('blog_detail', slug=blog.slug)

    if request.method == 'POST':
        reply_text = request.POST.get('reply')
        if reply_text:
            Comment.objects.create(
                blog=blog,
                user=request.user,
                comment=reply_text,
                parent=parent
            )

    return redirect('blog_detail', slug=blog.slug)

#generate blog

def generate_ai_blog(request):

    if request.method == "POST":

        title = request.POST.get("title")
        category = request.POST.get("category")
        keywords = request.POST.get("keywords")

        prompt = f"""
        Write a blog post.

        Title: {title}
        Category: {category}

        Use these points:
        {keywords}
        """

        content = generate_blog(prompt)

        return JsonResponse({
            "content": content
        })
    

def search(request):
    query = request.GET.get('q')
    results = []

    if query:
        blogs = BlogPost.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(category__name__icontains=query),
            status='PUBLISHED'
        )[:10]

        for blog in blogs:
            results.append({
                'title': blog.title,
                'slug': blog.slug,
                'author': blog.author.username
            })

    return JsonResponse({'results': results})

def ai_detection(request):
    if request.method == "POST":
        content = request.POST.get("content", "")

        sentences = re.split(r'(?<=[.!?]) +', content)

        highlighted = []
        ai_score = 0

        for sentence in sentences:
            # 🔥 SIMPLE HEURISTIC (you can upgrade later)
            score = 0

            if len(sentence) > 120:
                score += 1
            if sentence.count(",") >= 3:
                score += 1
            if "moreover" in sentence.lower() or "furthermore" in sentence.lower():
                score += 1

            if score >= 2:
                ai_score += 1
                highlighted.append(f"<span style='background:#ff4d4d;color:white'>{sentence}</span>")
            else:
                highlighted.append(sentence)

        total = len(sentences) if sentences else 1
        ai_percent = round((ai_score / total) * 100, 2)

        return JsonResponse({
            "highlighted": " ".join(highlighted),
            "ai_percent": ai_percent
        })
    
def humanize_content(request):
    if request.method == "POST":
        content = request.POST.get("content", "")

        prompt = f"""
        Rewrite the following blog in a more human and natural way.

        STRICT RULES:
        - Change sentence structure completely
        - Break long sentences into smaller ones
        - Use casual tone
        - Add slight imperfections
        - Avoid formal words like 'moreover', 'furthermore'
        - Make it sound like a real student wrote it
        - DO NOT repeat original sentences

        BLOG:
        {content}
        """

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "kimi-k2.5:cloud",  # ✅ FIXED
                "prompt": prompt,
                "stream": False
            }
        )

        result = response.json()
        print("HUMANIZER RESPONSE:", result)

        if "response" not in result:
            return JsonResponse({
                "content": content,
                "error": "AI failed, try again"
            })

        generated = result.get("response", "")

        if generated.strip() == content.strip():
            return JsonResponse({
                "content": content,
                "error": "No change detected"
            })

        return JsonResponse({
            "content": generated
        })

def generate_ai_blog_stream(request):

    title = request.GET.get("title")
    category = request.GET.get("category")
    keywords = request.GET.get("keywords")

    prompt = f"""
    Write a blog post.

    Title: {title}
    Category: {category}

    Use these points:
    {keywords}
    """

    def stream():
        for chunk in generate_blog_stream(prompt):
            yield chunk

    return StreamingHttpResponse(stream(), content_type='text/plain')
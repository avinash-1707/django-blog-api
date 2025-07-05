import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from .models import Post, Comment

def json_response(data, status=200):
    """Helper function to create JSON responses"""
    return JsonResponse(data, status=status)

def get_request_data(request):
    """Helper function to parse JSON request data"""
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None

@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    """Register a new user"""
    data = get_request_data(request)
    if not data:
        return json_response({'error': 'Invalid JSON'}, 400)
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return json_response({'error': 'Missing required fields'}, 400)
    
    if User.objects.filter(username=username).exists():
        return json_response({'error': 'Username already exists'}, 400)
    
    if User.objects.filter(email=email).exists():
        return json_response({'error': 'Email already exists'}, 400)
    
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return json_response({
            'message': 'User created successfully',
            'user_id': user.id
        }, 201)
    except Exception as e:
        return json_response({'error': 'Failed to create user'}, 500)

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """Login user"""
    data = get_request_data(request)
    if not data:
        return json_response({'error': 'Invalid JSON'}, 400)
    
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return json_response({'error': 'Missing username or password'}, 400)
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return json_response({
            'message': 'Login successful',
            'user_id': user.id,
            'username': user.username
        })
    else:
        return json_response({'error': 'Invalid credentials'}, 401)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_post(request):
    """Create a new blog post"""
    data = get_request_data(request)
    if not data:
        return json_response({'error': 'Invalid JSON'}, 400)
    
    title = data.get('title')
    content = data.get('content')
    
    if not all([title, content]):
        return json_response({'error': 'Missing title or content'}, 400)
    
    try:
        post = Post.objects.create(
            author=request.user,
            title=title,
            content=content
        )
        return json_response({
            'message': 'Post created successfully',
            'post_id': post.id,
            'title': post.title,
            'created_at': post.created_at.isoformat()
        }, 201)
    except Exception as e:
        return json_response({'error': 'Failed to create post'}, 500)

@require_http_methods(["GET"])
def get_posts(request):
    """Get all posts with pagination"""
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 10)
    
    try:
        page = int(page)
        per_page = int(per_page)
        if per_page > 100:
            per_page = 100
    except ValueError:
        return json_response({'error': 'Invalid page or per_page parameter'}, 400)
    
    posts = Post.objects.select_related('author').prefetch_related('likes', 'comments')
    paginator = Paginator(posts, per_page)
    
    try:
        posts_page = paginator.page(page)
    except:
        return json_response({'error': 'Invalid page number'}, 400)
    
    posts_data = []
    for post in posts_page:
        posts_data.append({
            'id': post.id,
            'title': post.title,
            'content': post.content[:200] + '...' if len(post.content) > 200 else post.content,
            'author': post.author.username,
            'author_id': post.author.id,
            'created_at': post.created_at.isoformat(),
            'total_likes': post.total_likes(),
            'comment_count': post.total_comments()
        })
    
    return json_response({
        'posts': posts_data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_posts': paginator.count,
            'has_next': posts_page.has_next(),
            'has_previous': posts_page.has_previous()
        }
    })

@require_http_methods(["GET"])
def get_post_detail(request, post_id):
    """Get detailed view of a post with comments"""
    try:
        post = Post.objects.select_related('author').prefetch_related(
            'comments__user', 'likes'
        ).get(id=post_id)
    except Post.DoesNotExist:
        return json_response({'error': 'Post not found'}, 404)
    
    comments_data = []
    for comment in post.comments.all():
        comments_data.append({
            'id': comment.id,
            'text': comment.text,
            'user': comment.user.username,
            'user_id': comment.user.id,
            'created_at': comment.created_at.isoformat()
        })
    
    post_data = {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author.username,
        'author_id': post.author.id,
        'created_at': post.created_at.isoformat(),
        'total_likes': post.total_likes(),
        'total_comments': post.total_comments(),
        'comments': comments_data
    }
    
    return json_response({'post': post_data})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_comment(request, post_id):
    """Add a comment to a post"""
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return json_response({'error': 'Post not found'}, 404)
    
    data = get_request_data(request)
    if not data:
        return json_response({'error': 'Invalid JSON'}, 400)
    
    text = data.get('text')
    if not text:
        return json_response({'error': 'Comment text is required'}, 400)
    
    try:
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            text=text
        )
        return json_response({
            'message': 'Comment added successfully',
            'comment_id': comment.id,
            'text': comment.text,
            'user': comment.user.username,
            'user_id': comment.user.id,
            'created_at': comment.created_at.isoformat()
        }, 201)
    except Exception as e:
        return json_response({'error': f'Failed to add comment: {str(e)}'}, 500)
from django.contrib.auth import get_user_model

from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from posts.forms import CommentForm
from posts.forms import PostForm

from posts.models import Follow
from posts.models import Group
from posts.models import Post

from yatube.settings import POSTS_LIMIT

User = get_user_model()


def index(request):
    post_list = Post.objects.all()

    paginator = Paginator(post_list, POSTS_LIMIT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {
        'page': page,
        'paginator': paginator,
        'posts_limit': POSTS_LIMIT,
    })


def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_LIMIT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {
        'group': group,
        'page': page,
        'paginator': paginator
    })


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form, 'is_edit': False, })


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = get_object_or_404(
            Post,
            author__username=username,
            id=post_id
        )
        comment.author = request.user
        comment.save()
        return redirect('post_view', username, post_id)
    return render(request, 'new_comment.html', {'form': form, })


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, POSTS_LIMIT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    posts_cnt = len(posts)
    followers_cnt = len(user.follower.all())
    followings_cnt = len(user.following.all())
    if request.user.is_authenticated is True:
        context = {
            'page': page,
            'author': user,
            'posts_cnt': posts_cnt,
            'followers_cnt': followers_cnt,
            'followings_cnt': followings_cnt,
            'following': Follow.objects.filter(user=request.user, author=user),
            'paginator': paginator,
        }
    else:
        context = {
            'page': page,
            'author': user,
            'posts_cnt': posts_cnt,
            'followers_cnt': followers_cnt,
            'followings_cnt': followings_cnt,
            'paginator': paginator,
        }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author__username=username, id=post_id)
    comments_under_post = post.comments.all()
    posts_cnt = len(user.posts.all())
    form = CommentForm(request or None)
    followers_cnt = len(user.follower.all())
    followings_cnt = len(user.following.all())
    if request.user.is_authenticated is True:
        context = {
            'post': post,
            'comments': comments_under_post,
            'author': post.author,
            'posts_cnt': posts_cnt,
            'followers_cnt': followers_cnt,
            'followings_cnt': followings_cnt,
            'following': Follow.objects.filter(user=request.user, author=user),
            'form': form,
        }
    else:
        context = {
            'post': post,
            'comments': comments_under_post,
            'author': post.author,
            'posts_cnt': posts_cnt,
            'followers_cnt': followers_cnt,
            'followings_cnt': followings_cnt,
            'form': form,
        }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    edit_post = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user != edit_post.author:
        return redirect('post_view', edit_post.author, post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=edit_post
    )
    if form.is_valid():
        form.save()
        return redirect('post_view', edit_post.author, post_id)
    context = {'form': form, 'post': edit_post, 'is_edit': True, }
    return render(request, 'new_post.html', context)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, POSTS_LIMIT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    followers_cnt = len(request.user.follower.all())
    return render(request, 'follow.html', {
        'page': page,
        'followers_cnt': followers_cnt,
        'paginator': paginator,
        'posts_limit': POSTS_LIMIT,
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)

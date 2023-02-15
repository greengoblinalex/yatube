from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Post, Group, Comment
from .forms import PostForm, CommentForm
from . import constants
from .utils import get_page_obj


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.select_related(
        'author',
        'group',
    ).order_by(
        '-created',
    )

    page_obj = get_page_obj(
        request,
        post_list,
        constants.NUMBER_OF_RECENT_POSTS
    )

    context = {
        'page_obj': page_obj,
    }
    return HttpResponse(render(request, template, context))


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.filter(
        group=group,
    ).select_related(
        'author',
    ).order_by(
        '-created',
    )

    page_obj = get_page_obj(
        request,
        post_list,
        constants.NUMBER_OF_RECENT_POSTS
    )

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return HttpResponse(render(request, template, context))


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(
        author=author
    ).select_related(
        'group',
    ).order_by(
        '-created',
    )

    page_obj = get_page_obj(
        request,
        post_list,
        constants.NUMBER_OF_RECENT_POSTS
    )

    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(
        post_id=post_id
    ).select_related(
        'post'
    ).order_by(
        '-created'
    )
    form = CommentForm(request.POST or None)

    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    context = {
        'form': form,
    }

    if request.method != 'POST':
        return render(request, template, context)

    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user.username)

    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )

    context = {
        'form': form,
        'post': post,
    }

    if request.method != 'POST':
        return render(request, template, context)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    template = 'posts:post_detail'
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect(template, post_id=post_id)

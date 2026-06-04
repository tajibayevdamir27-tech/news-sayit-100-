from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Article
from .forms import ArticleForm

def article_detail_slug(request, slug):
    article = get_object_or_404(Article, slug=slug)
    article.views += 1
    article.save()
    user_liked = request.user.is_authenticated and article.likes.filter(pk=request.user.pk).exists()
    related = Article.objects.filter(category=article.category).exclude(slug=slug)[:3]
    return render(request, 'main/article_detail.html', {
        'article': article,
        'user_liked': user_liked,
        'related': related,
    })


def is_admin(user):
    return user.is_authenticated and user.is_staff


def home(request):
    category = request.GET.get('category', '')
    query = request.GET.get('q', '').strip()

    articles = Article.objects.all()

    if category:
        articles = articles.filter(category=category)
    if query:
        articles = articles.filter(title__icontains=query) | articles.filter(content__icontains=query)

    breaking = Article.objects.order_by('-views')[:3]

    paginator = Paginator(articles, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Article.CATEGORY_CHOICES

    return render(request, 'main/home.html', {
        'page_obj': page_obj,
        'breaking': breaking,
        'categories': categories,
        'selected_category': category,
        'query': query,
    })


def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.views += 1
    article.save()
    user_liked = request.user.is_authenticated and article.likes.filter(pk=request.user.pk).exists()

    related = Article.objects.filter(category=article.category).exclude(pk=pk)[:3]

    return render(request, 'main/article_detail.html', {
        'article': article,
        'user_liked': user_liked,
        'related': related,
    })


@login_required
def toggle_like(request, pk):
    if request.method == 'POST':
        article = get_object_or_404(Article, pk=pk)
        if article.likes.filter(pk=request.user.pk).exists():
            article.likes.remove(request.user)
            liked = False
        else:
            article.likes.add(request.user)
            liked = True
        return JsonResponse({'liked': liked, 'count': article.like_count})
    return JsonResponse({'error': 'Invalid'}, status=400)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        if not username or not email or not password1:
            messages.error(request, 'Qate!!!  Bos orilardi toldirin.')
        elif password1 != password2:
            messages.error(request, 'Paroller birdy emes.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Bul login bar  basqa login jazin.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            messages.success(request, f'Hosh kordik, {username}!')
            return redirect('home')
    return render(request, 'main/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Login ya parol  duris emes.')
    return render(request, 'main/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')




@user_passes_test(is_admin, login_url='/login/')
def admin_panel(request):
    articles = Article.objects.all().order_by('-created_at')
    users = User.objects.all().order_by('-date_joined')
    total_articles = articles.count()
    total_users = users.count()
    total_views = sum(a.views for a in articles)
    total_likes = sum(a.like_count for a in articles)
    return render(request, 'admin/panel.html', {
        'articles': articles,
        'users': users,
        'total_articles': total_articles,
        'total_users': total_users,
        'total_views': total_views,
        'total_likes': total_likes,
    })


@user_passes_test(is_admin, login_url='/login/')
def admin_article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Maqala  o\'shirildi!')
            return redirect('admin_panel')
    else:
        form = ArticleForm()
    return render(request, 'admin/article_form.html', {'form': form, 'action': 'Qosiw'})


@user_passes_test(is_admin, login_url='/login/')
def admin_article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Maqala yangilandi!')
            return redirect('admin_panel')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'admin/article_form.html', {'form': form, 'action': 'Ozgertiriw', 'article': article})


@user_passes_test(is_admin, login_url='/login/')
def admin_article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Maqala o\'shirildi!')
    return redirect('admin_panel')


@user_passes_test(is_admin, login_url='/login/')
def admin_give_staff(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, pk=user_id)
        if target_user == request.user:
            messages.error(request, 'Oz ozinizge admin bere almasiz.')
        else:
            target_user.is_staff = not target_user.is_staff
            target_user.save()
            status = 'berildi' if target_user.is_staff else 'alindi'
            messages.success(request, f'{target_user.username} ga admin huquqi {status}!')
    return redirect('admin_panel')


@user_passes_test(is_admin, login_url='/login/')
def admin_delete_user(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, pk=user_id)
        if target_user == request.user:
            messages.error(request, 'Ozinizdi akawitinizdi  o\'shire almaysiz.')
        else:
            target_user.delete()
            messages.success(request, f'Paydalaniwshi o\'shirildi!')
    return redirect('admin_panel')

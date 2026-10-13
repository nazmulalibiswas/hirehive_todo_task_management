import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from tasks.forms import TaskForm
from tasks.models import CustomUserInfoModel, TaskModel

logger = logging.getLogger(__name__)


def register_page(request):
    if request.user.is_authenticated:
        return redirect('home_page')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validate fields
        if not username:
            messages.error(request, 'Username is required.')
            return render(request, 'register.html')

        if not password:
            messages.error(request, 'Password is required.')
            return render(request, 'register.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'register.html')

        try:
            CustomUserInfoModel.objects.create_user(
                full_name=full_name,
                username=username,
                email=email,
                password=password,
            )
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login_page')
        except IntegrityError:
            messages.error(request, 'Username already exists. Please choose another.')
            return render(request, 'register.html')

    return render(request, 'register.html')


def login_page(request):
    if request.user.is_authenticated:
        return redirect('home_page')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # Redirect to 'next' URL if it exists, otherwise home
            next_url = request.GET.get('next', 'home_page')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


@login_required
def logout_page(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login_page')


@login_required
def home_page(request):
    # Show task summary on home page
    user_tasks = TaskModel.objects.filter(user=request.user)
    context = {
        'total_tasks': user_tasks.count(),
        'pending_tasks': user_tasks.filter(status='Pending').count(),
        'in_progress_tasks': user_tasks.filter(status='InProgress').count(),
        'completed_tasks': user_tasks.filter(status='Completed').count(),
    }
    return render(request, 'home.html', context)


@login_required
def task_list(request):
    task_data = TaskModel.objects.filter(user=request.user)

    context = {
        'task_data': task_data,
    }

    return render(request, 'task-list.html', context)


@login_required
def add_task(request):
    if request.method == 'POST':
        form_data = TaskForm(request.POST)
        if form_data.is_valid():
            task = form_data.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task added successfully!')
            return redirect('task_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form_data = TaskForm()

    context = {
        'form_data': form_data,
        'form_title': 'Add Task',
        'btn_name': 'Add Task',
    }

    return render(request, 'master/base-form.html', context)


@login_required
def update_task(request, t_id):
    task_data = get_object_or_404(TaskModel, id=t_id, user=request.user)

    if request.method == 'POST':
        form_data = TaskForm(request.POST, instance=task_data)
        if form_data.is_valid():
            form_data.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('task_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form_data = TaskForm(instance=task_data)

    context = {
        'form_data': form_data,
        'form_title': 'Update Task',
        'btn_name': 'Update Task',
    }
    return render(request, 'master/base-form.html', context)


@require_POST
@login_required
def delete_task(request, t_id):
    task = get_object_or_404(TaskModel, id=t_id, user=request.user)
    task.delete()
    messages.success(request, 'Task deleted successfully!')
    return redirect('task_list')

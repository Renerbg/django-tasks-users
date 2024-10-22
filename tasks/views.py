from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import TaskForm
from .models import Task

# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'El usuario ya existe'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'La contraseña es incorrecta'
        })
    
@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user)
    if tasks.exists():
        return render(request, 'tasks.html', {'tasks':tasks, 'title':'Tareas'})
    else:
        return render(request, 'tasks.html', {'tasks':tasks, 'title':'Tareas',
                                              'error':'No tienes tareas'})


@login_required
def tasks_pendientes(request):
    tasks = Task.objects.filter(user=request.user, fecha_completada__isnull=True)
    if tasks.exists():
        return render(request, 'tasks.html', {'tasks':tasks, 'title':'Tareas Pendientes'})
    else:
        return render(request, 'tasks.html', {'tasks':tasks, 'title':'Tareas Pendientes',
                                              'error':'No tienes tareas pendientes'})


@login_required
def tasks_completadas(request):
    tasks = Task.objects.filter(user=request.user, fecha_completada__isnull=False).order_by('-fecha_completada')
    if tasks.exists():
        return render(request, 'tasks.html', {'tasks':tasks, 'title':'Tareas Completadas'})
    else:
        return render(request, 'tasks.html', {'tasks':tasks, 'title':'Tareas Completadas',
                                              'error':'No tienes tareas completadas'})


@login_required
def task_detalle(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detalle.html', {
            'task':task, 'form':form
            })
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detalle.html', {
                'task':task, 'form':form,
                'error': 'Error actualizando la tarea'
                })

@login_required
def create_task(request):

    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Por favor provee datos validos'
            })

@login_required
def completada_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    task.fecha_completada = timezone.now()
    task.save()
    return redirect('tasks')

@login_required
def eliminar_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    task.delete()
    return redirect('tasks')

@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'],
                     password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'El nombre o la contraseña es incorrecta'
            })
        else:
            login(request, user)
            return redirect('tasks')

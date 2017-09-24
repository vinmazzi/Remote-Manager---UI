from django.contrib.auth.models import User, Group
from user.models import UserExtraInfo
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from user.models import UserExtraInfo
from client.models import Client
from .forms import UserForm

# Create your views here.

def user_create(request):
    if not request.user.is_authenticated:
        return render(request, 'login/login.html')
    user_object = User.objects.get(username=request.user.username)
    client = user_object.userextrainfo_set.all()[0].client_fk
    client_id = client.pk
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                      username = form.cleaned_data['username'],
                      email = form.cleaned_data['email'],
                      first_name = form.cleaned_data['name'],
                      last_name = form.cleaned_data['last_name'],
                      password = form.cleaned_data['password'],
                    )
            user.userextrainfo_set.create(client_fk=client)
    form = UserForm()
    for field in form.fields:
        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
    return render(request, 'user/user_create.html', {
            'client_id': client_id,
            'form': form
        })

def user_list(request):
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    users = UserExtraInfo.objects.filter(client_fk=client)
    return render(request,'user/user_list.html', {
            'users': users,
        })

def user_edit(request, user_id):
    user = User.objects.get(pk=user_id)
    initial_values = {'username': user.username, 'email': user.email}
    form = UserForm()
    return render(request,'user/user_edit.html', {
            'form': form
        })

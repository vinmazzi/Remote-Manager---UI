from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from user.models import UserExtraInfo
import json

def auth(request):
    if not request.user.is_authenticated:
      username = request.POST.get('username')
      pw = request.POST.get('password')
      user = authenticate(request, username=username, password=pw)
      if user is not None:
          login(request, user)
          return HttpResponse(json.dumps({'login_status': 'success'}), content_type="application/json")
      else:
          return HttpResponse(json.dumps({'login_status': 'invalid'}), content_type="application/json")

    user_object = User.objects.get(username=request.user.username)
    client_id = user_object.userextrainfo_set.all()[0].client_fk.pk
    request.session['client_id'] = client_id
    request.session['full_user_name'] = "{} {}".format(user_object.first_name, user_object.last_name)
    request.session['user_perms'] = list(user_object.get_all_permissions())
    request.session.set_expiry(0)
    return HttpResponseRedirect(reverse('group:index'))

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'login/login.html')
    else:
        user_object = User.objects.get(username=request.user.username)
        client_id = user_object.userextrainfo_set.all()[0].client_fk.pk

        return HttpResponseRedirect(reverse('group:index'))

def do_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login:index'))

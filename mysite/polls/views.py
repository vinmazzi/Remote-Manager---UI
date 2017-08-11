from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.o
def index(request):
    return HttpResponse("Eaeeeeeee.")

def teste(request):
    return HttpResponse("ISSO É UM TESTE")

def meuIptables(request):
    return HttpResponse("MEU CODIGO DO IPTABLES VAI FICAR MASSA DEMAIS!!!!")

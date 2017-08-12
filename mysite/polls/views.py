from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from .models import Question

# Create your views here.o
def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = { 'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def teste(request):
    return HttpResponse("ISSO É UM TESTE")

def meuIptables(request):
    return HttpResponse("MEU CODIGO DO IPTABLES VAI FICAR MASSA DEMAIS!!!!")

def detail(request, question_id):
  #  O get_object_or_404 substitui todo esse "Try except" que está ai em baixo:
  #  try:
  #      question = Question.objects.get(id = question_id)
  #  except Question.DoesNotExist:
  #      raise Http404("Question Does not Exist")

    question = get_object_or_404(Question, pk=question_id) 
    return render(request, 'polls/detail.html', {'question': question})

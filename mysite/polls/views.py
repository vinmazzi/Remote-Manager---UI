from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader

from .models import Question, Choice

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
  # O render() substitui isso: 
  # HttpResponse(template.render(context, request))
  # O render aceita tres parametros: 
  # - a request
  # - o TEMPLATE ('polls/detail.html' NÃO É UMA URL, É O CAMINHO PARA O TEMPLATE. JÁ CONFUNDI UMA VEZ.) 
  # e os objetos que deverão ser passados para o TEMPLATE!

    return render(request, 'polls/detail.html', {'question': question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "Voce não selecionou uma opção!!! Cacete!"
        })
    else:
       selected_choice.votes += 1
       selected_choice.save()

       return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

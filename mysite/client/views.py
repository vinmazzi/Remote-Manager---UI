from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .models import Client
from .forms import ClientForm

# Create your views here.
def client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = Client()
            client.client_name = form.cleaned_data['client_name_text']

            client.save()
            return HttpResponseRedirect(reverse('client:index'))
    else:
        form = ClientForm()

    try:
        clients = Client.objects.all()

    except (KeyError, Client.DoesNotExist):
        return render(request, 'client/client.html', {
                'error_massage': "No Clients yet!",
                'form': form,
            })

    return render(request, 'client/client.html', {
                'clients': clients,
                'form': form,
            })

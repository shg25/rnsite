from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Air


def index(request):
    latest_air_list = Air.objects.order_by('-started')[:5]
    context = {'latest_air_list': latest_air_list}
    return render(request, 'airs/index.html', context)

def detail(request, air_id):
    air = get_object_or_404(Air, pk=air_id)
    return render(request, 'airs/detail.html', {'air': air})

def results(request, air_id):
    response = "You're looking at the results of air %s."
    return HttpResponse(response % air_id)


def vote(request, air_id):
    return HttpResponse("You're voting on air %s." % air_id)

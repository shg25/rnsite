from django.http import HttpResponse
from django.shortcuts import render

from .models import Air


def index(request):
    latest_air_list = Air.objects.order_by('-started')[:5]
    context = {'latest_air_list': latest_air_list}
    return render(request, 'airs/index.html', context)


def detail(request, air_id):
    return HttpResponse("You're looking at air %s." % air_id)


def results(request, air_id):
    response = "You're looking at the results of air %s."
    return HttpResponse(response % air_id)


def vote(request, air_id):
    return HttpResponse("You're voting on air %s." % air_id)

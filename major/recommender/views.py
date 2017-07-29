from django.shortcuts import render
from django.views.generic import View
from recommender import utils as recommender
from django.http import HttpResponse

# Create your views here.


class RecommendationDemo(View):
    def get(self, request, *args, **kwargs):
        context = {
        }
        return render(request, 'recommendationDemo.html', context)

    def post(self, request, *args, **kwargs):
        ratings = []
        ratings.append(int(request.POST.get('a-1', 0)))
        ratings.append(int(request.POST.get('b-1', 0)))
        ratings.append(int(request.POST.get('c-1', 0)))
        ratings.append(int(request.POST.get('d-1', 0)))
        ratings.append(int(request.POST.get('e-1', 0)))
        ratings.append(int(request.POST.get('f-1', 0)))
        ratings.append(int(request.POST.get('g-1', 0)))
        ratings.append(int(request.POST.get('h-1', 0)))
        ratings.append(int(request.POST.get('i-1', 0)))
        ratings.append(int(request.POST.get('j-1', 0)))
        print(ratings)
        originals, predictions = recommender.demoRecommend(ratings)

        context = {
            'originals': originals,
            'predictions': predictions,

        }
        return render(request, 'recommendationDemo.html', context)


class RecommendationTrain(View):
    def get(self, request, *args, **kwargs):
        recommender.train()
        return HttpResponse("Training Successful")

from django.shortcuts import render
from django.views.generic import View
from recommender import utils as recommender
from django.http import HttpResponse

# Create your views here.


class RecommendationDemo(View):
    def get(self, request, *args, **kwargs):
        originals, predictions = recommender.demoRecommend()
        # originals, predictions = [], []
        context = {
            'originals': originals,
            'predictions': predictions,

        }
        return render(request, 'recommendationDemo.html', context)


class RecommendationTrain(View):
    def get(self, request, *args, **kwargs):
        recommender.train()
        return HttpResponse("Training Successful")

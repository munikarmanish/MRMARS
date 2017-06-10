from django.shortcuts import render
from django.views.generic import FormView

from . import utils as sentiment
from .forms import SentimentDemoForm


class SentimentDemo(FormView):
    form_class = SentimentDemoForm
    template_name = 'sentiment/demo.html'

    def form_valid(self, form):
        review = form.cleaned_data.get('review')
        rating = sentiment.rating(review)
        print(rating)
        sentimentClass = sentiment.sentiment_from_rating(rating)

        context = {
            'form': form,
            'rating': rating,
            'sentimentClass': sentimentClass,
        }
        return render(self.request, template_name=self.template_name, context=context)

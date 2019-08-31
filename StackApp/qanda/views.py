from django.shortcuts import render
from .serializer import ScrapedquestionSerializer
from bs4 import BeautifulSoup
import requests
import json
from django.http import HttpResponse
from rest_framework import viewsets
from .serializer import ScrapedquestionSerializer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect, HttpResponseBadRequest
from django.urls.base import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    DayArchiveView,
    RedirectView,
)

from .forms import QuestionForm, AnswerForm, AnswerAcceptanceForm
from .models import Question, Answer, Scrapedquestion

class DailyQuestionList(DayArchiveView):
    queryset = Question.objects.all()
    date_field = 'created'
    month_format = '%m'
    allow_empty = True

class TodaysQuestionList(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        today = timezone.now()
        return reverse(
                'qanda:daily_questions',
            kwargs={
                'day': today.day,
                'month': today.month,
                'year': today.year,
            }
        )

class AskQuestionView(LoginRequiredMixin, CreateView):
    form_class = QuestionForm
    template_name = 'qanda/ask.html'

    def get_initial(self):
        return {
            'user': self.request.user.id
        }

    def form_valid(self, form):
        action = self.request.POST.get('action')
        if action == 'SAVE':
            # save and redirect
            return super().form_valid(form)
        elif action == 'PREVIEW':
            preview = Question(
                question=form.cleaned_data['question'],
                title=form.cleaned_data['title'])
            ctx = self.get_context_data(preview=preview)
            return self.render_to_response(context=ctx)
        return HttpResponseBadRequest()

class CreateAnswerView(LoginRequiredMixin, CreateView):
    form_class = AnswerForm
    template_name = 'qanda/create_answer.html'

    def get_initial(self):
        return {
            'question': self.get_question().id,
            'user': self.request.user.id,
        }

    def get_context_data(self, **kwargs):
        return super().get_context_data(question=self.get_question(),
                                        **kwargs)

    def get_success_url(self):
        return self.object.question.get_absolute_url()

    def form_valid(self, form):
        action = self.request.POST.get('action')
        if action == 'SAVE':
            # save and redirect 
            return super().form_valid(form)
        elif action == 'PREVIEW':
            ctx = self.get_context_data(preview=form.cleaned_data['answer'])
            return self.render_to_response(context=ctx)
        return HttpResponseBadRequest()

    def get_question(self):
        return Question.objects.get(pk=self.kwargs['pk'])


class QuestionDetailView(DetailView):
    model = Question

    ACCEPT_FORM = AnswerAcceptanceForm(initial={'accepted': True})
    REJECT_FORM = AnswerAcceptanceForm(initial={'accepted': False})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'answer_form': AnswerForm(initial={
                'user': self.request.user.id,
                'question': self.object.id,
            })
        })
        if self.object.can_accept_answers(self.request.user):
            ctx.update({
                'accept_form': self.ACCEPT_FORM,
                'reject_form': self.REJECT_FORM,
            })
        return ctx

class UpdateAnswerAcceptanceView(LoginRequiredMixin, UpdateView):
    form_class = AnswerAcceptanceForm
    queryset = Answer.objects.all()

    def get_success_url(self):
        return self.object.question.get_absolute_url()

    def form_invalid(self, form):
        return HttpResponseRedirect(
            redirect_to=self.object.question.get_absolute_url())

def index(request):
    return HttpResponse("Success")

class QuestionAPI(viewsets.ModelViewSet):
    queryset = Scrapedquestion.objects.all()
    serializer_class = ScrapedquestionSerializer

def latest(request):
    try: 
        end_page_num = 3
        i = 1
        while i <= end_page_num:
            res = requests.get("https://stackoverflow.com/questions/tagged/python%2bpandas?tab=newest&page={}&pagesize=50".format(i))
            soup = BeautifulSoup(res.text, "html.parser")
            questions = soup.select(".question-summary")
            for que in questions:
                q = que.select_one('.question-hyperlink').getText()
                vote_count = que.select_one('.vote-count-post').getText()
                views = que.select_one('.views').attrs['title']
                tags = [i.getText() for i in (que.select('.post-tag'))]
                
                question = Scrapedquestion()
                question.question = q
                question.vote_count = vote_count
                question.views = views
                question.tags = tags
                question.save()
            i += 1
        return HttpResponse("Latest Data Fetched from Stack Overflow")
    except e as Exception:
        return HttpResponse(f"Failed {e}")


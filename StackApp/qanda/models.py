from django.conf import settings
from django.db import models
from django.urls.base import reverse

class Scrapedquestion(models.Model):
    question = models.CharField(max_length=300)
    vote_count = models.IntegerField(default=0)
    views = models.CharField(max_length=50)
    tags = models.CharField(max_length=250)

    def __str__(self):
        return self.question

class Question(models.Model):
    title = models.CharField(max_length=140)
    question = models.TextField()
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('qanda:question_detail', kwargs={'pk': self.id})

    def can_accept_answers(self, user):
        return user == self.user


class Answer(models.Model):
    answer = models.TextField()
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(to=Question,
                                 on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created', )

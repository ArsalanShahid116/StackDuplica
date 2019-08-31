from rest_framework import serializers
from .models import Scrapedquestion


class ScrapedquestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scrapedquestion
        fields = ('__all__')

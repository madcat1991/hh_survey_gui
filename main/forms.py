from django.forms import ModelForm, RadioSelect

from main.models import RecsReviewQA


class RecsReviewQAForm(ModelForm):
    class Meta:
        model = RecsReviewQA
        fields = ["quality_qa", "diversity_qa", "easiness_qa", "happiness_qa"]
        widgets = {
            'quality_qa': RadioSelect(),
            'diversity_qa': RadioSelect(),
            'easiness_qa': RadioSelect(),
            'happiness_qa': RadioSelect(),
        }

from django.forms import ModelForm, RadioSelect, Textarea

from main.models import RecsReviewQA, ClusterRecsReviewQA


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


class ClusterRecsReviewQAForm(ModelForm):
    class Meta:
        model = ClusterRecsReviewQA
        fields = ["usefulness_qa", "choice_qa"]
        widgets = {
            'usefulness_qa': RadioSelect(),
            'choice_qa': RadioSelect(),
        }

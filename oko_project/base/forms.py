from django import forms
from .models import ParametersNormativesInCalculation, Folder

class ParametersNormativesInCalculationForm(forms.ModelForm):
    class Meta:
        model = ParametersNormativesInCalculation
        fields = ['overheads', 'salary_fund', 'profit']

from django import forms
from .models import ParametersNormativesInCalculation

class ParametersNormativesForm(forms.ModelForm):
    class Meta:
        model = ParametersNormativesInCalculation
        fields = ['overheads', 'salary_fund', 'profit']

from django import forms
from .models import Folder

class FolderAdminForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = '__all__'  # Убедитесь, что здесь указаны нужные поля

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # Если это новый объект
            self.fields['parent'].empty_label = "Выберите родительскую папку"

            
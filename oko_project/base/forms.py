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
        fields = ['name', 'parent', 'folder_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убедитесь, что поле parent не имеет строки 'null'
        self.fields['parent'].empty_label = "Без родительской папки"  # Это поможет отображать пустое значение

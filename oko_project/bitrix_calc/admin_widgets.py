from django import forms
from base.models import Folder

class HierarchicalFolderWidget(forms.Select):
    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs, choices)

    def create_choices(self, queryset, level=0, prefix=""):
        """
        Рекурсивно создает иерархические опции для папок, исключая дублирования и сортируя по алфавиту.
        """
        choices = []
        # Сортируем папки по имени
        for folder in queryset.order_by('name'):
            if not folder.parent or level > 0:  # Пропускаем верхний уровень, если у папки есть родитель
                choices.append((folder.id, f"{prefix * level}{folder.name}"))
            # Получаем дочерние папки, отсортированные по имени
            child_folders = Folder.objects.filter(parent=folder).order_by('name')
            choices.extend(self.create_choices(child_folders, level + 1, prefix="— "))
        return choices

    def update_choices(self, queryset):
        """
        Инициализирует иерархические опции с фильтрацией дублирующихся родительских папок и сортировкой по алфавиту.
        """
        self.choices = self.create_choices(queryset)

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Formulas, TechnologicalOperation, MaterialsTechnologicalOperation, AddingMaterialsTechnologicalOperation, ParametersOfProducts

# Функция для добавления значения formula_name в модель Formulas при сохранении
def add_formula_to_formulas(formula_name):
    if formula_name and not Formulas.objects.filter(formula_name=formula_name).exists():
        Formulas.objects.create(formula_name=formula_name)

# Функция для удаления значения formula_name из модели Formulas, если оно больше не используется
def remove_formula_from_formulas(formula_name):
    if formula_name and not (
        TechnologicalOperation.objects.filter(formula_name=formula_name).exists() or
        MaterialsTechnologicalOperation.objects.filter(formula_name=formula_name).exists() or
        AddingMaterialsTechnologicalOperation.objects.filter(formula_name=formula_name).exists() or
        ParametersOfProducts.objects.filter(formula_name=formula_name).exists()
    ):
        Formulas.objects.filter(formula_name=formula_name).delete()

@receiver(post_save, sender=TechnologicalOperation)
@receiver(post_save, sender=MaterialsTechnologicalOperation)
@receiver(post_save, sender=AddingMaterialsTechnologicalOperation)
@receiver(post_save, sender=ParametersOfProducts)
def create_formula(sender, instance, **kwargs):
    add_formula_to_formulas(instance.formula_name)

@receiver(post_delete, sender=TechnologicalOperation)
@receiver(post_delete, sender=MaterialsTechnologicalOperation)
@receiver(post_delete, sender=AddingMaterialsTechnologicalOperation)
@receiver(post_delete, sender=ParametersOfProducts)
def delete_formula(sender, instance, **kwargs):
    remove_formula_from_formulas(instance.formula_name)

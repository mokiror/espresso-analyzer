from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BrewRecipe, TastePrediction
from .coffe_math import calculate_full_prediction

@receiver(post_save, sender=BrewRecipe)
def create_or_update_prediction(sender, instance, created, **kwargs):

    #создаёт или обновляет прогноз при сохранении рецепта

    try:
        calculate_full_prediction(instance)
        print(f"Прогноз для рецепта {instance.id} успешно создан!")
    except Exception as e:
        print(f"Ошибка при создании прогноза для рецепта {instance.id}: {e}")
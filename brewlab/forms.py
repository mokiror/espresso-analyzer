from django import forms
from .models import CoffeeBean, BrewRecipe, TastePrediction


class CoffeeBeanForm(forms.ModelForm):
    #редактирование и добавление кофе

    class Meta:
        model = CoffeeBean
        fields = [
            'name', 'origin_country', 'region',
            'altitude_min', 'altitude_max', 'process_method',
            'acidity_score', 'density', 'description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Ethiopia Yirgacheffe'}),
            'origin_country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Ethiopia'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Yirgacheffe'}),
            'altitude_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1200'}),
            'altitude_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2000'}),
            'process_method': forms.Select(attrs={'class': 'form-select'}),
            'acidity_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '1', 'max': '10'}),
            'density': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.5', 'max': '0.8'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Опишите вкусовые характеристики...'}),
        }
        labels = {
            'name': 'Название сорта',
            'origin_country': 'Страна происхождения',
            'region': 'Регион',
            'altitude_min': 'Мин. высота (м)',
            'altitude_max': 'Макс. высота (м)',
            'process_method': 'Метод обработки',
            'acidity_score': 'Кислотность (1-10)',
            'density': 'Плотность зерна (г/см³)',
            'description': 'Описание',
        }
        help_texts = {
            'acidity_score': 'Чем выше значение, тем кислее будет кофе',
            'density': 'Обычно 0.60-0.72 г/см³ для обжаренных зёрен',
        }


class BrewRecipeForm(forms.ModelForm):
    #добавление рецепта

    class Meta:
        model = BrewRecipe
        fields = [
            'coffee', 'name', 'water_temperature',
            'grind_size', 'brew_time_seconds',
            'coffee_dose', 'water_volume', 'is_recommended'
        ]
        widgets = {
            'coffee': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Классический пуровер'}),
            'water_temperature': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '93'}),
            'grind_size': forms.Select(attrs={'class': 'form-select'}),
            'brew_time_seconds': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '180'}),
            'coffee_dose': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '15'}),
            'water_volume': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '250'}),
            'is_recommended': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'coffee': 'Сорт кофе',
            'name': 'Название рецепта',
            'water_temperature': 'Температура воды (°C)',
            'grind_size': 'Степень помола',
            'brew_time_seconds': 'Время заваривания (сек)',
            'coffee_dose': 'Доза кофе (г)',
            'water_volume': 'Объём воды (мл)',
            'is_recommended': 'Рекомендуемый рецепт',
        }
        help_texts = {
            'water_temperature': 'Оптимальный диапазон: 88-96°C',
            'brew_time_seconds': 'Обычно 180-240 сек для пуровера',
        }

    def clean(self):
        cleaned_data = super().clean()
        temp = cleaned_data.get('water_temperature')
        time = cleaned_data.get('brew_time_seconds')

        if temp and (temp < 70 or temp > 100):
            raise forms.ValidationError('Температура должна быть в диапазоне 70-100°C')

        if time and time < 30:
            raise forms.ValidationError('Время заваривания должно быть не менее 30 секунд')

        return cleaned_data
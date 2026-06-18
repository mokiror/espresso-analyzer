from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


class CoffeeBean(models.Model):

    PROCESS_METHODS = [
        ('washed', 'Washed'),
        ('natural', 'Natural'),
        ('honey', 'Honey'),
    ]

    #основная инфа
    name = models.CharField(max_length=100, unique=True, verbose_name="Название сорта")
    origin_country = models.CharField(max_length=50, verbose_name="Страна происхождения")
    region = models.CharField(max_length=100, blank=True, verbose_name="Регион")

    #характеристики выращивания
    altitude_min = models.PositiveIntegerField(
        help_text="Высота в метрах (минимум)",
        verbose_name="Мин. высота (м)"
    )
    altitude_max = models.PositiveIntegerField(
        help_text="Высота в метрах (максимум)",
        verbose_name="Макс. высота (м)"
    )
    process_method = models.CharField(
        max_length=20,
        choices=PROCESS_METHODS,
        verbose_name="Метод обработки"
    )

    #вкус
    acidity_score = models.FloatField(
        validators=[MinValueValidator(1.0), MaxValueValidator(10.0)],
        help_text="Оценка кислотности от 1 (низкая) до 10 (высокая)",
        verbose_name="Кислотность (1-10)"
    )

    #технические характеристики
    density = models.FloatField(
        default=0.65,
        validators=[MinValueValidator(0.5), MaxValueValidator(0.8)],
        help_text="Плотность обжарки (г/см³)",
        verbose_name="Плотность зерна"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Сорт кофе"
        verbose_name_plural = "Сорта кофе"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_process_method_display()})"

    def get_avg_altitude(self):
        return (self.altitude_min + self.altitude_max) / 2

    def get_absolute_url(self):
        return reverse('coffee_detail', args=[str(self.id)])

class BrewRecipe(models.Model):
    #рецепт заваривания для конкретного зерна

    GRIND_SETTINGS = [
        ('extra_fine', 'Очень мелкий (эспрессо 0.2-0.3 мм)'),
        ('fine', 'Мелкий (аэропресс 0.4-0.6 мм)'),
        ('medium_fine', 'Средне-мелкий (воронка 0.6-0.8 мм)'),
        ('medium', 'Средний (пуровер 0.8-1.0 мм)'),
        ('coarse', 'Крупный (френч-пресс 1.0-1.2 мм)'),
    ]

    coffee = models.ForeignKey(
        CoffeeBean,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Сорт кофе"
    )

    #параметры варки
    name = models.CharField(max_length=100, default="Стандартный рецепт", verbose_name="Название рецепта")
    water_temperature = models.FloatField(
        validators=[MinValueValidator(70), MaxValueValidator(100)],
        help_text="Температура воды в градусах цельсия",
        verbose_name="Температура воды (°C)"
    )
    grind_size = models.CharField(
        max_length=20,
        choices=GRIND_SETTINGS,
        verbose_name="Помол"
    )
    brew_time_seconds = models.PositiveIntegerField(
        default=180,
        help_text="Время контакта воды с кофе в секундах",
        verbose_name="Время заваривания (сек)"
    )

    #пропорции
    coffee_dose = models.FloatField(
        default=15.0,
        validators=[MinValueValidator(5), MaxValueValidator(30)],
        verbose_name="Доза кофе (г)"
    )
    water_volume = models.FloatField(
        default=250.0,
        validators=[MinValueValidator(100), MaxValueValidator(500)],
        verbose_name="Объём воды (мл)"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_recommended = models.BooleanField(default=False, verbose_name="Рекомендуемый рецепт")

    class Meta:
        verbose_name = "Рецепт заваривания"
        verbose_name_plural = "Рецепты заваривания"
        unique_together = ['coffee', 'water_temperature', 'grind_size']
        ordering = ['coffee', '-created_at']

    def __str__(self):
        return f"{self.coffee.name} - {self.water_temperature}°C, {self.get_grind_size_display()}"

    def get_ratio(self):
        #соотношение к вода/кофе (коэф заваривания)
        if self.coffee_dose > 0:
            return round(self.water_volume / self.coffee_dose, 1)
        return 0

    def get_grind_factor(self):
        factors = {
            'extra_fine': 1.8,
            'fine': 1.4,
            'medium_fine': 1.1,
            'medium': 1.0,
            'coarse': 0.7,
        }
        return factors.get(self.grind_size, 1.0)

class TastePrediction(models.Model):
    #результат расчёта вкусового баланса

    BALANCE_TYPES = [
        ('acidic', 'Сильная кислотность ☕ (недожарили)'),
        ('balanced', 'Сбалансировано!! ⭐ (идеально)'),
        ('bitter', 'Сильная горечь! 🔥 (пережарили)'),
    ]

    #связь с рецептом
    recipe = models.OneToOneField(
        BrewRecipe,
        on_delete=models.CASCADE,
        related_name='prediction',
        verbose_name="Рецепт"
    )

    #результат расчётов
    acidity_intensity = models.FloatField(
        help_text="Интенсивность кислотности (0-100)",
        verbose_name="Кислинка"
    )
    sweetness_intensity = models.FloatField(
        help_text="Интенсивность сладости (0-100)",
        verbose_name="Сладость"
    )
    bitterness_intensity = models.FloatField(
        help_text="Интенсивность горечи (0-100)",
        verbose_name="Горечь"
    )

    #рекомендации
    balance_type = models.CharField(
        max_length=20,
        choices=BALANCE_TYPES,
        verbose_name="Тип"
    )
    recommended_temperature_adjustment = models.IntegerField(
        help_text="Рекомендуемое изменение температуры в градусах",
        verbose_name="Корректировка температуры (°C)"
    )

    #тех параметры
    tds_estimate = models.FloatField(
        help_text="Total Dissolved Solids - процент растворённых веществ",
        verbose_name="TDS (%)"
    )
    extraction_yield = models.FloatField(
        help_text="Процент экстракции (извлечения) из зерна",
        verbose_name="Экстракция (%)",
        default=18.0
    )

    #данные
    calculated_at = models.DateTimeField(auto_now_add=True, verbose_name="Время расчёта")

    class Meta:
        verbose_name = "Прогноз вкуса"
        verbose_name_plural = "Прогнозы вкуса"
        ordering = ['-calculated_at']

    def __str__(self):
        return f"Прогноз для {self.recipe.coffee.name} - {self.get_balance_type_display()}"

    def get_triangle_data(self):
        return {
            'acidity': self.acidity_intensity,
            'sweetness': self.sweetness_intensity,
            'bitterness': self.bitterness_intensity,
        }

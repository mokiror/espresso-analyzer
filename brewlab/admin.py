from django.contrib import admin
from .models import CoffeeBean, BrewRecipe, TastePrediction

@admin.register(CoffeeBean)
class CoffeeBeanAdmin(admin.ModelAdmin):
    list_display = ['name', 'origin_country', 'acidity_score', 'process_method', 'created_at']
    list_filter = ['process_method', 'origin_country']
    search_fields = ['name', 'origin_country', 'region']
    list_editable = ['acidity_score']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'origin_country', 'region', 'description')
        }),
        ('Выращивание и обработка', {
            'fields': ('altitude_min', 'altitude_max', 'process_method')
        }),
        ('Вкусовые характеристики', {
            'fields': ('acidity_score', 'density')
        }),
    )

@admin.register(BrewRecipe)
class BrewRecipeAdmin(admin.ModelAdmin):
    list_display = ['coffee', 'water_temperature', 'grind_size', 'brew_time_seconds', 'is_recommended']
    list_filter = ['grind_size', 'is_recommended', 'coffee']
    search_fields = ['coffee__name', 'name']
    list_editable = ['is_recommended']

@admin.register(TastePrediction)
class TastePredictionAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'balance_type', 'tds_estimate', 'calculated_at']
    list_filter = ['balance_type']
    readonly_fields = ['acidity_intensity', 'sweetness_intensity', 'bitterness_intensity',
                       'tds_estimate', 'extraction_yield', 'balance_type']

    def has_add_permission(self, request):
        return False

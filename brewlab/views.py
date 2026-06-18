from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db import models
from .models import CoffeeBean, BrewRecipe, TastePrediction
from .coffe_math import calculate_full_prediction, recommend_optimal_recipe
from .chart_utils import create_taste_triangle, create_temperature_chart, create_balance_gauge
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .forms import CoffeeBeanForm, BrewRecipeForm

#главная страница
def home_view(request):
    coffee_count = CoffeeBean.objects.count()
    recipe_count = BrewRecipe.objects.count()
    prediction_count = TastePrediction.objects.count()

    #статистика по балансу
    balance_stats = TastePrediction.objects.values('balance_type').annotate(
        count=models.Count('balance_type')
    )

    context = {
        'coffee_count': coffee_count,
        'recipe_count': recipe_count,
        'prediction_count': prediction_count,
        'balance_stats': balance_stats,
        'title': 'Coffee Analyzer - Система анализа профиля кофе',
    }
    return render(request, 'brewlab/home.html', context)

#список сортов кофе
class CoffeeListView(ListView):
    model = CoffeeBean
    template_name = 'brewlab/coffee_list.html'
    context_object_name = 'coffees'
    paginate_by = 9

    def get_queryset(self):
        queryset = CoffeeBean.objects.all()

        #поиск
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(name__icontains=search_query) |
                models.Q(origin_country__icontains=search_query)
            )

        #фильтруем по обработке
        process = self.request.GET.get('process')
        if process:
            queryset = queryset.filter(process_method=process)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Сорта кофе'
        context['process_choices'] = CoffeeBean.PROCESS_METHODS
        context['current_process'] = self.request.GET.get('process', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

#детальная страница с кофеем
def coffee_detail_view(request, pk):
    coffee = get_object_or_404(CoffeeBean, pk=pk)
    recipes = coffee.recipes.prefetch_related('prediction').all()

    #рекомендуемый рецепт (если нет)
    recommended = None
    if not recipes.filter(is_recommended=True).exists():
        pass

    context = {
        'coffee': coffee,
        'recipes': recipes,
        'recommended': recommended,
        'title': f'{coffee.name} - Coffee Analyzer',
    }
    return render(request, 'brewlab/coffee_detail.html', context)

#страница с рецептами
def recipe_detail_view(request, pk):
    #страница рецепта с прогнозом и графиками
    recipe = get_object_or_404(BrewRecipe, pk=pk)

    #если прогноза нет то создаем
    if not hasattr(recipe, 'prediction'):
        try:
            calculate_full_prediction(recipe)
            recipe.refresh_from_db()
        except Exception as e:
            print(f"Ошибка расчёта: {e}")

    prediction = recipe.prediction if hasattr(recipe, 'prediction') else None

    #графики
    triangle_chart = None
    temperature_chart = None
    balance_gauge = None

    if prediction:
        #треугольник вкуса
        triangle_chart = create_taste_triangle(
            prediction.acidity_intensity,
            prediction.sweetness_intensity,
            prediction.bitterness_intensity
        )

        #баланс
        balance_gauge = create_balance_gauge(
            prediction.balance_type,
            value=prediction.sweetness_intensity
        )

        #данные по разным температурам
        coffee = recipe.coffee
        temperatures = list(range(85, 98, 2))  # 85, 87, 89, 91, 93, 95, 97
        sweetness_scores = []
        acidity_scores = []
        bitterness_scores = []

        for temp in temperatures:
            temp_recipe = BrewRecipe(
                coffee=coffee,
                water_temperature=temp,
                grind_size=recipe.grind_size,
                brew_time_seconds=recipe.brew_time_seconds,
                coffee_dose=recipe.coffee_dose,
                water_volume=recipe.water_volume,
            )
            try:
                from .coffe_math import calculate_acidity_factor, calculate_extraction_rate, predict_taste_profile
                altitude = coffee.get_avg_altitude()
                acidity_factor = calculate_acidity_factor(
                    coffee.acidity_score,
                    altitude,
                    coffee.process_method
                )
                grind_factor = temp_recipe.get_grind_factor()
                ratio = temp_recipe.get_ratio()
                extraction = calculate_extraction_rate(temp, temp_recipe.brew_time_seconds, grind_factor, ratio)
                taste = predict_taste_profile(acidity_factor, extraction, ratio)
                sweetness_scores.append(taste['sweetness'])
                acidity_scores.append(taste['acidity'])
                bitterness_scores.append(taste['bitterness'])
            except:
                sweetness_scores.append(50)
                acidity_scores.append(50)
                bitterness_scores.append(50)

        #график температуры
        temperature_chart = create_temperature_chart(
            temperatures,
            sweetness_scores,
            acidity_scores,
            bitterness_scores
        )

    context = {
        'recipe': recipe,
        'prediction': prediction,
        'triangle_chart': triangle_chart,
        'temperature_chart': temperature_chart,
        'balance_gauge': balance_gauge,
        'title': f'Рецепт: {recipe.name}',
    }
    return render(request, 'brewlab/recipe_detail.html', context)

#вообще все рецепты
class RecipeListView(ListView):
    model = BrewRecipe
    template_name = 'brewlab/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 12

    def get_queryset(self):
        queryset = BrewRecipe.objects.all().select_related('coffee')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Все рецепты'
        return context


#добавляем сорт кофе
class CoffeeCreateView(CreateView):
    model = CoffeeBean
    form_class = CoffeeBeanForm
    template_name = 'brewlab/coffee_form.html'
    success_url = reverse_lazy('brewlab:coffee_list')

    def form_valid(self, form):
        messages.success(self.request, f'Сорт "{form.instance.name}" успешно добавлен!')
        return super().form_valid(form)


#редакт ируем
class CoffeeUpdateView(UpdateView):
    model = CoffeeBean
    form_class = CoffeeBeanForm
    template_name = 'brewlab/coffee_form.html'
    success_url = reverse_lazy('brewlab:coffee_list')

    def form_valid(self, form):
        messages.success(self.request, f'Сорт "{form.instance.name}" успешно обновлён!')
        return super().form_valid(form)


#удаляем
class CoffeeDeleteView(DeleteView):
    model = CoffeeBean
    template_name = 'brewlab/coffee_confirm_delete.html'
    success_url = reverse_lazy('brewlab:coffee_list')

    def delete(self, request, *args, **kwargs):
        coffee = self.get_object()
        messages.success(self.request, f'Сорт "{coffee.name}" успешно удалён!')
        return super().delete(request, *args, **kwargs)


#добаляем рецепт
class RecipeCreateView(CreateView):
    model = BrewRecipe
    form_class = BrewRecipeForm
    template_name = 'brewlab/recipe_form.html'
    success_url = reverse_lazy('brewlab:recipe_list')

    def form_valid(self, form):
        messages.success(self.request, f'Рецепт "{form.instance.name}" успешно создан!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление рецепта'
        return context


#редактируем
class RecipeUpdateView(UpdateView):
    model = BrewRecipe
    form_class = BrewRecipeForm
    template_name = 'brewlab/recipe_form.html'
    success_url = reverse_lazy('brewlab:recipe_list')

    def form_valid(self, form):
        messages.success(self.request, f'Рецепт "{form.instance.name}" успешно обновлён!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование рецепта'
        return context


#удаляем
class RecipeDeleteView(DeleteView):
    model = BrewRecipe
    template_name = 'brewlab/recipe_confirm_delete.html'
    success_url = reverse_lazy('brewlab:recipe_list')

    def delete(self, request, *args, **kwargs):
        recipe = self.get_object()
        messages.success(self.request, f'Рецепт "{recipe.name}" успешно удалён!')
        return super().delete(request, *args, **kwargs)

from django.urls import path
from . import views

app_name = 'brewlab'

urlpatterns = [
    #главная
    path('', views.home_view, name='home'),

    #сорта
    path('coffee/', views.CoffeeListView.as_view(), name='coffee_list'),
    path('coffee/<int:pk>/', views.coffee_detail_view, name='coffee_detail'),
    path('coffee/add/', views.CoffeeCreateView.as_view(), name='coffee_add'),
    path('coffee/<int:pk>/edit/', views.CoffeeUpdateView.as_view(), name='coffee_edit'),
    path('coffee/<int:pk>/delete/', views.CoffeeDeleteView.as_view(), name='coffee_delete'),

    #рецепты
    path('recipes/', views.RecipeListView.as_view(), name='recipe_list'),
    path('recipe/<int:pk>/', views.recipe_detail_view, name='recipe_detail'),
    path('recipe/add/', views.RecipeCreateView.as_view(), name='recipe_add'),
    path('recipe/<int:pk>/edit/', views.RecipeUpdateView.as_view(), name='recipe_edit'),
    path('recipe/<int:pk>/delete/', views.RecipeDeleteView.as_view(), name='recipe_delete'),
]
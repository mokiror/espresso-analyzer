
#расчет вкусового профиля кофе

import math

def calculate_acidity_factor(acidity_score, altitude, process_method):

    #расчет фактора кислотности зерна

    #чем выше - тем кислее
    altitude_factor = min(1.5, altitude / 1200)
    
    #обработка
    process_factors = {
        'washed': 1.3,      #максимальная кислотность
        'honey': 1.0,       #средняя
        'natural': 0.7,     #низкая
    }
    process_factor = process_factors.get(process_method, 1.0)
    
    #итог
    total_factor = (acidity_score / 5.0) * altitude_factor * process_factor
    
    return max(0.5, min(2.0, total_factor))

def calculate_extraction_rate(temperature, time_seconds, grind_factor, ratio):

    #скорость экстракции
    #температура
    if temperature < 85:
        temp_coef = 0.6
    elif temperature < 92:
        temp_coef = 0.8 + (temperature - 85) * 0.03
    elif temperature <= 96:
        temp_coef = 1.0 + (temperature - 92) * 0.05
    else:
        temp_coef = 1.2 - (temperature - 96) * 0.05
    
    #временной фактор
    base_time = 180
    time_factor = math.log(1 + time_seconds / 60) / math.log(1 + base_time / 60)
    time_factor = min(1.5, time_factor)
    
    #соотношение к  вода/кофе
    optimal_ratio = 16
    if ratio > 0:
        ratio_factor = min(1.5, ratio / optimal_ratio)
    else:
        ratio_factor = 1.0
    
    #коэффициент
    extraction = temp_coef * time_factor * grind_factor * ratio_factor
    
    return max(0.3, min(1.2, extraction))

def calculate_tds(extraction_rate, ratio):

    #роцент растворённых веществ
    base_extraction_pct = extraction_rate * 20
    ratio_correction = 16 / ratio if ratio > 0 else 1
    tds = base_extraction_pct / ratio_correction / 16
    return max(0.5, min(2.5, tds))

def predict_taste_profile(acidity_factor, extraction_rate, ratio=16):

    #кислотность
    acidity = acidity_factor * 60
    if extraction_rate < 0.6:
        acidity = acidity * (1.0 + (0.6 - extraction_rate) * 1.5)
    elif extraction_rate > 0.9:
        acidity = acidity * (1.0 - (extraction_rate - 0.9) * 1.2)
    acidity = min(100, max(0, acidity))
    
    #слодость
    if extraction_rate < 0.65:
        sweetness = (extraction_rate / 0.65) * 70
    elif extraction_rate <= 0.85:
        sweetness = 70 + (extraction_rate - 0.65) / 0.2 * 25
    else:
        sweetness = 95 - (extraction_rate - 0.85) * 80
    sweetness = min(100, max(0, sweetness))
    
    #горечь
    if extraction_rate < 0.7:
        bitterness = extraction_rate * 20
    elif extraction_rate < 0.85:
        bitterness = 15 + (extraction_rate - 0.7) * 100
    else:
        bitterness = 30 + (extraction_rate - 0.85) * 200
    bitterness = min(100, max(0, bitterness))
    
    if acidity > 70:
        sweetness = sweetness * (1 - (acidity - 70) / 100)
    if bitterness > 60:
        acidity = acidity * (1 - (bitterness - 60) / 150)
    
    #баланс
    if acidity > 60 and bitterness < 25:
        balance = 'acidic'
        temp_adjustment = 3
    elif bitterness > 50:
        balance = 'bitter'
        temp_adjustment = -3
    elif acidity > 50 and bitterness > 40:
        balance = 'bitter'
        temp_adjustment = -2
    else:
        balance = 'balanced'
        temp_adjustment = 0
    
    #расчет tds
    tds = calculate_tds(extraction_rate, ratio)
    
    #экстракция
    extraction_percent = extraction_rate * 22.5
    extraction_percent = min(24, max(14, extraction_percent))
    
    return {
        'acidity': round(acidity, 1),
        'sweetness': round(sweetness, 1),
        'bitterness': round(bitterness, 1),
        'balance': balance,
        'temp_adjustment': temp_adjustment,
        'tds': round(tds, 2),
        'extraction_yield': round(extraction_percent, 1),
    }

def calculate_full_prediction(recipe):

    from .models import TastePrediction

    coffee = recipe.coffee
    altitude = coffee.get_avg_altitude()

    acidity_factor = calculate_acidity_factor(
        coffee.acidity_score,
        altitude,
        coffee.process_method
    )

    grind_factor = recipe.get_grind_factor()
    ratio = recipe.get_ratio()

    extraction = calculate_extraction_rate(
        recipe.water_temperature,
        recipe.brew_time_seconds,
        grind_factor,
        ratio
    )

    taste = predict_taste_profile(acidity_factor, extraction, ratio)

    prediction, created = TastePrediction.objects.update_or_create(
        recipe=recipe,
        defaults={
            'acidity_intensity': taste['acidity'],
            'sweetness_intensity': taste['sweetness'],
            'bitterness_intensity': taste['bitterness'],
            'balance_type': taste['balance'],
            'recommended_temperature_adjustment': taste['temp_adjustment'],
            'tds_estimate': taste['tds'],
            'extraction_yield': taste['extraction_yield'],
        }
    )
    return prediction

def recommend_optimal_recipe():
    return None

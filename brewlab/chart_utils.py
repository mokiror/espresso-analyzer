#создание графиков с помощью plotly

import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import json
from plotly.offline import plot
from django.utils.safestring import mark_safe

def create_taste_triangle(acidity, sweetness, bitterness):
    #создаем график вкусового профиля

    data = pd.DataFrame({
        'Параметр': ['Кислотность', 'Сладость', 'Горечь'],
        'Значение': [acidity, sweetness, bitterness],
        'Цвет': ['#e74c3c', '#2ecc71', '#f39c12']
    })

    #создаём радиальный график
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[acidity, sweetness, bitterness, acidity],
        theta=['Кислотность', 'Сладость', 'Горечь', 'Кислотность'],
        fill='toself',
        name='Вкусовой профиль',
        line_color='#2c1810',
        fillcolor='rgba(44, 24, 16, 0.3)',
        marker=dict(
            size=10,
            color=['#e74c3c', '#2ecc71', '#f39c12'],
        )
    ))

    #вид
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=12),
                gridcolor='rgba(0,0,0,0.1)',
                gridwidth=1,
            ),
            angularaxis=dict(
                tickfont=dict(size=14, color='#2c1810'),
                gridcolor='rgba(0,0,0,0.1)',
                gridwidth=1,
            ),
        ),
        showlegend=True,
        legend=dict(
            x=0.5,
            y=1.1,
            orientation='h',
            font=dict(size=14),
        ),
        margin=dict(l=80, r=80, t=80, b=80),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
    )

    #добавляем рекомендации
    max_value = max(acidity, sweetness, bitterness)
    if max_value == acidity and acidity > 60:
        recommendation = "Кислый ☕"
        color = '#e74c3c'
    elif max_value == bitterness and bitterness > 50:
        recommendation = "Горький 🔥"
        color = '#f39c12'
    elif sweetness > 60:
        recommendation = "Сладкий 🌸"
        color = '#2ecc71'
    else:
        recommendation = "Сбалансированный вкус ⚖️"
        color = '#3498db'

    fig.add_annotation(
        text=f"<b>{recommendation}</b>",
        x=0.5,
        y=1.15,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=16, color=color),
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor=color,
        borderwidth=2,
        borderpad=4,
    )

    #добавляем значения в график
    fig.add_annotation(
        text=f"Кислотность: {acidity:.1f}",
        x=0.9,
        y=1.05,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=12, color='#e74c3c'),
    )
    fig.add_annotation(
        text=f"Сладость: {sweetness:.1f}",
        x=0.9,
        y=0.95,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=12, color='#2ecc71'),
    )
    fig.add_annotation(
        text=f"Горечь: {bitterness:.1f}",
        x=0.9,
        y=0.85,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=12, color='#f39c12'),
    )
    plot_div = plot(fig, output_type='div', include_plotlyjs='cdn')

    return mark_safe(plot_div)

def create_temperature_chart(temperatures, sweetness_scores, acidity_scores, bitterness_scores):

    #график зависимости вкуса от температуры
    fig = go.Figure()

    #добавляем линии для каждого параметра
    fig.add_trace(go.Scatter(
        x=temperatures,
        y=sweetness_scores,
        name='Сладость',
        line=dict(color='#2ecc71', width=3),
        marker=dict(size=8, color='#2ecc71'),
        mode='lines+markers',
    ))

    fig.add_trace(go.Scatter(
        x=temperatures,
        y=acidity_scores,
        name='Кислотность',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8, color='#e74c3c'),
        mode='lines+markers',
    ))

    fig.add_trace(go.Scatter(
        x=temperatures,
        y=bitterness_scores,
        name='Горечь',
        line=dict(color='#f39c12', width=3),
        marker=dict(size=8, color='#f39c12'),
        mode='lines+markers',
    ))

    #ищем оптимальную температуру
    optimal_temp = temperatures[sweetness_scores.index(max(sweetness_scores))]

    fig.add_vline(
        x=optimal_temp,
        line_dash="dash",
        line_color="#3498db",
        annotation_text=f"Оптимальная температура: {optimal_temp}°C",
        annotation_position="top",
        annotation_font=dict(color="#3498db", size=14),
    )

    #внешний вид
    fig.update_layout(
        title={
            'text': 'Зависимость вкуса от температуры заваривания',
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=20, color='#2c1810')
        },
        xaxis_title='Температура (°C)',
        yaxis_title='Интенсивность (0-100)',
        hovermode='x',
        legend=dict(
            x=0.01,
            y=0.99,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1,
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=450,
        xaxis=dict(
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
        ),
        yaxis=dict(
            gridcolor='rgba(0,0,0,0.1)',
            gridwidth=1,
            range=[0, 100],
        ),
    )

    plot_div = plot(fig, output_type='div', include_plotlyjs='cdn')

    return mark_safe(plot_div)


def create_balance_gauge(balance_type, value=75):

    #индикатор баланса
    colors = {
        'acidic': '#e74c3c',
        'balanced': '#27ae60',
        'bitter': '#f39c12',
    }

    color = colors.get(balance_type, '#3498db')

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': "Баланс вкуса", 'font': {'size': 24}},
        delta={'reference': 50, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "gray"},  # ← ИСПРАВЛЕНО
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 33], 'color': '#e74c3c', 'name': 'Кислый'},
                {'range': [33, 67], 'color': '#f1c40f', 'name': 'Сбалансированный'},
                {'range': [67, 100], 'color': '#f39c12', 'name': 'Горький'},
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    fig.update_layout(
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=20),
    )

    plot_div = plot(fig, output_type='div', include_plotlyjs='cdn')

    return mark_safe(plot_div)
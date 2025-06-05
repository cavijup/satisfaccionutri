import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.data_loader import load_data, get_filtered_data # Asegúrate que estas funciones existan en data_loader.py
from utils.data_processing import ( # Asegúrate que estas funciones existan en data_processing.py
    # plot_question_satisfaction, # Comentamos la función original
    # create_wordcloud, # Descomenta si usas wordcloud aquí
    COL_DESCRIPTIONS
)

def plot_question_satisfaction(df, question_col, question_text):
    """
    Crea un gráfico de barras horizontales profesional y limpio
    """
    label_col = question_col + '_label'

    # Determinar qué columna usar
    if label_col in df.columns and df[label_col].notna().any():
        col_to_use = label_col
    elif question_col in df.columns:
        col_to_use = question_col
    else:
        # Crear figura vacía
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos disponibles",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, 
            font=dict(size=16, color="#666666")
        )
        fig.update_layout(
            title=dict(
                text=question_text,
                font=dict(size=18, color='#333333'),
                x=0.5
            ),
            height=300
        )
        return fig

    # Contar frecuencias de las respuestas
    count_df = df[col_to_use].dropna().value_counts().reset_index()
    count_df.columns = ['Respuesta', 'Conteo']

    if count_df.empty:
        # Figura vacía
        fig = go.Figure()
        fig.add_annotation(
            text="Sin datos válidos",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="#666666")
        )
        fig.update_layout(
            title=dict(
                text=question_text,
                font=dict(size=18, color='#333333'),
                x=0.5
            ),
            height=300
        )
        return fig

    # Mapear respuestas para ordenamiento
    satisfaction_order = {
        "MUY INSATISFECHO/A": 1,
        "INSATISFECHO/A": 2, 
        "NI SATISFECHO/A NI INSATISFECHO/A": 3,
        "SATISFECHO/A": 4,
        "MUY SATISFECHO/A": 5,
        "MUY INSATISFECHO": 1,
        "INSATISFECHO": 2,
        "NEUTRAL": 3,
        "SATISFECHO": 4,
        "MUY SATISFECHO": 5,
        1: 1, 2: 2, 3: 3, 4: 4, 5: 5
    }
    
    # Ordenar datos
    count_df['orden'] = count_df['Respuesta'].map(satisfaction_order)
    count_df = count_df.sort_values('orden', na_position='first')
    
    # Colores profesionales y vivos
    colors = {
        "MUY INSATISFECHO/A": "#E53E3E",     # Rojo
        "INSATISFECHO/A": "#FF8C00",         # Naranja
        "NI SATISFECHO/A NI INSATISFECHO/A": "#FFD700", # Amarillo
        "SATISFECHO/A": "#38A169",           # Verde
        "MUY SATISFECHO/A": "#00B894",       # Verde azulado
        "MUY INSATISFECHO": "#E53E3E",
        "INSATISFECHO": "#FF8C00",
        "NEUTRAL": "#FFD700",
        "SATISFECHO": "#38A169",
        "MUY SATISFECHO": "#00B894",
        1: "#E53E3E", 2: "#FF8C00", 3: "#FFD700", 4: "#38A169", 5: "#00B894"
    }
    
    # Asignar colores
    count_df['color'] = count_df['Respuesta'].map(colors)
    count_df['color'] = count_df['color'].fillna("#718096")  # Gris para valores sin mapear
    
    # Calcular porcentajes
    total = count_df['Conteo'].sum()
    count_df['Porcentaje'] = (count_df['Conteo'] / total * 100).round(1)
    
    # Crear el gráfico horizontal
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=count_df['Conteo'],
        y=count_df['Respuesta'],
        orientation='h',
        marker=dict(
            color=count_df['color'],
            line=dict(color='white', width=1)
        ),
        text=[f'{conteo} ({porcentaje}%)' 
              for conteo, porcentaje in zip(count_df['Conteo'], count_df['Porcentaje'])],
        textposition='outside',
        textfont=dict(size=12, color='#333333'),
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "Cantidad: %{x}<br>" +
            "Porcentaje: %{customdata}%<br>" +
            "<extra></extra>"
        ),
        customdata=count_df['Porcentaje'],
        showlegend=False
    ))
    
    # Layout profesional
    fig.update_layout(
        title=dict(
            text=question_text,
            font=dict(size=18, color='#333333'),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title=dict(
                text="Cantidad de Respuestas",
                font=dict(size=14, color='#333333')
            ),
            showgrid=True,
            gridcolor='rgba(128, 128, 128, 0.2)',
            showline=True,
            linecolor='#E2E8F0',
            zeroline=True,
            zerolinecolor='#E2E8F0'
        ),
        yaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='#E2E8F0'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=max(300, 60 + (len(count_df) * 50)),
        margin=dict(l=150, r=100, t=80, b=60),
        hovermode='y unified',
        hoverlabel=dict(
            bgcolor="rgba(0, 0, 0, 0.8)",
            bordercolor="white",
            font=dict(size=12, color="white")
        )
    )
    
    return fig
    """
    Crea un gráfico de barras horizontales con máximo impacto visual
    """
    label_col = question_col + '_label'

    # Determinar qué columna usar
    if label_col in df.columns and df[label_col].notna().any():
        col_to_use = label_col
    elif question_col in df.columns:
        col_to_use = question_col
    else:
        # Crear figura vacía con diseño impactante
        fig = go.Figure()
        fig.add_annotation(
            text="⚠️ DATOS NO DISPONIBLES",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, 
            font=dict(size=24, color="#E74C3C", family="Montserrat", weight="bold"),
            bgcolor="rgba(231, 76, 60, 0.1)",
            bordercolor="#E74C3C",
            borderwidth=2,
            borderpad=20
        )
        fig.update_layout(
            title=dict(
                text=f"🚫 {question_text}",
                font=dict(size=20, color='#2C3E50', family="Montserrat", weight="bold"),
                x=0.5
            ),
            height=400,
            plot_bgcolor='#F8F9FA',
            paper_bgcolor='white'
        )
        return fig

    # Contar frecuencias de las respuestas
    count_df = df[col_to_use].dropna().value_counts().reset_index()
    count_df.columns = ['Respuesta', 'Conteo']

    if count_df.empty:
        # Figura vacía con diseño impactante
        fig = go.Figure()
        fig.add_annotation(
            text="📊 SIN DATOS VÁLIDOS",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=22, color="#F39C12", family="Montserrat", weight="bold"),
            bgcolor="rgba(243, 156, 18, 0.1)",
            bordercolor="#F39C12",
            borderwidth=2,
            borderpad=15
        )
        fig.update_layout(
            title=dict(
                text=f"📈 {question_text}",
                font=dict(size=20, color='#2C3E50', family="Montserrat", weight="bold"),
                x=0.5
            ),
            height=400,
            plot_bgcolor='#F8F9FA',
            paper_bgcolor='white'
        )
        return fig

    # Mapear respuestas para ordenamiento
    satisfaction_order = {
        "MUY INSATISFECHO/A": 1,
        "INSATISFECHO/A": 2, 
        "NI SATISFECHO/A NI INSATISFECHO/A": 3,
        "SATISFECHO/A": 4,
        "MUY SATISFECHO/A": 5,
        "MUY INSATISFECHO": 1,
        "INSATISFECHO": 2,
        "NEUTRAL": 3,
        "SATISFECHO": 4,
        "MUY SATISFECHO": 5,
        1: 1, 2: 2, 3: 3, 4: 4, 5: 5
    }
    
    # Ordenar datos (de menor a mayor para barras horizontales)
    count_df['orden'] = count_df['Respuesta'].map(satisfaction_order)
    count_df = count_df.sort_values('orden', na_position='first')  # Menor arriba
    
    # Paleta de colores vibrante y de alto impacto
    impact_colors = {
        "MUY INSATISFECHO/A": "#FF1744",     # Rojo intenso
        "INSATISFECHO/A": "#FF5722",         # Naranja fuerte
        "NI SATISFECHO/A NI INSATISFECHO/A": "#FFB300", # Amarillo dorado
        "SATISFECHO/A": "#4CAF50",           # Verde vibrante
        "MUY SATISFECHO/A": "#00E676",       # Verde neón
        "MUY INSATISFECHO": "#FF1744",
        "INSATISFECHO": "#FF5722", 
        "NEUTRAL": "#FFB300",
        "SATISFECHO": "#4CAF50",
        "MUY SATISFECHO": "#00E676",
        1: "#FF1744", 2: "#FF5722", 3: "#FFB300", 4: "#4CAF50", 5: "#00E676"
    }
    
    # Asignar colores
    count_df['color'] = count_df['Respuesta'].map(impact_colors)
    count_df['color'] = count_df['color'].fillna("#9E9E9E")
    
    # Calcular porcentajes
    total = count_df['Conteo'].sum()
    count_df['Porcentaje'] = (count_df['Conteo'] / total * 100).round(1)
    
    # Emojis de alto impacto
    emoji_map = {
        "MUY INSATISFECHO/A": "😠",
        "INSATISFECHO/A": "😞",
        "NI SATISFECHO/A NI INSATISFECHO/A": "😐",
        "SATISFECHO/A": "😊",
        "MUY SATISFECHO/A": "🤩",
        "MUY INSATISFECHO": "😠",
        "INSATISFECHO": "😞",
        "NEUTRAL": "😐",
        "SATISFECHO": "😊",
        "MUY SATISFECHO": "🤩",
        1: "😠", 2: "😞", 3: "😐", 4: "😊", 5: "🤩"
    }
    count_df['emoji'] = count_df['Respuesta'].map(emoji_map).fillna("📊")
    
    # Crear etiquetas con emojis grandes y texto impactante
    count_df['etiqueta_completa'] = count_df['emoji'] + "  " + count_df['Respuesta'].astype(str)
    
    # Crear el gráfico horizontal de alto impacto
    fig = go.Figure()
    
    # Añadir barras con efectos visuales extremos
    fig.add_trace(go.Bar(
        x=count_df['Conteo'],
        y=count_df['etiqueta_completa'],
        orientation='h',
        marker=dict(
            color=count_df['color'],
            line=dict(color='white', width=3),
            opacity=0.95,
            # Añadir gradiente y efectos 3D
            pattern=dict(
                shape="",
                bgcolor=count_df['color'],
                fgcolor=count_df['color']
            )
        ),
        text=[f'<b>{conteo}</b><br><span style="font-size:14px">({porcentaje}%)</span>' 
              for conteo, porcentaje in zip(count_df['Conteo'], count_df['Porcentaje'])],
        textposition='outside',
        textfont=dict(
            size=16, 
            color='#2C3E50',
            family="Montserrat",
            weight="bold"
        ),
        hovertemplate=(
            "<b style='font-size:16px'>%{y}</b><br>" +
            "<span style='font-size:14px'>Cantidad: <b>%{x}</b></span><br>" +
            "<span style='font-size:14px'>Porcentaje: <b>%{customdata}%</b></span><br>" +
            "<extra></extra>"
        ),
        customdata=count_df['Porcentaje'],
        showlegend=False
    ))
    
    # Añadir líneas de fondo para mayor impacto visual
    max_value = count_df['Conteo'].max()
    for i in range(len(count_df)):
        fig.add_shape(
            type="rect",
            x0=0, y0=i-0.4, x1=max_value*1.1, y1=i+0.4,
            fillcolor="rgba(0,0,0,0.03)" if i % 2 == 0 else "rgba(0,0,0,0.01)",
            layer="below",
            line=dict(width=0)
        )
    
    # Layout de máximo impacto visual
    fig.update_layout(
        title=dict(
            text=f"📊 <b>{question_text}</b>",
            font=dict(size=24, color='#2C3E50', family="Montserrat", weight="bold"),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title=dict(
                text="<b>CANTIDAD DE RESPUESTAS</b>",
                font=dict(size=16, color='#34495E', family="Montserrat", weight="bold"),
                standoff=20
            ),
            tickfont=dict(size=14, color='#2C3E50', family="Montserrat", weight="bold"),
            showgrid=True,
            gridcolor='rgba(52, 73, 94, 0.15)',
            gridwidth=2,
            griddash='dot',
            showline=True,
            linecolor='#2C3E50',
            linewidth=4,
            mirror='ticks',
            zeroline=True,
            zerolinecolor='#E74C3C',
            zerolinewidth=4,
            tickmode='linear',
            tick0=0,
            dtick=max(1, max_value//8) if max_value > 8 else 1,
            ticklen=8,
            tickwidth=3,
            tickcolor='#2C3E50',
            ticks='outside',
            separatethousands=True,
            showspikes=True,
            spikecolor='#E74C3C',
            spikethickness=2,
            spikemode='across'
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=15, color='#2C3E50', family="Montserrat", weight="bold"),
            showgrid=False,
            showline=True,
            linecolor='#2C3E50',
            linewidth=4,
            mirror='ticks',
            ticklen=12,
            tickwidth=4,
            tickcolor='#2C3E50',
            ticks='outside',
            tickmode='array',
            tickvals=list(range(len(count_df))),
            ticktext=count_df['etiqueta_completa'].tolist(),
            ticklabelstandoff=10,
            automargin=True,
            categoryorder='array',
            categoryarray=count_df['etiqueta_completa'].tolist()
        ),
        plot_bgcolor='#FAFBFC',
        paper_bgcolor='white',
        height=120 + (len(count_df) * 70),  # Altura dinámica generosa
        margin=dict(l=250, r=120, t=100, b=80),
        hovermode='y unified',
        hoverlabel=dict(
            bgcolor="rgba(44, 62, 80, 0.9)",
            bordercolor="white",
            borderwidth=2,
            font=dict(size=14, color="white", family="Montserrat")
        ),
        dragmode='pan',
        showlegend=False,
        # Añadir decoraciones visuales
        annotations=[
            # Información total en estilo llamativo
            dict(
                text=f"<b style='font-size:18px; color:#E74C3C'>📊 TOTAL:</b><br>" +
                     f"<b style='font-size:22px; color:#2C3E50'>{total}</b><br>" +
                     f"<span style='font-size:14px; color:#7F8C8D'>respuestas válidas</span>",
                xref="paper", yref="paper",
                x=0.98, y=0.98,
                xanchor='right', yanchor='top',
                showarrow=False,
                font=dict(family="Montserrat"),
                bgcolor="rgba(255, 255, 255, 0.95)",
                bordercolor="#E74C3C",
                borderwidth=3,
                borderpad=15,
                # Añadir sombra visual
                layer="above"
            ),
            # Indicador de mejor/peor con más detalle
            dict(
                text=f"🏆 <b>MÁS FRECUENTE:</b> {count_df.iloc[-1]['emoji']} " +
                     f"{count_df.iloc[-1]['Respuesta']} ({count_df.iloc[-1]['Conteo']})<br>" +
                     f"⚠️ <b>MENOS FRECUENTE:</b> {count_df.iloc[0]['emoji']} " +
                     f"{count_df.iloc[0]['Respuesta']} ({count_df.iloc[0]['Conteo']})",
                xref="paper", yref="paper", 
                x=0.02, y=0.02,
                xanchor='left', yanchor='bottom',
                showarrow=False,
                font=dict(size=12, family="Montserrat", weight="bold"),
                bgcolor="rgba(236, 240, 241, 0.95)",
                bordercolor="#34495E",
                borderwidth=2,
                borderpad=10
            ),
            # Marca de agua con el título del aspecto
            dict(
                text=f"<i>{question_text.upper()}</i>",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                xanchor='center', yanchor='middle',
                showarrow=False,
                font=dict(size=32, color="rgba(44, 62, 80, 0.08)", family="Montserrat", weight="bold"),
                layer="below"
            )
        ],
        # Efectos de sombra y profundidad mejorados
        shapes=[
            # Marco decorativo superior
            dict(
                type="rect",
                x0=-max_value*0.02, y0=len(count_df)-0.3, 
                x1=max_value*1.08, y1=len(count_df)+0.3,
                fillcolor="rgba(231, 76, 60, 0.1)",
                line=dict(color="#E74C3C", width=3),
                layer="below"
            ),
            # Marco decorativo inferior  
            dict(
                type="rect",
                x0=-max_value*0.02, y0=-0.7, 
                x1=max_value*1.08, y1=0.3,
                fillcolor="rgba(39, 174, 96, 0.1)",
                line=dict(color="#27AE60", width=3),
                layer="below"
            ),
            # Línea vertical de énfasis en el centro
            dict(
                type="line",
                x0=max_value/2, y0=-0.5, 
                x1=max_value/2, y1=len(count_df)-0.5,
                line=dict(color="rgba(142, 68, 173, 0.3)", width=2, dash="longdash"),
                layer="below"
            )
        ]
    )
    
    # Añadir línea de referencia promedio con estilo
    if len(count_df) >= 2:
        promedio = count_df['Conteo'].mean()
        fig.add_vline(
            x=promedio,
            line_dash="dash",
            line_color="#8E44AD",
            line_width=4,
            opacity=0.8,
            annotation_text=f"📊 PROMEDIO: {promedio:.1f}",
            annotation_position="top",
            annotation_font=dict(size=14, color="#8E44AD", family="Montserrat", weight="bold"),
            annotation_bgcolor="rgba(142, 68, 173, 0.1)",
            annotation_bordercolor="#8E44AD",
            annotation_borderwidth=2
        )
    
    return fig

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Abarrotes",
    page_icon="📦",
    layout="wide"
)

# Título y descripción
st.title("Análisis de Satisfacción - Abarrotes")
st.markdown("""
Esta sección presenta el análisis detallado de la satisfacción con los abarrotes entregados,
incluyendo fechas de vencimiento, tipo de empaque y correspondencia con la lista de mercado.
""")

# --- Carga de Datos ---
# Cargar los datos originales (usará caché si Home.py ya lo hizo)
# @st.cache_data(show_spinner="Cargando datos...") # No cachear aquí si Home.py ya lo hace con la misma función
def get_data():
    df = load_data()
    return df

df_pagina = get_data()

if df_pagina is None or df_pagina.empty:
    st.error("1_Abarrotes.py: No se pudieron cargar los datos iniciales desde load_data().")
    st.stop()
# else: # No es necesario mostrar mensaje de éxito aquí de nuevo
    # st.success(f"Datos cargados para Abarrotes. Registros iniciales: {len(df_pagina)}")


# --- Sidebar para Filtros (similar a Home.py) ---
# Conservamos la sidebar pero no la usaremos para filtrar los datos
st.sidebar.title("Filtros (Desactivados)")
date_range_selected = None
selected_comuna = "Todas"
selected_barrio = "Todos"
selected_nodo = "Todos"

# Re-declarar filtros para que estén disponibles en esta página (solo para mostrar en la UI)
# Filtro por fecha
if 'fecha' in df_pagina.columns and pd.api.types.is_datetime64_any_dtype(df_pagina['fecha']):
    valid_dates = df_pagina['fecha'].dropna()
    if not valid_dates.empty:
        try:
            min_date_dt = valid_dates.min()
            max_date_dt = valid_dates.max()
            if min_date_dt <= max_date_dt:
                default_start_date = min_date_dt.date()
                default_end_date = max_date_dt.date()
                # Usar una KEY única para este filtro si se repite en otras páginas
                date_range_selected = st.sidebar.date_input(
                    "Rango de fechas (Desactivado)",
                    value=[default_start_date, default_end_date],
                    min_value=default_start_date,
                    max_value=default_end_date,
                    key='date_filter_abarrotes' # Key específica para esta página
                )
            else:
                 st.sidebar.warning("Rango de fechas inválido.")
        except Exception as e_date_filter_ui:
            st.sidebar.error(f"Error en filtro de fecha: {e_date_filter_ui}")

# Filtro por ubicación
if 'comuna' in df_pagina.columns:
    all_comunas = ["Todas"] + sorted([str(x) for x in df_pagina['comuna'].dropna().unique()])
    selected_comuna = st.sidebar.selectbox("Comuna (Desactivado)", all_comunas, index=0, key='comuna_filter_abarrotes')
# else: st.sidebar.info("Columna 'comuna' no disponible.") # Evitar repetir mensajes

if 'barrio' in df_pagina.columns:
    all_barrios = ["Todos"] + sorted([str(x) for x in df_pagina['barrio'].dropna().unique()])
    selected_barrio = st.sidebar.selectbox("Barrio (Desactivado)", all_barrios, index=0, key='barrio_filter_abarrotes')
# else: st.sidebar.info("Columna 'barrio' no disponible.")

if 'nodo' in df_pagina.columns:
    all_nodos = ["Todos"] + sorted([str(x) for x in df_pagina['nodo'].dropna().unique()])
    selected_nodo = st.sidebar.selectbox("Nodo (Desactivado)", all_nodos, index=0, key='nodo_filter_abarrotes')
# else: st.sidebar.info("Columna 'nodo' no disponible.")

# Información sobre filtros desactivados
st.sidebar.info("Los filtros están desactivados temporalmente para mostrar todos los datos disponibles.")

# --- NO APLICAR FILTROS - Usar el DataFrame completo ---
# En lugar de filtrar, simplemente usamos el DataFrame completo
filtered_df_pagina = df_pagina.copy()  # Usar todos los datos sin filtrar

# Mostrar métrica de encuestas para esta página
st.sidebar.metric("Total de Encuestas (Abarrotes)", len(filtered_df_pagina))


# --- Contenido de la Página (si hay datos) ---
if filtered_df_pagina.empty:
    st.warning("No se encontraron registros para el análisis de Abarrotes.")
    print(f"WARN 1_Abarrotes.py: filtered_df_pagina está vacío.")
else:
    print(f"INFO 1_Abarrotes.py: Mostrando contenido con {len(filtered_df_pagina)} filas totales.")
    # --- Análisis de Abarrotes ---

    # Mapeo de las columnas de abarrotes (usar COL_DESCRIPTIONS si es posible)
    abarrotes_cols_map = {
        '9fecha_vencimiento': COL_DESCRIPTIONS.get('9fecha_vencimiento', 'Fecha de vencimiento'),
        '10tipo_empaque': COL_DESCRIPTIONS.get('10tipo_empaque', 'Tipo de empaque'),
        '11productos_iguales_lista_mercado': COL_DESCRIPTIONS.get('11productos_iguales_lista_mercado', 'Correspondencia con lista')
    }

    # Análisis de satisfacción por pregunta
    st.header("Satisfacción con los Abarrotes")

    # Comprobar si existen las columnas de abarrotes y tienen datos válidos (numéricos o etiquetas)
    # Usar .notna() porque la columna _label puede existir pero estar llena de NaNs si la conversión falló
    valid_display_cols = []
    for col_key in abarrotes_cols_map.keys():
        label_col = col_key + '_label'
        # Priorizar _label, si no existe o está vacía, verificar la columna numérica original
        if label_col in filtered_df_pagina.columns and filtered_df_pagina[label_col].notna().any():
            valid_display_cols.append(col_key)
        elif col_key in filtered_df_pagina.columns and pd.api.types.is_numeric_dtype(filtered_df_pagina[col_key].dtype) and filtered_df_pagina[col_key].notna().any():
            valid_display_cols.append(col_key)
            print(f"WARN 1_Abarrotes.py: Usando columna numérica '{col_key}' directamente porque '{label_col}' falta o está vacía.")


    if not valid_display_cols:
        st.warning("No se encontraron datos de satisfacción válidos para Abarrotes.")
    else:
        # Mostrar gráficos uno por uno para máximo impacto
        for col_key in valid_display_cols:
            col_description = abarrotes_cols_map[col_key]
            # Seleccionar la columna correcta (priorizar _label)
            plot_col = col_key + '_label' if col_key + '_label' in filtered_df_pagina.columns and filtered_df_pagina[col_key + '_label'].notna().any() else col_key

            print(f"DEBUG 1_Abarrotes.py: Intentando graficar '{plot_col}' para '{col_description}'")
            try:
                fig = plot_question_satisfaction(filtered_df_pagina, col_key, col_description) # Pasar col_key, la función usará _label
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    # Añadir separador visual entre gráficos
                    st.markdown("---")
                else:
                    # La función plot_question_satisfaction ya imprime si no hay datos
                    st.info(f"No hay datos suficientes o válidos para graficar '{col_description}'.")
            except Exception as e_plot:
                 st.error(f"Error al graficar '{col_description}': {e_plot}")
                 print(f"ERROR 1_Abarrotes.py - plot_question_satisfaction para '{col_key}': {e_plot}")


    # --- Análisis de Comedores con Insatisfacción ---
    st.header("Comedores con Niveles de Insatisfacción Reportados")

    # Verificar columnas necesarias: identificación de comedor y columnas de satisfacción numéricas
    # Intentar encontrar una columna de identificación del comedor
    id_comedor_candidates = ['nombre_comedor', 'comedor', 'id_comedor', 'nombre del comedor'] # Añade otros posibles nombres
    id_comedor_col = next((col for col in id_comedor_candidates if col in filtered_df_pagina.columns), None)

    satisfaction_numeric_cols = [col for col in abarrotes_cols_map.keys() if col in filtered_df_pagina.columns and pd.api.types.is_numeric_dtype(filtered_df_pagina[col])]

    if not satisfaction_numeric_cols:
        st.info("No hay columnas numéricas de satisfacción de abarrotes para analizar insatisfacción.")
    elif not id_comedor_col:
        st.warning("No se encontró una columna para identificar el comedor (ej. 'nombre_comedor', 'comedor'). No se puede agrupar.")
    else:
        print(f"DEBUG 1_Abarrotes.py: Analizando insatisfacción. ID Comedor: '{id_comedor_col}', Columnas numéricas: {satisfaction_numeric_cols}")
        try:
            # Crear dataframe para análisis, asegurando que las columnas sean numéricas
            analisis_df = filtered_df_pagina[[id_comedor_col] + satisfaction_numeric_cols].copy()
            for col in satisfaction_numeric_cols:
                analisis_df[col] = pd.to_numeric(analisis_df[col], errors='coerce')

            # Identificar filas con insatisfacción (valor <= 2) en CUALQUIERA de las columnas numéricas
            insatisfaccion_mask = (analisis_df[satisfaction_numeric_cols] <= 2).any(axis=1)

            if not insatisfaccion_mask.any():
                st.success("No se encontraron reportes de insatisfacción (puntaje <= 2) para Abarrotes con los datos actuales.")
            else:
                insatisfechos_df = analisis_df[insatisfaccion_mask]
                print(f"DEBUG 1_Abarrotes.py: {len(insatisfechos_df)} filas con al menos una insatisfacción encontrada.")

                # Agrupar por comedor y contar cuántas veces aparece cada comedor insatisfecho
                conteo_comedores = insatisfechos_df[id_comedor_col].value_counts().reset_index()
                conteo_comedores.columns = ['Comedor', 'Número de Reportes con Insatisfacción']

                # Opcional: Detallar qué aspectos fueron insatisfactorios por comedor (más complejo)
                # Por ahora, mostrar la tabla de conteo
                st.write("Comedores con al menos un reporte de insatisfacción (puntaje <= 2) en Abarrotes:")
                st.dataframe(conteo_comedores.sort_values('Número de Reportes con Insatisfacción', ascending=False), hide_index=True, use_container_width=True)

                # Podrías añadir aquí conclusiones textuales como las tenías antes
                # ...

        except Exception as e_insat:
            st.error(f"Error analizando comedores insatisfechos: {e_insat}")
            print(f"ERROR 1_Abarrotes.py - Análisis Insatisfacción: {e_insat}")


    # --- Conclusiones y recomendaciones ---
    st.header("Conclusiones y Recomendaciones (Abarrotes)")
    try:
        satisfaction_means = {}
        valid_cols_for_mean = [col for col in abarrotes_cols_map.keys() if col in filtered_df_pagina.columns and pd.api.types.is_numeric_dtype(filtered_df_pagina[col])]

        if valid_cols_for_mean:
             for col in valid_cols_for_mean:
                 numeric_data = pd.to_numeric(filtered_df_pagina[col], errors='coerce')
                 if numeric_data.notna().any():
                     satisfaction_means[col] = numeric_data.mean()

        if satisfaction_means:
             min_aspect_col = min(satisfaction_means, key=satisfaction_means.get)
             min_score = satisfaction_means[min_aspect_col]
             max_aspect_col = max(satisfaction_means, key=satisfaction_means.get)
             max_score = satisfaction_means[max_aspect_col]

             min_desc = abarrotes_cols_map.get(min_aspect_col, min_aspect_col)
             max_desc = abarrotes_cols_map.get(max_aspect_col, max_aspect_col)

             st.markdown(f"""
             Basado en el análisis de los datos:

             - El aspecto con **mayor satisfacción** es "{max_desc}" con un puntaje promedio de **{max_score:.2f}/5**.
             - El aspecto con **menor satisfacción** es "{min_desc}" con un puntaje promedio de **{min_score:.2f}/5**.

             **Recomendaciones:**
             - Centrar esfuerzos de mejora en "{min_desc}".
             - Mantener las buenas prácticas relacionadas con "{max_desc}".
             - Realizar seguimiento continuo de la satisfacción para identificar tendencias.
             """)
        else:
             st.info("No hay datos numéricos de satisfacción suficientes para generar conclusiones automáticas.")
    except Exception as e_conclu:
        st.error(f"Error generando conclusiones: {e_conclu}")
        print(f"ERROR 1_Abarrotes.py - Conclusiones: {e_conclu}")


# --- Footer ---
st.markdown("---")
st.markdown("Dashboard de Análisis de la Encuesta de Satisfacción | Sección: Abarrotes")
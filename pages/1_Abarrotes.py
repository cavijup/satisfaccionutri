import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_data, get_filtered_data # Asegúrate que estas funciones existan en data_loader.py
from utils.data_processing import ( # Asegúrate que estas funciones existan en data_processing.py
    # plot_question_satisfaction, # Comentamos la función original
    # create_wordcloud, # Descomenta si usas wordcloud aquí
    COL_DESCRIPTIONS
)

def plot_satisfaction_horizontal_professional(df, question_col, question_text):
    """
    Crea un gráfico de barras horizontales profesional con iconos
    """
    label_col = question_col + '_label'
    
    # Determinar columna a usar
    if label_col in df.columns and df[label_col].notna().any():
        col_to_use = label_col
    elif question_col in df.columns:
        col_to_use = question_col
    else:
        return None
    
    # Contar frecuencias
    count_df = df[col_to_use].dropna().value_counts().reset_index()
    count_df.columns = ['Respuesta', 'Conteo']
    
    if count_df.empty:
        return None
    
    # Ordenar por satisfacción
    satisfaction_order = {
        "MUY INSATISFECHO/A": 1, "INSATISFECHO/A": 2, 
        "NI SATISFECHO/A NI INSATISFECHO/A": 3,
        "SATISFECHO/A": 4, "MUY SATISFECHO/A": 5,
        1: 1, 2: 2, 3: 3, 4: 4, 5: 5
    }
    
    count_df['orden'] = count_df['Respuesta'].map(satisfaction_order)
    count_df = count_df.sort_values('orden', na_position='last')
    
    # Calcular porcentajes
    total = count_df['Conteo'].sum()
    count_df['Porcentaje'] = (count_df['Conteo'] / total * 100).round(1)
    
    # Colores y emojis
    colors = {
        "MUY INSATISFECHO/A": "#E74C3C", "INSATISFECHO/A": "#F39C12",
        "NI SATISFECHO/A NI INSATISFECHO/A": "#F1C40F",
        "SATISFECHO/A": "#27AE60", "MUY SATISFECHO/A": "#2ECC71",
        1: "#E74C3C", 2: "#F39C12", 3: "#F1C40F", 4: "#27AE60", 5: "#2ECC71"
    }
    
    emojis = {
        "MUY INSATISFECHO/A": "😠", "INSATISFECHO/A": "😕",
        "NI SATISFECHO/A NI INSATISFECHO/A": "😐",
        "SATISFECHO/A": "😊", "MUY SATISFECHO/A": "🤩",
        1: "😠", 2: "😕", 3: "😐", 4: "😊", 5: "🤩"
    }
    
    count_df['color'] = count_df['Respuesta'].map(colors).fillna("#95A5A6")
    count_df['emoji'] = count_df['Respuesta'].map(emojis).fillna("📊")
    
    # Crear etiquetas con emojis
    count_df['etiqueta_completa'] = count_df['emoji'] + " " + count_df['Respuesta'].astype(str)
    
    # Crear gráfico horizontal
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=count_df['Conteo'],
        y=count_df['etiqueta_completa'],
        orientation='h',
        marker=dict(
            color=count_df['color'],
            line=dict(color='white', width=1.5),
            opacity=0.9
        ),
        text=[f'{conteo} ({porcentaje}%)' for conteo, porcentaje in 
              zip(count_df['Conteo'], count_df['Porcentaje'])],
        textposition='outside',
        textfont=dict(size=12, color='#2C3E50', family="Inter"),
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "Cantidad: <b>%{x}</b><br>" +
            "Porcentaje: <b>%{customdata}%</b><br>" +
            "<extra></extra>"
        ),
        customdata=count_df['Porcentaje'],
        showlegend=False
    ))
    
    # Layout profesional
    fig.update_layout(
        title=dict(
            text=question_text,
            font=dict(size=18, color='#2C3E50', family="Inter", weight=600),
            x=0.5
        ),
        xaxis=dict(
            title="Cantidad de Respuestas",
            titlefont=dict(size=14, color='#34495E', family="Inter"),
            tickfont=dict(size=11, color='#34495E', family="Inter"),
            showgrid=True,
            gridcolor='#ECF0F1',
            gridwidth=1,
            showline=True,
            linecolor='#BDC3C7'
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=12, color='#2C3E50', family="Inter"),
            showgrid=False,
            showline=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=300 + (len(count_df) * 20),  # Altura dinámica
        margin=dict(l=200, r=100, t=80, b=60),
        annotations=[
            dict(
                text=f"Total: {total} respuestas",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                xanchor='left', yanchor='top',
                showarrow=False,
                font=dict(size=11, color="#7F8C8D", family="Inter"),
                bgcolor="rgba(236, 240, 241, 0.8)",
                bordercolor="#BDC3C7",
                borderwidth=1,
                borderpad=4
            )
        ]
    )
    
    return fig
    """
    Crea un medidor/gauge profesional para satisfacción promedio
    """
    # Calcular satisfacción promedio
    if question_col not in df.columns:
        return None
    
    numeric_data = pd.to_numeric(df[question_col], errors='coerce')
    if not numeric_data.notna().any():
        return None
    
    satisfaccion_promedio = numeric_data.mean()
    total_respuestas = numeric_data.count()
    
    # Determinar color según nivel
    if satisfaccion_promedio >= 4.0:
        color = "#27AE60"  # Verde
        estado = "Excelente"
    elif satisfaccion_promedio >= 3.5:
        color = "#2ECC71"  # Verde claro
        estado = "Bueno"
    elif satisfaccion_promedio >= 2.5:
        color = "#F39C12"  # Naranja
        estado = "Regular"
    elif satisfaccion_promedio >= 2.0:
        color = "#E67E22"  # Naranja oscuro
        estado = "Bajo"
    else:
        color = "#E74C3C"  # Rojo
        estado = "Crítico"
    
    # Crear medidor
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = satisfaccion_promedio,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {
            'text': question_text,
            'font': {'size': 18, 'color': '#2C3E50', 'family': 'Inter'}
        },
        delta = {
            'reference': 3.0,  # Punto neutral
            'increasing': {'color': "#27AE60"},
            'decreasing': {'color': "#E74C3C"}
        },
        gauge = {
            'axis': {
                'range': [None, 5],
                'tickwidth': 1,
                'tickcolor': "#34495E",
                'tickfont': {'size': 12, 'family': 'Inter'}
            },
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#BDC3C7",
            'steps': [
                {'range': [0, 2], 'color': "#FADBD8"},     # Rojo claro
                {'range': [2, 3], 'color': "#FCF3CF"},     # Amarillo claro
                {'range': [3, 4], 'color': "#D5DBDB"},     # Gris claro
                {'range': [4, 5], 'color': "#D4F1C4"}      # Verde claro
            ],
            'threshold': {
                'line': {'color': "#2C3E50", 'width': 4},
                'thickness': 0.75,
                'value': 4.0
            }
        },
        number = {
            'font': {'size': 32, 'color': color, 'family': 'Inter'},
            'suffix': "/5"
        }
    ))
    
    # Añadir anotaciones
    fig.add_annotation(
        text=f"<b>{estado}</b><br>{total_respuestas} respuestas",
        x=0.5, y=0.15,
        font=dict(size=16, color="#2C3E50", family="Inter"),
        showarrow=False,
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#BDC3C7",
        borderwidth=1,
        borderpad=10
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=40, r=40, t=80, b=60),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig
    """
    Crea un gráfico de dona profesional para satisfacción
    """
    label_col = question_col + '_label'
    
    # Determinar columna a usar
    if label_col in df.columns and df[label_col].notna().any():
        col_to_use = label_col
    elif question_col in df.columns:
        col_to_use = question_col
    else:
        return None
    
    # Contar frecuencias
    count_df = df[col_to_use].dropna().value_counts().reset_index()
    count_df.columns = ['Respuesta', 'Conteo']
    
    if count_df.empty:
        return None
    
    # Calcular porcentajes
    total = count_df['Conteo'].sum()
    count_df['Porcentaje'] = (count_df['Conteo'] / total * 100).round(1)
    
    # Colores profesionales
    colors = {
        "MUY INSATISFECHO/A": "#E74C3C",
        "INSATISFECHO/A": "#F39C12", 
        "NI SATISFECHO/A NI INSATISFECHO/A": "#F1C40F",
        "SATISFECHO/A": "#27AE60",
        "MUY SATISFECHO/A": "#2ECC71",
        1: "#E74C3C", 2: "#F39C12", 3: "#F1C40F", 4: "#27AE60", 5: "#2ECC71"
    }
    
    # Mapear colores
    count_df['color'] = count_df['Respuesta'].map(colors)
    count_df['color'] = count_df['color'].fillna("#95A5A6")
    
    # Crear gráfico de dona
    fig = go.Figure(data=[go.Pie(
        labels=count_df['Respuesta'],
        values=count_df['Conteo'],
        hole=0.6,  # Hace el agujero del dona
        marker=dict(
            colors=count_df['color'],
            line=dict(color='white', width=2)
        ),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=12, family="Inter"),
        hovertemplate=(
            "<b>%{label}</b><br>" +
            "Cantidad: <b>%{value}</b><br>" +
            "Porcentaje: <b>%{percent}</b><br>" +
            "<extra></extra>"
        )
    )])
    
    # Calcular satisfacción promedio (si es numérico)
    satisfaccion_promedio = None
    if question_col in df.columns:
        numeric_data = pd.to_numeric(df[question_col], errors='coerce')
        if numeric_data.notna().any():
            satisfaccion_promedio = numeric_data.mean()
    
    # Añadir texto central
    if satisfaccion_promedio:
        fig.add_annotation(
            text=f"<b>{satisfaccion_promedio:.1f}</b><br><span style='font-size:14px'>de 5.0</span>",
            x=0.5, y=0.5,
            font=dict(size=24, color="#2C3E50", family="Inter"),
            showarrow=False
        )
    else:
        fig.add_annotation(
            text=f"<b>{total}</b><br><span style='font-size:14px'>respuestas</span>",
            x=0.5, y=0.5,
            font=dict(size=24, color="#2C3E50", family="Inter"),
            showarrow=False
        )
    
    # Layout profesional
    fig.update_layout(
        title=dict(
            text=question_text,
            font=dict(size=18, color='#2C3E50', family="Inter", weight=600),
            x=0.5
        ),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(size=11, family="Inter")
        ),
        height=400,
        margin=dict(l=20, r=150, t=60, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig
    """
    Crea un gráfico de barras profesional y elegante para la distribución de respuestas.
    """
    label_col = question_col + '_label'

    # Determinar qué columna usar
    if label_col in df.columns and df[label_col].notna().any():
        col_to_use = label_col
    elif question_col in df.columns:
        col_to_use = question_col
    else:
        # Crear figura vacía con mensaje profesional
        fig = go.Figure()
        fig.add_annotation(
            text="Datos no disponibles",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, 
            font=dict(size=16, color="#6C757D", family="Inter")
        )
        fig.update_layout(
            title=dict(
                text=question_text,
                font=dict(size=18, color='#212529', family="Inter", weight=600),
                x=0.5
            ),
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig

    # Contar frecuencias de las respuestas
    count_df = df[col_to_use].dropna().value_counts().reset_index()
    count_df.columns = ['Respuesta', 'Conteo']

    if count_df.empty:
        # Figura vacía con mensaje profesional
        fig = go.Figure()
        fig.add_annotation(
            text="Sin datos válidos para mostrar",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="#6C757D", family="Inter")
        )
        fig.update_layout(
            title=dict(
                text=question_text,
                font=dict(size=18, color='#212529', family="Inter", weight=600),
                x=0.5
            ),
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig

    # Mapear respuestas para ordenamiento profesional
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
    count_df = count_df.sort_values('orden', na_position='last')
    
    # Paleta de colores profesional y elegante
    professional_colors = {
        "MUY INSATISFECHO/A": "#DC3545",     # Rojo corporativo
        "INSATISFECHO/A": "#FD7E14",         # Naranja corporativo
        "NI SATISFECHO/A NI INSATISFECHO/A": "#FFC107", # Amarillo corporativo
        "SATISFECHO/A": "#28A745",           # Verde corporativo
        "MUY SATISFECHO/A": "#20C997",       # Verde esmeralda
        "MUY INSATISFECHO": "#DC3545",
        "INSATISFECHO": "#FD7E14", 
        "NEUTRAL": "#FFC107",
        "SATISFECHO": "#28A745",
        "MUY SATISFECHO": "#20C997",
        1: "#DC3545", 2: "#FD7E14", 3: "#FFC107", 4: "#28A745", 5: "#20C997"
    }
    
    # Asignar colores
    count_df['color'] = count_df['Respuesta'].map(professional_colors)
    count_df['color'] = count_df['color'].fillna("#6C757D")  # Gris neutro para no mapeados
    
    # Calcular porcentajes
    total = count_df['Conteo'].sum()
    count_df['Porcentaje'] = (count_df['Conteo'] / total * 100).round(1)
    
    # Crear el gráfico profesional
    fig = go.Figure()
    
    # Agregar barras con estilo profesional
    fig.add_trace(go.Bar(
        x=count_df['Respuesta'],
        y=count_df['Conteo'],
        marker=dict(
            color=count_df['color'],
            line=dict(color='white', width=1.5),
            opacity=0.9
        ),
        text=[f'{conteo}<br>({porcentaje}%)' for conteo, porcentaje in zip(count_df['Conteo'], count_df['Porcentaje'])],
        textposition='outside',
        textfont=dict(
            size=12, 
            color='#495057',
            family="Inter"
        ),
        hovertemplate=(
            "<b>%{x}</b><br>" +
            "Cantidad: <b>%{y}</b><br>" +
            "Porcentaje: <b>%{customdata}%</b><br>" +
            "<extra></extra>"
        ),
        customdata=count_df['Porcentaje'],
        showlegend=False
    ))
    
    # Layout profesional y limpio
    fig.update_layout(
        title=dict(
            text=question_text,
            font=dict(size=18, color='#212529', family="Inter", weight=600),
            x=0.5,
            y=0.95,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(
                text="Nivel de Satisfacción",
                font=dict(size=14, color='#495057', family="Inter")
            ),
            tickfont=dict(size=11, color='#495057', family="Inter"),
            showgrid=False,
            showline=True,
            linecolor='#DEE2E6',
            linewidth=1,
            tickangle=-20 if len(count_df) > 3 else 0,
            categoryorder='array',
            categoryarray=count_df['Respuesta'].tolist()
        ),
        yaxis=dict(
            title=dict(
                text="Cantidad de Respuestas",
                font=dict(size=14, color='#495057', family="Inter")
            ),
            tickfont=dict(size=11, color='#495057', family="Inter"),
            showgrid=True,
            gridcolor='#F8F9FA',
            gridwidth=1,
            showline=True,
            linecolor='#DEE2E6',
            linewidth=1,
            zeroline=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=380,
        margin=dict(l=60, r=40, t=80, b=80),
        hovermode='x unified',
        # Añadir información contextual
        annotations=[
            dict(
                text=f"Total de respuestas: {total}",
                xref="paper", yref="paper",
                x=0.02, y=0.98, 
                xanchor='left', yanchor='top',
                showarrow=False,
                font=dict(size=10, color="#6C757D", family="Inter"),
                bgcolor="rgba(248, 249, 250, 0.8)",
                bordercolor="#DEE2E6",
                borderwidth=1,
                borderpad=4
            )
        ]
    )
    
   
    return 

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
        # Crear columnas para layout (máximo 2 gráficos por fila)
        num_cols = 2
        cols_layout = st.columns(num_cols)
        col_index = 0

        for col_key in valid_display_cols:
            col_description = abarrotes_cols_map[col_key]
            # Seleccionar la columna correcta (priorizar _label)
            plot_col = col_key + '_label' if col_key + '_label' in filtered_df_pagina.columns and filtered_df_pagina[col_key + '_label'].notna().any() else col_key

            with cols_layout[col_index % num_cols]:
                print(f"DEBUG 1_Abarrotes.py: Intentando graficar '{plot_col}' para '{col_description}'")
                try:
                    # Usar la nueva función profesional en lugar de la original
                    fig = plot_satisfaction_horizontal_professional(filtered_df_pagina, col_key, col_description)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # La función plot_question_satisfaction ya imprime si no hay datos
                        st.info(f"No hay datos suficientes o válidos para graficar '{col_description}'.")
                except Exception as e_plot:
                     st.error(f"Error al graficar '{col_description}': {e_plot}")
                     print(f"ERROR 1_Abarrotes.py - plot_question_satisfaction para '{col_key}': {e_plot}")

            col_index += 1


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
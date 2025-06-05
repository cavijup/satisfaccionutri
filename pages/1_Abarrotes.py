import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_data, get_filtered_data
from utils.data_processing import COL_DESCRIPTIONS

# Función de diseño minimalista y ultra profesional
def plot_question_satisfaction_improved(df, col_key, col_description):
    """
    Diseño minimalista premium con elegancia y sofisticación visual
    """
    label_col = col_key + '_label'
    
    # Determinar qué columna usar
    if label_col in df.columns and df[label_col].notna().any():
        plot_col = label_col
        data_series = df[label_col].dropna()
    elif col_key in df.columns:
        plot_col = col_key
        data_series = pd.to_numeric(df[col_key], errors='coerce').dropna()
    else:
        return None
    
    if data_series.empty:
        return None
    
    # Contar valores y crear DataFrame
    value_counts = data_series.value_counts().reset_index()
    value_counts.columns = ['Respuesta', 'Cantidad']
    value_counts = value_counts.sort_values('Cantidad', ascending=True)
    
    # Paleta de colores sofisticada y gradiente sutil
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
    bar_colors = [colors[i % len(colors)] for i in range(len(value_counts))]
    
    # Crear gráfico con diseño minimalista premium
    fig = go.Figure(data=[
        go.Bar(
            y=value_counts['Respuesta'],
            x=value_counts['Cantidad'],
            orientation='h',
            marker=dict(
                color=bar_colors,
                opacity=0.85,
                line=dict(width=0)  # Sin bordes para look minimalista
            ),
            text=[f'  {val}' for val in value_counts['Cantidad']],
            textposition='middle right',
            textfont=dict(
                color='white', 
                size=13, 
                family='Inter, system-ui, -apple-system, sans-serif',
                weight='600'
            ),
            hovertemplate='<b style="color:#2d3748;">%{y}</b><br>' +
                         '<span style="color:#667eea;">Respuestas:</span> <b>%{x}</b>' +
                         '<extra></extra>',
            hoverlabel=dict(
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='rgba(102,126,234,0.3)',
                borderwidth=1,
                font=dict(color='#2d3748', size=12)
            )
        )
    ])
    
    # Layout ultra minimalista y elegante
    fig.update_layout(
        title=dict(
            text=f'{col_description}',
            x=0.02,
            y=0.95,
            font=dict(
                size=18, 
                color='#2d3748', 
                family='Inter, system-ui, -apple-system, sans-serif',
                weight='700'
            )
        ),
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=True,
            zeroline=False,
            tickfont=dict(
                size=11, 
                color='#718096',
                family='Inter, system-ui, -apple-system, sans-serif'
            ),
            title=''  # Sin título para look minimalista
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=True,
            zeroline=False,
            tickfont=dict(
                size=12, 
                color='#4a5568',
                family='Inter, system-ui, -apple-system, sans-serif',
                weight='500'
            ),
            title=''  # Sin título para look minimalista
        ),
        plot_bgcolor='rgba(0,0,0,0)',  # Transparente total
        paper_bgcolor='rgba(0,0,0,0)',  # Transparente total
        height=320,
        margin=dict(l=10, r=60, t=50, b=10),
        font=dict(family='Inter, system-ui, -apple-system, sans-serif'),
        showlegend=False,
        # Sutil sombra y elevación visual
        annotations=[
            dict(
                text='',
                showarrow=False,
                xref="paper", yref="paper",
                x=0, y=0, xanchor='left', yanchor='bottom',
                bordercolor="rgba(102,126,234,0.1)",
                borderwidth=1,
                bgcolor="rgba(255,255,255,0.8)",
                opacity=0
            )
        ]
    )
    
    # Añadir línea decorativa sutil en la parte superior
    fig.add_shape(
        type="line",
        x0=0, y0=1, x1=1, y1=1,
        xref="paper", yref="paper",
        line=dict(color="rgba(102,126,234,0.2)", width=2)
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
@st.cache_data(show_spinner="Cargando datos...")
def get_data():
    df = load_data()
    return df

df_pagina = get_data()

if df_pagina is None or df_pagina.empty:
    st.error("1_Abarrotes.py: No se pudieron cargar los datos iniciales desde load_data().")
    st.stop()

# --- Sidebar para Filtros (similar a Home.py) ---
st.sidebar.title("Filtros (Desactivados)")
date_range_selected = None
selected_comuna = "Todas"
selected_barrio = "Todos"
selected_nodo = "Todos"

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
                date_range_selected = st.sidebar.date_input(
                    "Rango de fechas (Desactivado)",
                    value=[default_start_date, default_end_date],
                    min_value=default_start_date,
                    max_value=default_end_date,
                    key='date_filter_abarrotes'
                )
            else:
                 st.sidebar.warning("Rango de fechas inválido.")
        except Exception as e_date_filter_ui:
            st.sidebar.error(f"Error en filtro de fecha: {e_date_filter_ui}")

# Filtro por ubicación
if 'comuna' in df_pagina.columns:
    all_comunas = ["Todas"] + sorted([str(x) for x in df_pagina['comuna'].dropna().unique()])
    selected_comuna = st.sidebar.selectbox("Comuna (Desactivado)", all_comunas, index=0, key='comuna_filter_abarrotes')

if 'barrio' in df_pagina.columns:
    all_barrios = ["Todos"] + sorted([str(x) for x in df_pagina['barrio'].dropna().unique()])
    selected_barrio = st.sidebar.selectbox("Barrio (Desactivado)", all_barrios, index=0, key='barrio_filter_abarrotes')

if 'nodo' in df_pagina.columns:
    all_nodos = ["Todos"] + sorted([str(x) for x in df_pagina['nodo'].dropna().unique()])
    selected_nodo = st.sidebar.selectbox("Nodo (Desactivado)", all_nodos, index=0, key='nodo_filter_abarrotes')

st.sidebar.info("Los filtros están desactivados temporalmente para mostrar todos los datos disponibles.")

# --- NO APLICAR FILTROS - Usar el DataFrame completo ---
filtered_df_pagina = df_pagina.copy()
st.sidebar.metric("Total de Encuestas (Abarrotes)", len(filtered_df_pagina))

# --- Contenido de la Página (si hay datos) ---
if filtered_df_pagina.empty:
    st.warning("No se encontraron registros para el análisis de Abarrotes.")
    print(f"WARN 1_Abarrotes.py: filtered_df_pagina está vacío.")
else:
    print(f"INFO 1_Abarrotes.py: Mostrando contenido con {len(filtered_df_pagina)} filas totales.")
    
    # Mapeo de las columnas de abarrotes
    abarrotes_cols_map = {
        '9fecha_vencimiento': COL_DESCRIPTIONS.get('9fecha_vencimiento', 'Fecha de vencimiento'),
        '10tipo_empaque': COL_DESCRIPTIONS.get('10tipo_empaque', 'Tipo de empaque'),
        '11productos_iguales_lista_mercado': COL_DESCRIPTIONS.get('11productos_iguales_lista_mercado', 'Correspondencia con lista')
    }

    # Análisis de satisfacción por pregunta
    st.header("Satisfacción con los Abarrotes")

    valid_display_cols = []
    for col_key in abarrotes_cols_map.keys():
        label_col = col_key + '_label'
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
            with cols_layout[col_index % num_cols]:
                print(f"DEBUG 1_Abarrotes.py: Intentando graficar '{col_key}' para '{col_description}'")
                try:
                    fig = plot_question_satisfaction_improved(filtered_df_pagina, col_key, col_description)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"No hay datos suficientes o válidos para graficar '{col_description}'.")
                except Exception as e_plot:
                     st.error(f"Error al graficar '{col_description}': {e_plot}")
                     print(f"ERROR 1_Abarrotes.py - plot_question_satisfaction para '{col_key}': {e_plot}")

            col_index += 1

    # --- Análisis de Comedores con Insatisfacción ---
    st.header("Comedores con Niveles de Insatisfacción Reportados")

    id_comedor_candidates = ['nombre_comedor', 'comedor', 'id_comedor', 'nombre del comedor']
    id_comedor_col = next((col for col in id_comedor_candidates if col in filtered_df_pagina.columns), None)
    satisfaction_numeric_cols = [col for col in abarrotes_cols_map.keys() if col in filtered_df_pagina.columns and pd.api.types.is_numeric_dtype(filtered_df_pagina[col])]

    if not satisfaction_numeric_cols:
        st.info("No hay columnas numéricas de satisfacción de abarrotes para analizar insatisfacción.")
    elif not id_comedor_col:
        st.warning("No se encontró una columna para identificar el comedor (ej. 'nombre_comedor', 'comedor'). No se puede agrupar.")
    else:
        print(f"DEBUG 1_Abarrotes.py: Analizando insatisfacción. ID Comedor: '{id_comedor_col}', Columnas numéricas: {satisfaction_numeric_cols}")
        try:
            analisis_df = filtered_df_pagina[[id_comedor_col] + satisfaction_numeric_cols].copy()
            for col in satisfaction_numeric_cols:
                analisis_df[col] = pd.to_numeric(analisis_df[col], errors='coerce')

            insatisfaccion_mask = (analisis_df[satisfaction_numeric_cols] <= 2).any(axis=1)

            if not insatisfaccion_mask.any():
                st.success("No se encontraron reportes de insatisfacción (puntaje <= 2) para Abarrotes con los datos actuales.")
            else:
                insatisfechos_df = analisis_df[insatisfaccion_mask]
                print(f"DEBUG 1_Abarrotes.py: {len(insatisfechos_df)} filas con al menos una insatisfacción encontrada.")

                conteo_comedores = insatisfechos_df[id_comedor_col].value_counts().reset_index()
                conteo_comedores.columns = ['Comedor', 'Número de Reportes con Insatisfacción']

                st.write("Comedores con al menos un reporte de insatisfacción (puntaje <= 2) en Abarrotes:")
                st.dataframe(conteo_comedores.sort_values('Número de Reportes con Insatisfacción', ascending=False), hide_index=True, use_container_width=True)

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
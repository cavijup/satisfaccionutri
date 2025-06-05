import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from utils.data_loader import load_data, get_filtered_data # Asegúrate que estas funciones existan en data_loader.py
from utils.data_processing import ( # Asegúrate que estas funciones existan en data_processing.py
    plot_question_satisfaction,
    # create_wordcloud, # Descomenta si usas wordcloud aquí
    COL_DESCRIPTIONS
)

# Configuración de colores y estilos mejorados
COLORS = {
    'primary': '#2E86AB',      # Azul principal
    'secondary': '#A23B72',    # Magenta
    'accent': '#F18F01',       # Naranja
    'success': '#C73E1D',      # Rojo suave
    'background': '#FAFAFA',   # Gris muy claro
    'text': '#2C3E50',         # Gris oscuro
    'light_gray': '#ECF0F1',   # Gris claro
    'satisfaction_scale': [
        '#E74C3C',  # 1 - Muy insatisfecho (rojo)
        '#F39C12',  # 2 - Insatisfecho (naranja)
        '#F1C40F',  # 3 - Neutral (amarillo)
        '#27AE60',  # 4 - Satisfecho (verde claro)
        '#2ECC71'   # 5 - Muy satisfecho (verde)
    ]
}

# Configuración tipográfica mejorada
FONT_CONFIG = {
    'family': 'Inter, system-ui, -apple-system, sans-serif',
    'title_size': 18,
    'subtitle_size': 14,
    'axis_size': 12,
    'tick_size': 11,
    'legend_size': 12
}

def create_enhanced_satisfaction_chart(df, column_key, title, chart_type='bar'):
    """
    Crea gráficos de satisfacción con diseño visual mejorado
    """
    # Determinar columna a usar (priorizar _label)
    label_col = column_key + '_label'
    plot_col = label_col if label_col in df.columns and df[label_col].notna().any() else column_key
    
    if plot_col not in df.columns:
        return None
        
    # Filtrar datos válidos
    valid_data = df[plot_col].dropna()
    if valid_data.empty:
        return None
    
    # Contar valores y calcular porcentajes
    if pd.api.types.is_numeric_dtype(valid_data):
        # Para datos numéricos, mapear a etiquetas
        satisfaction_map = {1: 'Muy Insatisfecho', 2: 'Insatisfecho', 
                          3: 'Neutral', 4: 'Satisfecho', 5: 'Muy Satisfecho'}
        value_counts = valid_data.value_counts().sort_index()
        labels = [satisfaction_map.get(i, f'Valor {i}') for i in value_counts.index]
        colors = [COLORS['satisfaction_scale'][i-1] if 1 <= i <= 5 else COLORS['primary'] 
                 for i in value_counts.index]
    else:
        # Para datos categóricos
        value_counts = valid_data.value_counts()
        labels = value_counts.index.tolist()
        colors = COLORS['satisfaction_scale'][:len(labels)]
    
    values = value_counts.values
    percentages = (values / values.sum() * 100).round(1)
    
    if chart_type == 'donut':
        return create_donut_chart(labels, values, percentages, colors, title)
    else:
        return create_bar_chart(labels, values, percentages, colors, title)

def create_bar_chart(labels, values, percentages, colors, title):
    """Crea gráfico de barras con diseño mejorado"""
    fig = go.Figure()
    
    # Añadir barras con diseño mejorado
    fig.add_trace(go.Bar(
        x=labels,
        y=values,
        text=[f'{v}<br>({p}%)' for v, p in zip(values, percentages)],
        textposition='outside',
        textfont=dict(size=FONT_CONFIG['tick_size'], color=COLORS['text']),
        marker=dict(
            color=colors,
            line=dict(color='rgba(255,255,255,0.8)', width=1),
            opacity=0.9
        ),
        hovertemplate='<b>%{x}</b><br>Respuestas: %{y}<br>Porcentaje: %{text}<extra></extra>',
        showlegend=False
    ))
    
    # Configuración del layout mejorado
    fig.update_layout(
        title=dict(
            text=f'<b>{title}</b>',
            x=0.5,
            y=0.95,
            xanchor='center',
            font=dict(size=FONT_CONFIG['title_size'], color=COLORS['text'])
        ),
        xaxis=dict(
            title='',
            tickfont=dict(size=FONT_CONFIG['tick_size'], color=COLORS['text']),
            gridcolor='rgba(0,0,0,0.1)',
            linecolor='rgba(0,0,0,0.2)'
        ),
        yaxis=dict(
            title='Número de respuestas',
            titlefont=dict(size=FONT_CONFIG['subtitle_size'], color=COLORS['text']),
            tickfont=dict(size=FONT_CONFIG['tick_size'], color=COLORS['text']),
            gridcolor='rgba(0,0,0,0.1)',
            linecolor='rgba(0,0,0,0.2)'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=50, r=50, t=80, b=50),
        height=400,
        hovermode='x unified',
        font=dict(family=FONT_CONFIG['family'])
    )
    
    return fig

def create_donut_chart(labels, values, percentages, colors, title):
    """Crea gráfico de dona con diseño mejorado"""
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(
            colors=colors,
            line=dict(color='white', width=2)
        ),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=FONT_CONFIG['tick_size'], color=COLORS['text']),
        hovertemplate='<b>%{label}</b><br>Respuestas: %{value}<br>Porcentaje: %{percent}<extra></extra>',
        pull=[0.05 if i == 0 else 0 for i in range(len(labels))]  # Destacar primer segmento
    ))
    
    # Añadir texto central
    avg_score = sum(i * v for i, v in enumerate(values, 1)) / sum(values) if sum(values) > 0 else 0
    fig.add_annotation(
        text=f'<b>{avg_score:.1f}</b><br><span style="font-size:12px">Promedio</span>',
        x=0.5, y=0.5,
        font=dict(size=16, color=COLORS['text']),
        showarrow=False
    )
    
    fig.update_layout(
        title=dict(
            text=f'<b>{title}</b>',
            x=0.5,
            y=0.95,
            xanchor='center',
            font=dict(size=FONT_CONFIG['title_size'], color=COLORS['text'])
        ),
        showlegend=True,
        legend=dict(
            orientation='v',
            x=1.02,
            y=0.5,
            font=dict(size=FONT_CONFIG['legend_size'], color=COLORS['text'])
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=50, r=150, t=80, b=50),
        height=400,
        font=dict(family=FONT_CONFIG['family'])
    )
    
    return fig

def create_comparison_chart(df, columns_map):
    """Crea gráfico comparativo de todos los aspectos"""
    averages = []
    aspects = []
    
    for col_key, description in columns_map.items():
        if col_key in df.columns:
            numeric_data = pd.to_numeric(df[col_key], errors='coerce')
            if numeric_data.notna().any():
                avg = numeric_data.mean()
                averages.append(avg)
                aspects.append(description)
    
    if not averages:
        return None
    
    # Crear gráfico de barras horizontales
    fig = go.Figure()
    
    # Colores según el nivel de satisfacción
    bar_colors = [COLORS['satisfaction_scale'][min(4, max(0, int(avg)-1))] for avg in averages]
    
    fig.add_trace(go.Bar(
        y=aspects,
        x=averages,
        orientation='h',
        text=[f'{avg:.2f}' for avg in averages],
        textposition='inside',
        textfont=dict(size=FONT_CONFIG['subtitle_size'], color='white'),
        marker=dict(
            color=bar_colors,
            line=dict(color='white', width=1)
        ),
        hovertemplate='<b>%{y}</b><br>Promedio: %{x:.2f}/5<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='<b>Comparación de Satisfacción por Aspecto</b>',
            x=0.5,
            y=0.95,
            xanchor='center',
            font=dict(size=FONT_CONFIG['title_size'], color=COLORS['text'])
        ),
        xaxis=dict(
            title='Puntaje Promedio',
            range=[0, 5],
            tickfont=dict(size=FONT_CONFIG['tick_size'], color=COLORS['text']),
            titlefont=dict(size=FONT_CONFIG['subtitle_size'], color=COLORS['text']),
            gridcolor='rgba(0,0,0,0.1)'
        ),
        yaxis=dict(
            tickfont=dict(size=FONT_CONFIG['tick_size'], color=COLORS['text']),
            categoryorder='total ascending'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=200, r=50, t=80, b=50),
        height=300,
        font=dict(family=FONT_CONFIG['family'])
    )
    
    return fig

def display_enhanced_abarrotes_charts(filtered_df_pagina, abarrotes_cols_map):
    """
    Función principal para mostrar gráficos mejorados de abarrotes
    """
    st.header("📊 Satisfacción con los Abarrotes")
    
    # Verificar datos válidos
    valid_display_cols = []
    for col_key in abarrotes_cols_map.keys():
        label_col = col_key + '_label'
        if label_col in filtered_df_pagina.columns and filtered_df_pagina[label_col].notna().any():
            valid_display_cols.append(col_key)
        elif col_key in filtered_df_pagina.columns and pd.api.types.is_numeric_dtype(filtered_df_pagina[col_key].dtype) and filtered_df_pagina[col_key].notna().any():
            valid_display_cols.append(col_key)
    
    if not valid_display_cols:
        st.warning("⚠️ No se encontraron datos de satisfacción válidos para Abarrotes.")
        return
    
    # Gráfico comparativo general
    comp_fig = create_comparison_chart(filtered_df_pagina, abarrotes_cols_map)
    if comp_fig:
        st.plotly_chart(comp_fig, use_container_width=True)
        st.markdown("---")
    
    # Gráficos individuales con alternancia de estilos
    st.subheader("📈 Análisis Detallado por Aspecto")
    
    cols = st.columns(2)
    for idx, col_key in enumerate(valid_display_cols):
        col_description = abarrotes_cols_map[col_key]
        chart_type = 'donut' if idx % 2 == 0 else 'bar'  # Alternar estilos
        
        with cols[idx % 2]:
            try:
                fig = create_enhanced_satisfaction_chart(
                    filtered_df_pagina, col_key, col_description, chart_type
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"ℹ️ Sin datos suficientes para '{col_description}'")
            except Exception as e:
                st.error(f"❌ Error en gráfico '{col_description}': {e}")

def inject_custom_css():
    """Inyecta CSS personalizado para mejorar la apariencia"""
    st.markdown("""
    <style>
    /* Mejorar tipografía general */
    .main .block-container {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Estilo para headers */
    .main h1, .main h2, .main h3 {
        color: #2C3E50;
        font-weight: 600;
    }
    
    /* Mejorar spacing entre gráficos */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Estilo para métricas */
    [data-testid="metric-container"] {
        background-color: #FAFAFA;
        border: 1px solid #ECF0F1;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Mejorar apariencia de warnings y info */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid;
    }
    
    /* Personalizar sidebar */
    .css-1d391kg {
        background-color: #F8F9FA;
    }
    </style>
    """, unsafe_allow_html=True)

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Abarrotes",
    page_icon="📦",
    layout="wide"
)

# Inyectar CSS personalizado
inject_custom_css()

# Título y descripción
st.title("📦 Análisis de Satisfacción - Abarrotes")
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
    st.error("❌ No se pudieron cargar los datos iniciales desde load_data().")
    st.stop()

# --- Sidebar para Filtros (similar a Home.py) ---
# Conservamos la sidebar pero no la usaremos para filtrar los datos
st.sidebar.title("🔧 Filtros (Desactivados)")
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
                    "📅 Rango de fechas (Desactivado)",
                    value=[default_start_date, default_end_date],
                    min_value=default_start_date,
                    max_value=default_end_date,
                    key='date_filter_abarrotes' # Key específica para esta página
                )
            else:
                 st.sidebar.warning("⚠️ Rango de fechas inválido.")
        except Exception as e_date_filter_ui:
            st.sidebar.error(f"❌ Error en filtro de fecha: {e_date_filter_ui}")

# Filtro por ubicación
if 'comuna' in df_pagina.columns:
    all_comunas = ["Todas"] + sorted([str(x) for x in df_pagina['comuna'].dropna().unique()])
    selected_comuna = st.sidebar.selectbox("🏘️ Comuna (Desactivado)", all_comunas, index=0, key='comuna_filter_abarrotes')

if 'barrio' in df_pagina.columns:
    all_barrios = ["Todos"] + sorted([str(x) for x in df_pagina['barrio'].dropna().unique()])
    selected_barrio = st.sidebar.selectbox("🏠 Barrio (Desactivado)", all_barrios, index=0, key='barrio_filter_abarrotes')

if 'nodo' in df_pagina.columns:
    all_nodos = ["Todos"] + sorted([str(x) for x in df_pagina['nodo'].dropna().unique()])
    selected_nodo = st.sidebar.selectbox("📍 Nodo (Desactivado)", all_nodos, index=0, key='nodo_filter_abarrotes')

# Información sobre filtros desactivados
st.sidebar.info("ℹ️ Los filtros están desactivados temporalmente para mostrar todos los datos disponibles.")

# --- NO APLICAR FILTROS - Usar el DataFrame completo ---
# En lugar de filtrar, simplemente usamos el DataFrame completo
filtered_df_pagina = df_pagina.copy()  # Usar todos los datos sin filtrar

# Mostrar métrica de encuestas para esta página
st.sidebar.metric("📊 Total de Encuestas (Abarrotes)", len(filtered_df_pagina))

# --- Contenido de la Página (VERSIÓN MEJORADA) ---
if filtered_df_pagina.empty:
    st.warning("⚠️ No se encontraron registros para el análisis de Abarrotes.")
    print(f"WARN 1_Abarrotes.py: filtered_df_pagina está vacío.")
else:
    print(f"INFO 1_Abarrotes.py: Mostrando contenido con {len(filtered_df_pagina)} filas totales.")
    
    # --- Análisis de Abarrotes con Gráficos Mejorados ---
    
    # Mapeo de las columnas de abarrotes
    abarrotes_cols_map = {
        '9fecha_vencimiento': COL_DESCRIPTIONS.get('9fecha_vencimiento', 'Fecha de vencimiento'),
        '10tipo_empaque': COL_DESCRIPTIONS.get('10tipo_empaque', 'Tipo de empaque'),
        '11productos_iguales_lista_mercado': COL_DESCRIPTIONS.get('11productos_iguales_lista_mercado', 'Correspondencia con lista')
    }
    
    # Mostrar gráficos mejorados
    display_enhanced_abarrotes_charts(filtered_df_pagina, abarrotes_cols_map)

    # --- Análisis de Comedores con Insatisfacción (MEJORADO) ---
    st.markdown("---")
    st.header("🚨 Comedores con Niveles de Insatisfacción Reportados")

    # Verificar columnas necesarias: identificación de comedor y columnas de satisfacción numéricas
    id_comedor_candidates = ['nombre_comedor', 'comedor', 'id_comedor', 'nombre del comedor']
    id_comedor_col = next((col for col in id_comedor_candidates if col in filtered_df_pagina.columns), None)
    satisfaction_numeric_cols = [col for col in abarrotes_cols_map.keys() if col in filtered_df_pagina.columns and pd.api.types.is_numeric_dtype(filtered_df_pagina[col])]

    if not satisfaction_numeric_cols:
        st.info("ℹ️ No hay columnas numéricas de satisfacción de abarrotes para analizar insatisfacción.")
    elif not id_comedor_col:
        st.warning("⚠️ No se encontró una columna para identificar el comedor (ej. 'nombre_comedor', 'comedor'). No se puede agrupar.")
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
                st.success("✅ No se encontraron reportes de insatisfacción (puntaje ≤ 2) para Abarrotes con los datos actuales.")
            else:
                insatisfechos_df = analisis_df[insatisfaccion_mask]
                print(f"DEBUG 1_Abarrotes.py: {len(insatisfechos_df)} filas con al menos una insatisfacción encontrada.")

                # Agrupar por comedor y contar cuántas veces aparece cada comedor insatisfecho
                conteo_comedores = insatisfechos_df[id_comedor_col].value_counts().reset_index()
                conteo_comedores.columns = ['Comedor', 'Número de Reportes con Insatisfacción']

                # Crear visualización mejorada para comedores insatisfechos
                if len(conteo_comedores) > 0:
                    fig_insat = go.Figure()
                    
                    fig_insat.add_trace(go.Bar(
                        y=conteo_comedores['Comedor'].head(10),  # Top 10
                        x=conteo_comedores['Número de Reportes con Insatisfacción'].head(10),
                        orientation='h',
                        marker=dict(
                            color=COLORS['secondary'],
                            opacity=0.8,
                            line=dict(color='white', width=1)
                        ),
                        text=conteo_comedores['Número de Reportes con Insatisfacción'].head(10),
                        textposition='inside',
                        textfont=dict(color='white', size=12),
                        hovertemplate='<b>%{y}</b><br>Reportes: %{x}<extra></extra>'
                    ))
                    
                    fig_insat.update_layout(
                        title=dict(
                            text='<b>Top 10 Comedores con Más Reportes de Insatisfacción</b>',
                            x=0.5,
                            font=dict(size=FONT_CONFIG['title_size'], color=COLORS['text'])
                        ),
                        xaxis=dict(
                            title='Número de Reportes',
                            tickfont=dict(size=FONT_CONFIG['tick_size'], color=COLORS['text']),
                            titlefont=dict(size=FONT_CONFIG['subtitle_size'], color=COLORS['text']),
                            gridcolor='rgba(0,0,0,0.1)'
                        ),
                        yaxis=dict(
                            categoryorder='total ascending',
                            tickfont=dict(size=FONT_CONFIG['tick_size'], color=COLORS['text'])
                        ),
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        height=400,
                        margin=dict(l=200, r=50, t=80, b=50),
                        font=dict(family=FONT_CONFIG['family'])
                    )
                    
                    st.plotly_chart(fig_insat, use_container_width=True)
                
                # Tabla con estilo mejorado
                st.markdown("**📋 Detalle completo de comedores con insatisfacción:**")
                st.dataframe(
                    conteo_comedores.sort_values('Número de Reportes con Insatisfacción', ascending=False),
                    hide_index=True,
                    use_container_width=True
                )

        except Exception as e_insat:
            st.error(f"❌ Error analizando comedores insatisfechos: {e_insat}")
            print(f"ERROR 1_Abarrotes.py - Análisis Insatisfacción: {e_insat}")

    # --- Conclusiones y recomendaciones (MEJORADO) ---
    st.markdown("---")
    st.header("📋 Conclusiones y Recomendaciones")
    
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

            # Crear métricas visuales
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="🏆 Mayor Satisfacción",
                    value=f"{max_score:.2f}/5",
                    delta=max_desc
                )
            
            with col2:
                st.metric(
                    label="📉 Menor Satisfacción", 
                    value=f"{min_score:.2f}/5",
                    delta=min_desc,
                    delta_color="inverse"
                )
            
            with col3:
                overall_avg = np.mean(list(satisfaction_means.values()))
                st.metric(
                    label="📊 Promedio General",
                    value=f"{overall_avg:.2f}/5"
                )

            # Recomendaciones con mejor formato
            st.markdown(f"""
            ### 🎯 **Recomendaciones Estratégicas**
            
            **🔴 Área Prioritaria de Mejora:**
            - **{min_desc}** requiere atención inmediata (puntaje: {min_score:.2f}/5)
            - Implementar plan de acción específico para este aspecto
            
            **🟢 Fortaleza a Mantener:**
            - **{max_desc}** muestra excelentes resultados (puntaje: {max_score:.2f}/5)
            - Documentar buenas prácticas para replicar en otras áreas
            
            **📈 Acciones Sugeridas:**
            - Realizar seguimiento quincenal de indicadores
            - Capacitar equipos en aspectos con menor satisfacción
            - Establecer metas de mejora progresiva
            """)
        else:
            st.info("ℹ️ No hay datos numéricos de satisfacción suficientes para generar conclusiones automáticas.")
    
    except Exception as e_conclu:
        st.error(f"❌ Error generando conclusiones: {e_conclu}")
        print(f"ERROR 1_Abarrotes.py - Conclusiones: {e_conclu}")

# --- Footer mejorado ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7F8C8D; font-size: 14px; padding: 20px;'>
    📊 <strong>Dashboard de Análisis de Satisfacción</strong> | Sección: Abarrotes<br>
    <em>Análisis generado automáticamente basado en datos de encuestas</em>
</div>
""", unsafe_allow_html=True)
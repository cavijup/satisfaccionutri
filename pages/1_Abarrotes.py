import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.data_loader import load_data, get_filtered_data
from utils.data_processing import COL_DESCRIPTIONS

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Abarrotes",
    page_icon="📦",
    layout="wide"
)

def plot_question_satisfaction_visual(df, question_col, question_text):
    """
    Crea un gráfico de barras súper visual y llamativo para la distribución de respuestas.
    """
    label_col = question_col + '_label'

    if label_col not in df.columns:
        if question_col in df.columns:
            col_to_use = question_col
        else:
            # Crear figura vacía con mensaje
            fig = go.Figure()
            fig.add_annotation(
                text="❌ Datos no disponibles",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=20, color="red")
            )
            fig.update_layout(
                title=f"📊 {question_text}",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                height=400
            )
            return fig
    elif df[label_col].isna().all():
        col_to_use = question_col if question_col in df.columns else label_col
    else:
        col_to_use = label_col

    # Contar frecuencias de las respuestas
    count_df = df[col_to_use].dropna().value_counts().reset_index()
    count_df.columns = ['Respuesta', 'Conteo']

    if count_df.empty:
        # Figura vacía con mensaje
        fig = go.Figure()
        fig.add_annotation(
            text="⚠️ Sin datos válidos",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=18, color="orange")
        )
        fig.update_layout(
            title=f"📊 {question_text}",
            height=400
        )
        return fig

    # Mapear respuestas a valores numéricos para ordenar
    satisfaction_order = {
        "MUY INSATISFECHO/A": 1,
        "INSATISFECHO/A": 2,
        "NI SATISFECHO/A NI INSATISFECHO/A": 3,
        "SATISFECHO/A": 4,
        "MUY SATISFECHO/A": 5
    }
    
    # Intentar mapear y ordenar
    count_df['orden'] = count_df['Respuesta'].map(satisfaction_order)
    # Ordenar poniendo los NaN al final
    count_df = count_df.sort_values('orden', na_position='last')
    
    # Colores degradados y llamativos
    colors = {
        "MUY INSATISFECHO/A": "#FF1744",      # Rojo intenso
        "INSATISFECHO/A": "#FF9800",           # Naranja vibrante
        "NI SATISFECHO/A NI INSATISFECHO/A": "#FFC107",  # Amarillo dorado
        "SATISFECHO/A": "#4CAF50",             # Verde fresco
        "MUY SATISFECHO/A": "#00E676",         # Verde brillante
        1: "#FF1744", 2: "#FF9800", 3: "#FFC107", 4: "#4CAF50", 5: "#00E676"  # Para valores numéricos
    }
    
    # Asignar colores
    count_df['color'] = count_df['Respuesta'].map(colors)
    count_df['color'] = count_df['color'].fillna("#9E9E9E")  # Gris para no mapeados
    
    # Calcular porcentajes
    total = count_df['Conteo'].sum()
    count_df['Porcentaje'] = (count_df['Conteo'] / total * 100).round(1)
    
    # Crear emojis para cada respuesta
    emoji_map = {
        "MUY INSATISFECHO/A": "😠",
        "INSATISFECHO/A": "😕",
        "NI SATISFECHO/A NI INSATISFECHO/A": "😐",
        "SATISFECHO/A": "😊",
        "MUY SATISFECHO/A": "🤩",
        1: "😠", 2: "😕", 3: "😐", 4: "😊", 5: "🤩"
    }
    count_df['emoji'] = count_df['Respuesta'].map(emoji_map).fillna("📊")
    
    # Crear el gráfico con Plotly Graph Objects para más control
    fig = go.Figure()
    
    # Agregar barras con efectos visuales
    for i, row in count_df.iterrows():
        fig.add_trace(go.Bar(
            x=[row['Respuesta']],
            y=[row['Conteo']],
            name=row['Respuesta'],
            marker=dict(
                color=row['color'],
                line=dict(color='white', width=2),
                # Agregar gradiente y sombra
                pattern=dict(
                    shape="",
                    bgcolor=row['color'],
                    fgcolor=row['color']
                )
            ),
            text=f"{row['emoji']}<br>{row['Conteo']}<br>({row['Porcentaje']}%)",
            textposition='outside',
            textfont=dict(size=14, color='black', family="Arial Black"),
            hovertemplate=(
                f"<b>{row['emoji']} %{{x}}</b><br>"
                f"Cantidad: <b>%{{y}}</b><br>"
                f"Porcentaje: <b>{row['Porcentaje']}%</b><br>"
                "<extra></extra>"
            )
        ))
    
    # Personalizar layout con efectos visuales
    fig.update_layout(
        title=dict(
            text=f"📊 {question_text}",
            font=dict(size=20, color='#2E3440', family="Arial Black"),
            x=0.5,
            y=0.95
        ),
        xaxis=dict(
            title=dict(
                text="<b>Nivel de Satisfacción</b>",
                font=dict(size=14, color='#2E3440')
            ),
            tickfont=dict(size=12, color='#2E3440'),
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='#ECEFF4',
            tickangle=-45 if len(count_df) > 3 else 0
        ),
        yaxis=dict(
            title=dict(
                text="<b>Cantidad de Respuestas</b>",
                font=dict(size=14, color='#2E3440')
            ),
            tickfont=dict(size=12, color='#2E3440'),
            showgrid=True,
            gridcolor='#ECEFF4',
            gridwidth=1,
            zeroline=False,
            showline=True,
            linecolor='#ECEFF4'
        ),
        plot_bgcolor='rgba(0,0,0,0)',  # Fondo transparente
        paper_bgcolor='rgba(0,0,0,0)',  # Fondo transparente
        showlegend=False,
        height=450,
        margin=dict(l=50, r=50, t=80, b=100),
        # Agregar animaciones y efectos hover
        hovermode='closest',
        # Agregar anotaciones decorativas
        annotations=[
            dict(
                text=f"Total: {total} respuestas",
                xref="paper", yref="paper",
                x=1, y=1.02, xanchor='right', yanchor='bottom',
                showarrow=False,
                font=dict(size=12, color="#5E81AC"),
                bgcolor="rgba(94, 129, 172, 0.1)",
                bordercolor="#5E81AC",
                borderwidth=1
            )
        ]
    )
    
    # Agregar línea de referencia si hay suficientes datos
    if len(count_df) >= 3:
        promedio = count_df['Conteo'].mean()
        fig.add_hline(
            y=promedio,
            line_dash="dash",
            line_color="#BF616A",
            annotation_text=f"Promedio: {promedio:.1f}",
            annotation_position="top right",
            annotation_font=dict(size=10, color="#BF616A")
        )
    
    # Efectos adicionales para hacer más llamativo
    fig.update_traces(
        selector=dict(type='bar'),
        marker_line_width=2,
        opacity=0.9
    )
    
    return fig

# Título y descripción con estilo mejorado
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0; font-size: 2.5rem;">📦 Análisis de Satisfacción - Abarrotes</h1>
    <p style="color: rgba(255,255,255,0.9); margin: 1rem 0 0 0; font-size: 1.2rem;">
        Análisis detallado de satisfacción con abarrotes entregados
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
Esta sección presenta el análisis detallado de la satisfacción con los abarrotes entregados,
incluyendo fechas de vencimiento, tipo de empaque y correspondencia con la lista de mercado.
""")

# --- Carga de Datos ---
def get_data():
    df = load_data()
    return df

df_pagina = get_data()

if df_pagina is None or df_pagina.empty:
    st.error("1_Abarrotes.py: No se pudieron cargar los datos iniciales desde load_data().")
    st.stop()

# --- Sidebar para Filtros ---
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); border-radius: 10px; margin-bottom: 1rem;">
    <h3 style="color: white; margin: 0;">🎛️ Panel de Control</h3>
</div>
""", unsafe_allow_html=True)

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
                    "📅 Rango de fechas (Desactivado)",
                    value=[default_start_date, default_end_date],
                    min_value=default_start_date,
                    max_value=default_end_date,
                    key='date_filter_abarrotes'
                )
            else:
                st.sidebar.warning("⚠️ Rango de fechas inválido.")
        except Exception as e_date_filter_ui:
            st.sidebar.error(f"❌ Error en filtro de fecha: {e_date_filter_ui}")

# Filtros de ubicación con iconos
if 'comuna' in df_pagina.columns:
    all_comunas = ["Todas"] + sorted([str(x) for x in df_pagina['comuna'].dropna().unique()])
    selected_comuna = st.sidebar.selectbox("🏢 Comuna (Desactivado)", all_comunas, index=0, key='comuna_filter_abarrotes')

if 'barrio' in df_pagina.columns:
    all_barrios = ["Todos"] + sorted([str(x) for x in df_pagina['barrio'].dropna().unique()])
    selected_barrio = st.sidebar.selectbox("🏘️ Barrio (Desactivado)", all_barrios, index=0, key='barrio_filter_abarrotes')

if 'nodo' in df_pagina.columns:
    all_nodos = ["Todos"] + sorted([str(x) for x in df_pagina['nodo'].dropna().unique()])
    selected_nodo = st.sidebar.selectbox("🎯 Nodo (Desactivado)", all_nodos, index=0, key='nodo_filter_abarrotes')

# Información sobre filtros con estilo
st.sidebar.markdown("""
<div style="padding: 1rem; background: rgba(255, 193, 7, 0.1); border-left: 4px solid #FFC107; border-radius: 5px;">
    <p style="margin: 0; color: #856404;">
        <strong>ℹ️ Información:</strong><br>
        Los filtros están desactivados temporalmente para mostrar todos los datos disponibles.
    </p>
</div>
""", unsafe_allow_html=True)

# --- NO APLICAR FILTROS - Usar el DataFrame completo ---
filtered_df_pagina = df_pagina.copy()

# Mostrar métrica con estilo
st.sidebar.markdown("---")
total_encuestas = len(filtered_df_pagina)
st.sidebar.markdown(f"""
<div style="text-align: center; padding: 1rem; background: linear-gradient(45deg, #667eea, #764ba2); border-radius: 10px; color: white;">
    <h2 style="margin: 0; font-size: 2rem;">{total_encuestas}</h2>
    <p style="margin: 0.5rem 0 0 0;">📊 Total Encuestas</p>
</div>
""", unsafe_allow_html=True)

# --- Contenido de la Página ---
if filtered_df_pagina.empty:
    st.warning("⚠️ No se encontraron registros para el análisis de Abarrotes.")
    print(f"WARN 1_Abarrotes.py: filtered_df_pagina está vacío.")
else:
    print(f"INFO 1_Abarrotes.py: Mostrando contenido con {len(filtered_df_pagina)} filas totales.")

    # Mapeo de las columnas de abarrotes
    abarrotes_cols_map = {
        '9fecha_vencimiento': COL_DESCRIPTIONS.get('9fecha_vencimiento', 'Fecha de vencimiento'),
        '10tipo_empaque': COL_DESCRIPTIONS.get('10tipo_empaque', 'Tipo de empaque'),
        '11productos_iguales_lista_mercado': COL_DESCRIPTIONS.get('11productos_iguales_lista_mercado', 'Correspondencia con lista')
    }

    # Header con estilo para análisis de satisfacción
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin: 2rem 0;">
        <h2 style="color: white; margin: 0; font-size: 2rem;">📈 Satisfacción con los Abarrotes</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">Análisis detallado por aspecto</p>
    </div>
    """, unsafe_allow_html=True)

    # Comprobar columnas válidas
    valid_display_cols = []
    for col_key in abarrotes_cols_map.keys():
        label_col = col_key + '_label'
        if label_col in filtered_df_pagina.columns and filtered_df_pagina[label_col].notna().any():
            valid_display_cols.append(col_key)
        elif col_key in filtered_df_pagina.columns and pd.api.types.is_numeric_dtype(filtered_df_pagina[col_key].dtype) and filtered_df_pagina[col_key].notna().any():
            valid_display_cols.append(col_key)
            print(f"WARN 1_Abarrotes.py: Usando columna numérica '{col_key}' directamente porque '{label_col}' falta o está vacía.")

    if not valid_display_cols:
        st.warning("⚠️ No se encontraron datos de satisfacción válidos para Abarrotes.")
    else:
        # Crear columnas para layout con spacing mejorado
        num_cols = 2
        cols_layout = st.columns(num_cols, gap="large")
        col_index = 0

        for col_key in valid_display_cols:
            col_description = abarrotes_cols_map[col_key]

            with cols_layout[col_index % num_cols]:
                # Contenedor con borde y sombra para cada gráfico
                st.markdown(f"""
                <div style="padding: 1rem; border: 1px solid #E1E8ED; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1rem; background: white;">
                """, unsafe_allow_html=True)
                
                print(f"DEBUG 1_Abarrotes.py: Intentando graficar '{col_key}' para '{col_description}'")
                try:
                    fig = plot_question_satisfaction_visual(filtered_df_pagina, col_key, col_description)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"ℹ️ No hay datos suficientes o válidos para graficar '{col_description}'.")
                except Exception as e_plot:
                    st.error(f"❌ Error al graficar '{col_description}': {e_plot}")
                    print(f"ERROR 1_Abarrotes.py - plot_question_satisfaction para '{col_key}': {e_plot}")
                
                st.markdown("</div>", unsafe_allow_html=True)

            col_index += 1

    # --- Análisis de Comedores con Insatisfacción ---
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%); border-radius: 10px; margin: 2rem 0;">
        <h2 style="color: white; margin: 0; font-size: 2rem;">⚠️ Comedores con Insatisfacción</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">Análisis de comedores que reportaron problemas</p>
    </div>
    """, unsafe_allow_html=True)

    # Verificar columnas necesarias
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
            # Crear dataframe para análisis
            analisis_df = filtered_df_pagina[[id_comedor_col] + satisfaction_numeric_cols].copy()
            for col in satisfaction_numeric_cols:
                analisis_df[col] = pd.to_numeric(analisis_df[col], errors='coerce')

            # Identificar filas con insatisfacción
            insatisfaccion_mask = (analisis_df[satisfaction_numeric_cols] <= 2).any(axis=1)

            if not insatisfaccion_mask.any():
                st.success("✅ No se encontraron reportes de insatisfacción (puntaje <= 2) para Abarrotes con los datos actuales.")
            else:
                insatisfechos_df = analisis_df[insatisfaccion_mask]
                print(f"DEBUG 1_Abarrotes.py: {len(insatisfechos_df)} filas con al menos una insatisfacción encontrada.")

                # Agrupar por comedor y contar
                conteo_comedores = insatisfechos_df[id_comedor_col].value_counts().reset_index()
                conteo_comedores.columns = ['Comedor', 'Número de Reportes con Insatisfacción']

                st.write("📊 **Comedores con al menos un reporte de insatisfacción (puntaje <= 2) en Abarrotes:**")
                
                # Mostrar tabla con estilo
                st.markdown("""
                <style>
                .dataframe {
                    border: 1px solid #E1E8ED;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                </style>
                """, unsafe_allow_html=True)
                
                st.dataframe(
                    conteo_comedores.sort_values('Número de Reportes con Insatisfacción', ascending=False), 
                    hide_index=True, 
                    use_container_width=True
                )

        except Exception as e_insat:
            st.error(f"❌ Error analizando comedores insatisfechos: {e_insat}")
            print(f"ERROR 1_Abarrotes.py - Análisis Insatisfacción: {e_insat}")

    # --- Conclusiones y recomendaciones ---
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%); border-radius: 10px; margin: 2rem 0;">
        <h2 style="color: white; margin: 0; font-size: 2rem;">📝 Conclusiones y Recomendaciones</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">Insights basados en datos</p>
    </div>
    """, unsafe_allow_html=True)
    
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

            # Mostrar conclusiones con estilo
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div style="padding: 1.5rem; background: linear-gradient(45deg, #00E676, #4CAF50); border-radius: 10px; text-align: center; margin-bottom: 1rem;">
                    <h3 style="color: white; margin: 0;">🏆 MEJOR ASPECTO</h3>
                    <h4 style="color: white; margin: 0.5rem 0;">{max_desc}</h4>
                    <h2 style="color: white; margin: 0; font-size: 2.5rem;">{max_score:.2f}/5</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="padding: 1.5rem; background: linear-gradient(45deg, #FF6B6B, #FF8E53); border-radius: 10px; text-align: center; margin-bottom: 1rem;">
                    <h3 style="color: white; margin: 0;">🎯 NECESITA MEJORA</h3>
                    <h4 style="color: white; margin: 0.5rem 0;">{min_desc}</h4>
                    <h2 style="color: white; margin: 0; font-size: 2.5rem;">{min_score:.2f}/5</h2>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="padding: 1.5rem; background: rgba(102, 126, 234, 0.1); border-left: 4px solid #667eea; border-radius: 5px; margin: 1rem 0;">
                <h4 style="color: #667eea; margin: 0 0 1rem 0;">💡 Recomendaciones Estratégicas:</h4>
                <ul style="color: #2E3440; margin: 0;">
                    <li><strong>Prioridad Alta:</strong> Centrar esfuerzos de mejora en "{min_desc}"</li>
                    <li><strong>Mantener:</strong> Continuar con las buenas prácticas en "{max_desc}"</li>
                    <li><strong>Seguimiento:</strong> Realizar monitoreo continuo para identificar tendencias</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ No hay datos numéricos de satisfacción suficientes para generar conclusiones automáticas.")
    except Exception as e_conclu:
        st.error(f"❌ Error generando conclusiones: {e_conclu}")
        print(f"ERROR 1_Abarrotes.py - Conclusiones: {e_conclu}")

# --- Footer con estilo ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-top: 2rem;">
    <p style="color: white; margin: 0; font-size: 1.1rem;">
        📊 Dashboard de Análisis de la Encuesta de Satisfacción | Sección: Abarrotes
    </p>
    <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 0.9rem;">
        Desarrollado con ❤️ para mejorar la calidad del servicio
    </p>
</div>
""", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data, get_filtered_data # Asegúrate que estas funciones existan en data_loader.py
from utils.data_processing import ( # Asegúrate que estas funciones existan en data_processing.py
    plot_question_satisfaction,
    # create_wordcloud, # Descomenta si usas wordcloud aquí
    COL_DESCRIPTIONS
)

# Función modificada para convertir gráficos a barras horizontales
def make_horizontal_chart(fig, title_with_icon=None):
    """
    Convierte cualquier gráfico de barras verticales a horizontales y aplica fondo blanco
    """
    if fig is None:
        return None
    
    try:
        # Intercambiar x e y para hacer horizontal
        for trace in fig.data:
            if hasattr(trace, 'x') and hasattr(trace, 'y'):
                # Intercambiar valores
                temp_x = trace.x
                trace.x = trace.y
                trace.y = temp_x
                
                # Cambiar orientación
                if hasattr(trace, 'orientation'):
                    trace.orientation = 'h'
        
        # Actualizar layout para fondo blanco y ajustar ejes
        layout_updates = {
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'xaxis_title': "Número de Respuestas",
            'yaxis_title': "Categorías de Respuesta",
            'yaxis': {'categoryorder': 'total ascending'}  # Ordenar por valores
        }
        
        # Agregar título con icono si se proporciona
        if title_with_icon:
            layout_updates['title'] = {
                'text': title_with_icon,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            }
        
        fig.update_layout(**layout_updates)
        
        return fig
        
    except Exception as e:
        print(f"Error convirtiendo a horizontal: {e}")
        return fig

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Abarrotes",
    page_icon="📦",
    layout="wide"
)

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
    st.error("1_Abarrotes.py: No se pudieron cargar los datos iniciales desde load_data().")
    st.stop()
# else: # No es necesario mostrar mensaje de éxito aquí de nuevo
    # st.success(f"Datos cargados para Abarrotes. Registros iniciales: {len(df_pagina)}")


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
                 st.sidebar.warning("Rango de fechas inválido.")
        except Exception as e_date_filter_ui:
            st.sidebar.error(f"Error en filtro de fecha: {e_date_filter_ui}")

# Filtro por ubicación
if 'comuna' in df_pagina.columns:
    all_comunas = ["Todas"] + sorted([str(x) for x in df_pagina['comuna'].dropna().unique()])
    selected_comuna = st.sidebar.selectbox("🏘️ Comuna (Desactivado)", all_comunas, index=0, key='comuna_filter_abarrotes')
# else: st.sidebar.info("Columna 'comuna' no disponible.") # Evitar repetir mensajes

if 'barrio' in df_pagina.columns:
    all_barrios = ["Todos"] + sorted([str(x) for x in df_pagina['barrio'].dropna().unique()])
    selected_barrio = st.sidebar.selectbox("🏠 Barrio (Desactivado)", all_barrios, index=0, key='barrio_filter_abarrotes')
# else: st.sidebar.info("Columna 'barrio' no disponible.")

if 'nodo' in df_pagina.columns:
    all_nodos = ["Todos"] + sorted([str(x) for x in df_pagina['nodo'].dropna().unique()])
    selected_nodo = st.sidebar.selectbox("📍 Nodo (Desactivado)", all_nodos, index=0, key='nodo_filter_abarrotes')
# else: st.sidebar.info("Columna 'nodo' no disponible.")

# Información sobre filtros desactivados
st.sidebar.info("ℹ️ Los filtros están desactivados temporalmente para mostrar todos los datos disponibles.")

# --- NO APLICAR FILTROS - Usar el DataFrame completo ---
# En lugar de filtrar, simplemente usamos el DataFrame completo
filtered_df_pagina = df_pagina.copy()  # Usar todos los datos sin filtrar

# Mostrar métrica de encuestas para esta página
st.sidebar.metric("📊 Total de Encuestas (Abarrotes)", len(filtered_df_pagina))


# --- Contenido de la Página (si hay datos) ---
if filtered_df_pagina.empty:
    st.warning("No se encontraron registros para el análisis de Abarrotes.")
    print(f"WARN 1_Abarrotes.py: filtered_df_pagina está vacío.")
else:
    print(f"INFO 1_Abarrotes.py: Mostrando contenido con {len(filtered_df_pagina)} filas totales.")
    # --- Análisis de Abarrotes ---

    # Mapeo de las columnas de abarrotes con iconos (usar COL_DESCRIPTIONS si es posible)
    abarrotes_cols_map = {
        '9fecha_vencimiento': {
            'description': COL_DESCRIPTIONS.get('9fecha_vencimiento', 'Fecha de vencimiento'),
            'icon': '📅',
            'title_with_icon': '📅 Satisfacción con Fechas de Vencimiento'
        },
        '10tipo_empaque': {
            'description': COL_DESCRIPTIONS.get('10tipo_empaque', 'Tipo de empaque'),
            'icon': '📦',
            'title_with_icon': '📦 Satisfacción con Tipo de Empaque'
        },
        '11productos_iguales_lista_mercado': {
            'description': COL_DESCRIPTIONS.get('11productos_iguales_lista_mercado', 'Correspondencia con lista'),
            'icon': '📋',
            'title_with_icon': '📋 Correspondencia con Lista de Mercado'
        }
    }

    # Análisis de satisfacción por pregunta
    st.header("📊 Satisfacción con los Abarrotes")

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
            col_info = abarrotes_cols_map[col_key]
            col_description = col_info['description']
            title_with_icon = col_info['title_with_icon']
            
            # Seleccionar la columna correcta (priorizar _label)
            plot_col = col_key + '_label' if col_key + '_label' in filtered_df_pagina.columns and filtered_df_pagina[col_key + '_label'].notna().any() else col_key

            with cols_layout[col_index % num_cols]:
                print(f"DEBUG 1_Abarrotes.py: Intentando graficar '{plot_col}' para '{col_description}'")
                try:
                    # Usar la función original del archivo data_processing
                    fig = plot_question_satisfaction(filtered_df_pagina, col_key, col_description)
                    
                    if fig:
                        # Convertir a horizontal y aplicar fondo blanco con título con icono
                        fig_horizontal = make_horizontal_chart(fig, title_with_icon)
                        st.plotly_chart(fig_horizontal, use_container_width=True)
                    else:
                        # La función plot_question_satisfaction ya imprime si no hay datos
                        st.info(f"No hay datos suficientes o válidos para graficar '{col_description}'.")
                except Exception as e_plot:
                     st.error(f"Error al graficar '{col_description}': {e_plot}")
                     print(f"ERROR 1_Abarrotes.py - plot_question_satisfaction para '{col_key}': {e_plot}")

            col_index += 1


    # --- Análisis de Comedores con Insatisfacción ---
    st.header("⚠️ Comedores con Niveles de Insatisfacción Reportados")

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
                st.success("✅ No se encontraron reportes de insatisfacción (puntaje <= 2) para Abarrotes con los datos actuales.")
            else:
                insatisfechos_df = analisis_df[insatisfaccion_mask]
                print(f"DEBUG 1_Abarrotes.py: {len(insatisfechos_df)} filas con al menos una insatisfacción encontrada.")

                # Agrupar por comedor y contar cuántas veces aparece cada comedor insatisfecho
                conteo_comedores = insatisfechos_df[id_comedor_col].value_counts().reset_index()
                conteo_comedores.columns = ['🏪 Comedor', '📊 Número de Reportes con Insatisfacción']

                # Opcional: Detallar qué aspectos fueron insatisfactorios por comedor (más complejo)
                # Por ahora, mostrar la tabla de conteo
                st.write("🍽️ Comedores con al menos un reporte de insatisfacción (puntaje <= 2) en Abarrotes:")
                st.dataframe(conteo_comedores.sort_values('📊 Número de Reportes con Insatisfacción', ascending=False), hide_index=True, use_container_width=True)

                # Podrías añadir aquí conclusiones textuales como las tenías antes
                # ...

        except Exception as e_insat:
            st.error(f"Error analizando comedores insatisfechos: {e_insat}")
            print(f"ERROR 1_Abarrotes.py - Análisis Insatisfacción: {e_insat}")


    # --- Conclusiones y recomendaciones ---
    st.header("💡 Conclusiones y Recomendaciones (Abarrotes)")
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

             min_desc = abarrotes_cols_map.get(min_aspect_col, {}).get('description', min_aspect_col)
             max_desc = abarrotes_cols_map.get(max_aspect_col, {}).get('description', max_aspect_col)
             min_icon = abarrotes_cols_map.get(min_aspect_col, {}).get('icon', '📊')
             max_icon = abarrotes_cols_map.get(max_aspect_col, {}).get('icon', '📊')

             st.markdown(f"""
             📈 **Basado en el análisis de los datos:**

             - 🏆 El aspecto con **mayor satisfacción** es "{max_icon} {max_desc}" con un puntaje promedio de **{max_score:.2f}/5**.
             - ⚠️ El aspecto con **menor satisfacción** es "{min_icon} {min_desc}" con un puntaje promedio de **{min_score:.2f}/5**.

             **🎯 Recomendaciones:**
             - 🔧 Centrar esfuerzos de mejora en "{min_icon} {min_desc}".
             - ✅ Mantener las buenas prácticas relacionadas con "{max_icon} {max_desc}".
             - 📊 Realizar seguimiento continuo de la satisfacción para identificar tendencias.
             """)
        else:
             st.info("ℹ️ No hay datos numéricos de satisfacción suficientes para generar conclusiones automáticas.")
    except Exception as e_conclu:
        st.error(f"Error generando conclusiones: {e_conclu}")
        print(f"ERROR 1_Abarrotes.py - Conclusiones: {e_conclu}")


# --- Footer ---
st.markdown("---")
st.markdown("📊 Dashboard de Análisis de la Encuesta de Satisfacción | 📦 Sección: Abarrotes")
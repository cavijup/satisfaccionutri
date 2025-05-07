import streamlit as st
import pandas as pd
import plotly.express as px
# Eliminar 'get_filtered_data' de la importación
from utils.data_loader import load_data
from utils.data_processing import (
    plot_question_satisfaction,
    # create_wordcloud, # Descomenta si usas wordcloud aquí
    COL_DESCRIPTIONS
)

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
incluyendo fechas de vencimiento, tipo de empaque y correspondencia con la lista de mercado,
basado en **todos los datos recolectados**.
""")

# --- Carga de Datos ---
# Cargar los datos originales (usará caché si Home.py ya lo hizo)
# @st.cache_data(show_spinner="Cargando datos...") # No cachear aquí si Home.py ya lo hace
def get_data():
    df_page = load_data()
    return df_page

df = get_data() # Usar 'df' directamente

if df is None or df.empty:
    st.error("1_Abarrotes.py: No se pudieron cargar los datos iniciales desde load_data().")
    st.stop()
# else: # Mensaje de éxito ya se muestra en Home.py
    # st.success(f"Datos cargados para Abarrotes. Registros iniciales: {len(df)}")


# --- Barra Lateral (Solo navegación y métrica total) ---
st.sidebar.title("Navegación")
# st.sidebar.info("...") # Puedes añadir información aquí si quieres
st.sidebar.metric("Total de encuestas analizadas", len(df)) # Mostrar total de registros

# --- Aplicar Filtros (SECCIÓN ELIMINADA) ---
# Ya no necesitamos llamar a get_filtered_data, usaremos 'df' directamente.
# filtered_df_pagina = df # Asignar el dataframe completo

# --- Contenido de la Página (Siempre se muestra) ---
print(f"INFO 1_Abarrotes.py: Mostrando contenido con {len(df)} filas (sin filtros).")

# --- Análisis de Abarrotes ---

# Mapeo de las columnas de abarrotes
abarrotes_cols_map = {
    '9fecha_vencimiento': COL_DESCRIPTIONS.get('9fecha_vencimiento', 'Fecha de vencimiento'),
    '10tipo_empaque': COL_DESCRIPTIONS.get('10tipo_empaque', 'Tipo de empaque'),
    '11productos_iguales_lista_mercado': COL_DESCRIPTIONS.get('11productos_iguales_lista_mercado', 'Correspondencia con lista')
}

# Análisis de satisfacción por pregunta
st.header("Satisfacción con los Abarrotes (Global)")

# Comprobar si existen las columnas de abarrotes y tienen datos válidos
valid_display_cols = []
for col_key in abarrotes_cols_map.keys():
    label_col = col_key + '_label'
    if label_col in df.columns and df[label_col].notna().any():
        valid_display_cols.append(col_key)
    elif col_key in df.columns and pd.api.types.is_numeric_dtype(df[col_key].dtype) and df[col_key].notna().any():
        valid_display_cols.append(col_key)
        print(f"WARN 1_Abarrotes.py: Usando columna numérica '{col_key}' porque '{label_col}' falta o está vacía.")

if not valid_display_cols:
    st.warning("No se encontraron datos de satisfacción válidos para Abarrotes.")
else:
    # Crear columnas para layout
    num_cols = 2
    cols_layout = st.columns(num_cols)
    col_index = 0

    for col_key in valid_display_cols:
        col_description = abarrotes_cols_map[col_key]
        plot_col = col_key + '_label' if col_key + '_label' in df.columns and df[col_key + '_label'].notna().any() else col_key

        with cols_layout[col_index % num_cols]:
            print(f"DEBUG 1_Abarrotes.py: Intentando graficar '{plot_col}' para '{col_description}'")
            try:
                # Usar el DataFrame completo 'df'
                fig = plot_question_satisfaction(df, col_key, col_description)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No hay datos suficientes o válidos para graficar '{col_description}'.")
            except Exception as e_plot:
                 st.error(f"Error al graficar '{col_description}': {e_plot}")
                 print(f"ERROR 1_Abarrotes.py - plot_question_satisfaction para '{col_key}': {e_plot}")
        col_index += 1

# --- Análisis de Comedores con Insatisfacción ---
st.header("Comedores con Niveles de Insatisfacción Reportados (Global)")

# Verificar columnas necesarias
id_comedor_candidates = ['nombre_comedor', 'comedor', 'id_comedor', 'nombre del comedor']
id_comedor_col = next((col for col in id_comedor_candidates if col in df.columns), None)
satisfaction_numeric_cols = [col for col in abarrotes_cols_map.keys() if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]

if not satisfaction_numeric_cols:
    st.info("No hay columnas numéricas de satisfacción de abarrotes para analizar.")
elif not id_comedor_col:
    st.warning("No se encontró columna para identificar el comedor.")
else:
    print(f"DEBUG 1_Abarrotes.py: Analizando insatisfacción (global). ID Comedor: '{id_comedor_col}', Columnas numéricas: {satisfaction_numeric_cols}")
    try:
        analisis_df = df[[id_comedor_col] + satisfaction_numeric_cols].copy()
        for col in satisfaction_numeric_cols:
            analisis_df[col] = pd.to_numeric(analisis_df[col], errors='coerce')

        insatisfaccion_mask = (analisis_df[satisfaction_numeric_cols] <= 2).any(axis=1)

        if not insatisfaccion_mask.any():
            st.success("No se encontraron reportes de insatisfacción (puntaje <= 2) para Abarrotes en el total de datos.")
        else:
            insatisfechos_df = analisis_df[insatisfaccion_mask]
            print(f"DEBUG 1_Abarrotes.py: {len(insatisfechos_df)} filas totales con insatisfacción.")

            conteo_comedores = insatisfechos_df[id_comedor_col].value_counts().reset_index()
            conteo_comedores.columns = ['Comedor', 'Número de Reportes con Insatisfacción']

            st.write("Comedores con al menos un reporte de insatisfacción (puntaje <= 2) en Abarrotes (Global):")
            st.dataframe(conteo_comedores.sort_values('Número de Reportes con Insatisfacción', ascending=False), hide_index=True, use_container_width=True)

    except Exception as e_insat:
        st.error(f"Error analizando comedores insatisfechos: {e_insat}")
        print(f"ERROR 1_Abarrotes.py - Análisis Insatisfacción: {e_insat}")


# --- Conclusiones y recomendaciones ---
st.header("Conclusiones y Recomendaciones (Global - Abarrotes)")
try:
    satisfaction_means = {}
    # Usar el df completo
    valid_cols_for_mean = [col for col in abarrotes_cols_map.keys() if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]

    if valid_cols_for_mean:
         for col in valid_cols_for_mean:
             numeric_data = pd.to_numeric(df[col], errors='coerce')
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
         Basado en el análisis de **todos** los datos:

         - El aspecto con **mayor satisfacción** global es "{max_desc}" ({max_score:.2f}/5).
         - El aspecto con **menor satisfacción** global es "{min_desc}" ({min_score:.2f}/5).

         **Recomendaciones Generales:**
         - Investigar las causas de la menor satisfacción en "{min_desc}".
         - Reforzar las prácticas que llevan a la alta satisfacción en "{max_desc}".
         """)
    else:
         st.info("No hay datos numéricos de satisfacción suficientes para generar conclusiones.")
except Exception as e_conclu:
    st.error(f"Error generando conclusiones: {e_conclu}")
    print(f"ERROR 1_Abarrotes.py - Conclusiones: {e_conclu}")

# --- Footer ---
st.markdown("---")
st.markdown("Dashboard de Análisis de la Encuesta de Satisfacción | Sección: Abarrotes")
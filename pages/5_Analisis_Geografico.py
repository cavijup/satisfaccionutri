import streamlit as st
import pandas as pd
import plotly.express as px
# Eliminar 'get_filtered_data' de la importación
from utils.data_loader import load_data
from utils.data_processing import (
    get_satisfaction_columns,
    # CATEGORIES, # Importar CATEGORIES si se usa aquí, o definirlo localmente
    plot_geographic_satisfaction, # Importar la función para graficar
    COL_DESCRIPTIONS # Importar descripciones
)

# Configuración de la página
st.set_page_config(
    page_title="Análisis Geográfico",
    page_icon="🗺️",
    layout="wide"
)

# Título y descripción
st.title("Análisis Geográfico de Satisfacción")
st.markdown("""
Esta sección presenta el análisis comparativo de la satisfacción promedio general por ubicación geográfica,
basado en **todos los datos recolectados**.
""")

# --- Carga de Datos ---
# @st.cache_data(show_spinner="Cargando datos...") # No cachear aquí si Home.py ya lo hace
def get_data():
    df_page = load_data()
    return df_page

df = get_data() # Usar 'df' directamente

if df is None or df.empty:
    st.error("5_Analisis_Geografico.py: No se pudieron cargar los datos iniciales desde load_data().")
    st.stop()

# --- Barra Lateral (Solo navegación y métrica total) ---
st.sidebar.title("Navegación")
st.sidebar.metric("Total de encuestas analizadas", len(df)) # Mostrar total de registros

# --- SECCIÓN DE FILTROS ELIMINADA ---
# Ya no se definen filtros específicos aquí, usamos el df completo

# --- Contenido de la Página (Siempre usa 'df') ---
print(f"INFO 5_Analisis_Geografico.py: Mostrando contenido con {len(df)} filas (sin filtros).")

# Verificar variables geográficas disponibles
geo_vars = []
if 'comuna' in df.columns and df['comuna'].notna().any(): # Verificar que la columna tenga datos
    geo_vars.append('comuna')
if 'barrio' in df.columns and df['barrio'].notna().any():
    geo_vars.append('barrio')
if 'nodo' in df.columns and df['nodo'].notna().any():
    geo_vars.append('nodo')
# 'nicho' no estaba en tu archivo original, lo omito a menos que confirmes que existe

if not geo_vars:
    st.warning("No se encontraron variables geográficas con datos (comuna, barrio, nodo) para el análisis.")
    st.stop()

# Selección de variable geográfica para analizar
# Usar radio buttons o selectbox para que el usuario elija por qué variable agrupar
selected_geo_var = st.selectbox(
    "Seleccione la variable geográfica para el análisis:",
    options=geo_vars,
    format_func=lambda x: x.capitalize() # Mostrar nombres capitalizados
)

st.header(f"Satisfacción Promedio General por {selected_geo_var.capitalize()}")

# Graficar usando la función importada
# La función plot_geographic_satisfaction calcula el promedio general
try:
    geo_fig = plot_geographic_satisfaction(df.copy(), selected_geo_var) # Pasar una copia por si la función modifica el df
    if geo_fig:
        st.plotly_chart(geo_fig, use_container_width=True)
    else:
        st.info(f"No hay suficientes datos para generar el gráfico por '{selected_geo_var}'.")
except Exception as e_geo_plot:
    st.error(f"Error al generar gráfico geográfico: {e_geo_plot}")
    print(f"ERROR 5_Analisis_Geografico.py - plot_geographic_satisfaction: {e_geo_plot}")


# --- Análisis de Mejor y Peor Ubicación (Basado en Satisfacción Promedio General) ---
st.header(f"Análisis Detallado por {selected_geo_var.capitalize()}")

# Necesitamos calcular el promedio general por ubicación aquí o usar una función que lo devuelva
satisfaction_cols = get_satisfaction_columns(df)
if not satisfaction_cols:
    st.warning("No se encontraron columnas de satisfacción válidas para el análisis detallado.")
else:
    # Calcular promedio por fila
    df_analysis = df.copy() # Trabajar sobre una copia
    # Asegurarse que las columnas de satisfacción son numéricas
    for col in satisfaction_cols:
        df_analysis[col] = pd.to_numeric(df_analysis[col], errors='coerce')
    df_analysis['satisfaccion_promedio_general'] = df_analysis[satisfaction_cols].mean(axis=1, skipna=True)

    # Agrupar por la variable geográfica seleccionada
    if selected_geo_var in df_analysis.columns and df_analysis[selected_geo_var].notna().any():
        # Agrupar por string para evitar problemas con tipos mixtos
        geo_stats = df_analysis.groupby(df_analysis[selected_geo_var].astype(str))['satisfaccion_promedio_general'].agg(['mean', 'count']).reset_index()
        geo_stats.columns = [selected_geo_var, 'Satisfacción Promedio', 'Cantidad Encuestas']
        geo_stats = geo_stats.dropna(subset=['Satisfacción Promedio']) # Eliminar grupos sin promedio calculable
        geo_stats = geo_stats.sort_values('Satisfacción Promedio', ascending=False)

        if len(geo_stats) > 0:
            best_location = geo_stats.iloc[0]
            worst_location = geo_stats.iloc[-1]

            st.markdown(f"""
            Análisis general de satisfacción por **{selected_geo_var.capitalize()}**:

            - **Mejor Desempeño:** {best_location[selected_geo_var]} (Promedio: {best_location['Satisfacción Promedio']:.2f}/5, Encuestas: {int(best_location['Cantidad Encuestas'])})
            - **Menor Desempeño:** {worst_location[selected_geo_var]} (Promedio: {worst_location['Satisfacción Promedio']:.2f}/5, Encuestas: {int(worst_location['Cantidad Encuestas'])})
            """)

            # --- Análisis Detallado de Aspectos en Peor Ubicación ---
            st.subheader(f"Aspectos con Menor Satisfacción en: {worst_location[selected_geo_var]}")

            # Filtrar el DataFrame original por la peor ubicación
            df_worst_loc = df_analysis[df_analysis[selected_geo_var].astype(str) == worst_location[selected_geo_var]].copy()

            # Calcular el promedio de cada columna de satisfacción SOLO para esa ubicación
            aspect_means_worst = {}
            for col in satisfaction_cols:
                 # Asegurar que la columna es numérica
                 numeric_col_worst = pd.to_numeric(df_worst_loc[col], errors='coerce')
                 if numeric_col_worst.notna().any():
                      aspect_means_worst[col] = numeric_col_worst.mean()

            if aspect_means_worst:
                 # Ordenar aspectos por satisfacción (menor a mayor)
                 sorted_aspects_worst = sorted(aspect_means_worst.items(), key=lambda item: item[1])

                 st.markdown("Principales áreas de mejora identificadas:")
                 for col_key, score in sorted_aspects_worst[:3]: # Mostrar los 3 peores
                      aspect_desc = COL_DESCRIPTIONS.get(col_key, col_key) # Obtener descripción
                      st.markdown(f"- **{aspect_desc}:** {score:.2f}/5")

                 st.markdown(f"""
                 **Recomendaciones Específicas para {worst_location[selected_geo_var]}:**
                 - Priorizar acciones de mejora en los aspectos listados arriba.
                 - Realizar seguimiento focalizado en esta ubicación.
                 - Comparar prácticas con {best_location[selected_geo_var]} para identificar oportunidades.
                 """)
            else:
                 st.info(f"No hay suficientes datos para detallar aspectos específicos en {worst_location[selected_geo_var]}.")

        else:
            st.info(f"No hay suficientes datos agrupados por '{selected_geo_var}' para realizar el análisis comparativo.")
    else:
        st.info(f"La columna '{selected_geo_var}' no tiene datos válidos para agrupar.")

# --- Footer ---
st.markdown("---")
st.markdown("Dashboard de Análisis de la Encuesta de Satisfacción | Sección: Análisis Geográfico")
import streamlit as st
import pandas as pd
# Eliminar 'get_filtered_data' de la importación
from utils.data_loader import load_data
from utils.data_processing import (
    plot_satisfaction_by_category,
    identify_problem_areas,
    get_satisfaction_columns
)
import time

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Encuesta Satisfacción",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título y descripción
st.title("Dashboard de Análisis - Encuesta de Satisfacción de Entrega de Mercados")
st.markdown("""
Este dashboard presenta el análisis de **todas** las encuestas de satisfacción recopiladas
del proceso de entrega de mercados a comedores comunitarios, permitiendo identificar
áreas de mejora y fortalezas generales del programa.

Navegue entre las pestañas de la barra lateral para explorar distintos aspectos de los datos.
""")

# --- Carga de Datos ---
@st.cache_data(show_spinner="Cargando datos de Google Sheets...") # Añadir spinner aquí
def get_data():
    df = load_data()
    return df

df = get_data() # Usar 'df' directamente como nombre del DataFrame principal

if df is None or df.empty:
    st.error("Home.py: No se pudieron cargar los datos iniciales desde load_data(). La aplicación no puede continuar.")
    st.stop()
else:
    st.success(f"Datos cargados. Total de registros: {len(df)}")

# --- Barra Lateral (Sin Filtros) ---
st.sidebar.title("Navegación")
st.sidebar.info("Seleccione una sección para ver el análisis detallado.")
st.sidebar.metric("Total de encuestas analizadas", len(df)) # Mostrar total de registros

# Botón para refrescar datos
if st.sidebar.button("Refrescar Datos"):
    st.cache_data.clear() # Limpiar caché de load_data
    st.rerun()

# --- Contenido Principal (Siempre se muestra ya que no hay filtros) ---

print(f"INFO Home.py: Mostrando contenido principal con {len(df)} filas (sin filtros).")

# --- Métricas Generales ---
st.header("Métricas Generales (Globales)")

# Calcular métricas usando el df completo
satisfaction_cols = get_satisfaction_columns(df) # Usar el df completo
overall_satisfaction = None
plazos_cumplidos = None
proceso_sencillo = None

if satisfaction_cols:
    all_means = []
    for col in satisfaction_cols:
         numeric_col = pd.to_numeric(df[col], errors='coerce')
         if numeric_col.notna().any():
              all_means.append(numeric_col.mean())
    if all_means:
         overall_satisfaction = sum(all_means) / len(all_means)

if '29plazos_entrega_mercados' in df.columns:
    plazos_series = df['29plazos_entrega_mercados'].dropna().astype(str).str.strip().str.lower()
    if len(plazos_series) > 0:
        plazos_cumplidos = (plazos_series == 'sí').mean() * 100

if '31pasos_recepcion_mercado' in df.columns:
    proceso_series = df['31pasos_recepcion_mercado'].dropna().astype(str).str.strip().str.lower()
    if len(proceso_series) > 0:
        proceso_sencillo = (proceso_series == 'sencillo').mean() * 100

# Mostrar métricas en columnas
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Satisfacción General", f"{overall_satisfaction:.2f}/5" if overall_satisfaction is not None else "N/A")
with col2:
    st.metric("Cumplimiento de Plazos", f"{plazos_cumplidos:.1f}%" if plazos_cumplidos is not None else "N/A")
with col3:
    st.metric("Proceso Sencillo", f"{proceso_sencillo:.1f}%" if proceso_sencillo is not None else "N/A")

# --- Áreas problemáticas ---
st.subheader("Aspectos con Menor Satisfacción (Global)")
try:
    problem_areas = identify_problem_areas(df) # Usar el df completo
    if not problem_areas.empty:
        problem_areas['Satisfacción Media'] = problem_areas['Satisfacción Media'].map('{:.2f}'.format)
        st.dataframe(problem_areas, use_container_width=True, hide_index=True)
    else:
        st.info("No se pudieron calcular las áreas problemáticas.")
except Exception as e_problem:
    st.error(f"Error al identificar áreas problemáticas: {e_problem}")
    print(f"ERROR Home.py - identify_problem_areas: {e_problem}")


# --- Gráficos principales ---
st.header("Satisfacción Promedio por Categoría (Global)")
try:
    satisfaction_fig = plot_satisfaction_by_category(df) # Usar el df completo
    if satisfaction_fig:
        st.plotly_chart(satisfaction_fig, use_container_width=True)
    # else: # La función ahora devuelve una figura vacía si no hay datos
    #    st.info("No se pudo crear el gráfico de satisfacción por categoría.")
except Exception as e_plot_cat:
    st.error(f"Error al generar gráfico por categoría: {e_plot_cat}")
    print(f"ERROR Home.py - plot_satisfaction_by_category: {e_plot_cat}")


# --- Secciones fijas ---
st.header("Navegación por el Dashboard")
st.markdown("""
Utilice la barra lateral izquierda para navegar a las distintas secciones del dashboard:

1.  **Abarrotes**: Análisis detallado de la satisfacción con abarrotes.
2.  **Cárnicos y Huevos**: Análisis de la satisfacción con carnes y huevos.
3.  **Frutas y Verduras**: Análisis de la satisfacción con frutas, verduras, hortalizas y tubérculos.
4.  **Proceso de Entrega**: Evaluación del proceso de entrega, tiempos y atención.
5.  **Análisis Geográfico**: Comparativa de satisfacción por ubicación geográfica.

Cada sección contiene gráficos interactivos y análisis detallados **sobre el total de los datos**.
""")

# Instrucciones de uso
with st.expander("Instrucciones de Uso"):
    st.markdown("""
    ## Cómo utilizar este dashboard

    1.  **Navegación**: Haga clic en las opciones de la barra lateral para explorar análisis detallados por categoría o geografía.
    2.  **Métricas Generales**: Vea un resumen de la satisfacción general y otros indicadores clave basados en todos los datos.
    3.  **Refrescar Datos**: Si cree que los datos en Google Sheets han cambiado recientemente, use el botón "Refrescar Datos" para forzar una recarga desde la fuente (esto puede tomar unos segundos).

    Para obtener más detalles sobre cualquier gráfico, puede pasar el cursor sobre los elementos visuales.
    """)

# Footer
st.markdown("---")
st.markdown(f"Dashboard de Análisis de Encuestas - {time.strftime('%Y-%m-%d %H:%M:%S')}")
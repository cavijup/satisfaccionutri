import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_filtered_data
from utils.data_processing import (
    plot_satisfaction_by_category,
    identify_problem_areas,
    get_satisfaction_columns
)

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
Este dashboard presenta el análisis de las encuestas de satisfacción del proceso de entrega de mercados
a comedores comunitarios, permitiendo identificar áreas de mejora y fortalezas del programa.

Utilice la barra lateral para aplicar filtros y navegue entre las pestañas para explorar distintos 
aspectos de los datos.
""")

# Cargar datos con indicador de progreso
with st.spinner('Cargando datos de Google Sheets...'):
    df = load_data()

if df.empty:
    st.error("No se pudieron cargar los datos. Verifica tus credenciales y la conexión a Google Sheets.")
    st.stop()

# Mostrar indicador de conexión exitosa
st.success(f"Datos cargados correctamente. Total de registros: {len(df)}")

# Sidebar para filtros
st.sidebar.title("Filtros")

# Filtro por fecha
if 'fecha' in df.columns:
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    valid_dates = df.dropna(subset=['fecha'])
    
    if not valid_dates.empty:
        min_date = valid_dates['fecha'].min().date()
        max_date = valid_dates['fecha'].max().date()
        
        date_range = st.sidebar.date_input(
            "Rango de fechas",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
    else:
        date_range = None
else:
    date_range = None

# Filtro por ubicación geográfica
if 'comuna' in df.columns:
    all_comunas = ["Todas"] + sorted([str(x) for x in df['comuna'].unique() if pd.notna(x)])
    selected_comuna = st.sidebar.selectbox("Comuna", all_comunas)
else:
    selected_comuna = None

if 'barrio' in df.columns:
    all_barrios = ["Todos"] + sorted([str(x) for x in df['barrio'].unique() if pd.notna(x)])
    selected_barrio = st.sidebar.selectbox("Barrio", all_barrios)
else:
    selected_barrio = None

if 'nodo' in df.columns:
    all_nodos = ["Todos"] + sorted([str(x) for x in df['nodo'].unique() if pd.notna(x)])
    selected_nodo = st.sidebar.selectbox("Nodo", all_nodos)
else:
    selected_nodo = None

# Aplicar filtros
filtered_df = get_filtered_data(df, date_range, selected_comuna, selected_barrio, selected_nodo)

# Mostrar número de encuestas filtradas
st.sidebar.metric("Total de encuestas filtradas", len(filtered_df))

# Botón para refrescar datos
if st.sidebar.button("Refrescar Datos"):
    # Limpiar caché y recargar
    st.cache_data.clear()
    st.experimental_rerun()

# Métricas generales
st.header("Métricas Generales")

# Calcular métricas
satisfaction_cols = get_satisfaction_columns(filtered_df)

# Calcular satisfacción general si hay columnas válidas
if satisfaction_cols:
    overall_satisfaction = filtered_df[satisfaction_cols].mean().mean()
else:
    overall_satisfaction = None

# Calcular plazos cumplidos si existe la columna
if '29plazos_entrega_mercados' in filtered_df.columns:
    plazos_cumplidos = (filtered_df['29plazos_entrega_mercados'].astype(str).str.lower() == 'sí').mean() * 100
else:
    plazos_cumplidos = None

# Calcular proceso sencillo si existe la columna
if '31pasos_recepcion_mercado' in filtered_df.columns:
    proceso_sencillo = (filtered_df['31pasos_recepcion_mercado'].astype(str).str.lower() == 'sencillo').mean() * 100
else:
    proceso_sencillo = None

# Mostrar métricas en 3 columnas
col1, col2, col3 = st.columns(3)
with col1:
    if overall_satisfaction is not None:
        st.metric("Satisfacción General", f"{overall_satisfaction:.2f}/5")
    else:
        st.metric("Satisfacción General", "No disponible")
with col2:
    if plazos_cumplidos is not None:
        st.metric("Cumplimiento de Plazos", f"{plazos_cumplidos:.1f}%")
    else:
        st.metric("Cumplimiento de Plazos", "No disponible")
with col3:
    if proceso_sencillo is not None:
        st.metric("Proceso Sencillo", f"{proceso_sencillo:.1f}%")
    else:
        st.metric("Proceso Sencillo", "No disponible")

# Áreas problemáticas
st.subheader("Aspectos con Menor Satisfacción")
problem_areas = identify_problem_areas(filtered_df)
if not problem_areas.empty:
    st.dataframe(problem_areas, use_container_width=True)
else:
    st.info("No hay suficientes datos para identificar áreas problemáticas.")

# Gráficos principales
st.header("Análisis por Categoría")

# Gráfico de satisfacción por categoría
satisfaction_fig = plot_satisfaction_by_category(filtered_df)
if satisfaction_fig:
    st.plotly_chart(satisfaction_fig, use_container_width=True)
else:
    st.info("No hay suficientes datos para crear el gráfico de satisfacción por categoría.")

# Información sobre navegación
st.header("Navegación por el Dashboard")
st.markdown("""
Utilice la barra lateral izquierda para navegar a las distintas secciones del dashboard:

1. **Abarrotes**: Análisis detallado de la satisfacción con abarrotes (granos, aceite, arroz, etc.)
2. **Cárnicos y Huevos**: Análisis de la satisfacción con carnes y huevos
3. **Frutas y Verduras**: Análisis de la satisfacción con frutas, verduras, hortalizas y tubérculos
4. **Proceso de Entrega**: Evaluación del proceso de entrega, tiempos y atención
5. **Análisis Geográfico**: Comparativa de satisfacción por ubicación geográfica

Cada sección contiene gráficos interactivos y análisis detallados de los aspectos evaluados en la encuesta.
""")

# Instrucciones de uso
with st.expander("Instrucciones de Uso"):
    st.markdown("""
    ## Cómo utilizar este dashboard
    
    1. **Filtros**: Use los controles en la barra lateral para filtrar por fecha, comuna, barrio y nodo.
    2. **Métricas Generales**: Vea un resumen de la satisfacción general y otros indicadores clave.
    3. **Análisis por Categoría**: Explore las distintas páginas para ver el análisis detallado de cada categoría.
    4. **Análisis Geográfico**: Compare la satisfacción entre diferentes regiones.
    5. **Refrescar Datos**: Utilice el botón "Refrescar Datos" para obtener la información más reciente.
    
    Para obtener más detalles sobre cualquier gráfico, puede pasar el cursor sobre los elementos visuales.
    """)

# Footer
st.markdown("---")
st.markdown("Dashboard creado para el análisis de la encuesta de satisfacción del proceso de entrega de mercados.")
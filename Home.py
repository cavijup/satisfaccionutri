import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_filtered_data # Asegúrate que estas funciones existan en data_loader.py
from utils.data_processing import ( # Asegúrate que estas funciones existan en data_processing.py
    plot_satisfaction_by_category,
    identify_problem_areas,
    get_satisfaction_columns
)
import time # Para simular carga si es necesario

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

# --- Carga de Datos ---
# Usar cache para la carga inicial
# @st.cache_data(show_spinner="Cargando datos iniciales...") # Se aplica dentro de load_data
def get_data():
    df = load_data()
    return df

df_original = get_data()

if df_original is None or df_original.empty:
    st.error("Home.py: No se pudieron cargar los datos iniciales desde load_data(). La aplicación no puede continuar.")
    # st.info("Revisar logs para detalles del error en load_data(). Puede ser un problema de credenciales, permisos en Google Sheets o conexión.")
    # Puedes añadir un botón para reintentar si quieres
    # if st.button("Reintentar Carga de Datos"):
    #      st.cache_data.clear()
    #      st.rerun()
    st.stop() # Detener la ejecución si no hay datos
else:
    st.success(f"Datos cargados. Total de registros iniciales: {len(df_original)}")
    # st.sidebar.success(f"Registros iniciales: {len(df_original)}") # Mover a sidebar si prefieres

# --- Sidebar para Filtros ---
st.sidebar.title("Filtros")

# Inicializar variables de filtro
date_range_selected = None
selected_comuna = "Todas" # Valor por defecto
selected_barrio = "Todos" # Valor por defecto
selected_nodo = "Todos"   # Valor por defecto

# Filtro por fecha (solo si la columna 'fecha' existe y tiene datos válidos)
if 'fecha' in df_original.columns and pd.api.types.is_datetime64_any_dtype(df_original['fecha']):
    valid_dates = df_original['fecha'].dropna()
    if not valid_dates.empty:
        try:
            min_date_dt = valid_dates.min()
            max_date_dt = valid_dates.max()
            # Asegurar que min_date no sea posterior a max_date
            if min_date_dt <= max_date_dt:
                default_start_date = min_date_dt.date()
                default_end_date = max_date_dt.date()

                date_range_selected = st.sidebar.date_input(
                    "Rango de fechas",
                    value=[default_start_date, default_end_date], # Usar 'value' para preselección
                    min_value=default_start_date,
                    max_value=default_end_date,
                    # key='date_filter_home' # Añadir key si hay múltiples filtros de fecha en la app
                )
            else:
                 st.sidebar.warning("El rango de fechas en los datos es inválido (fecha mínima posterior a máxima).")
        except Exception as e_date_filter_ui:
            st.sidebar.error(f"Error al configurar filtro de fecha: {e_date_filter_ui}")
    else:
        st.sidebar.info("No hay fechas válidas en los datos para filtrar.")
else:
    st.sidebar.info("Columna 'fecha' no disponible o no es de tipo fecha.")


# Filtro por ubicación geográfica (solo si las columnas existen)
if 'comuna' in df_original.columns:
    # Obtener comunas únicas, convertir a string, ordenar y añadir "Todas"
    all_comunas = ["Todas"] + sorted([str(x) for x in df_original['comuna'].dropna().unique()])
    selected_comuna = st.sidebar.selectbox("Comuna", all_comunas, index=0) # Default a "Todas"
else:
    st.sidebar.info("Columna 'comuna' no disponible.")

if 'barrio' in df_original.columns:
    # Filtrar barrios basado en comuna seleccionada (opcional, más complejo)
    # O mostrar todos los barrios
    all_barrios = ["Todos"] + sorted([str(x) for x in df_original['barrio'].dropna().unique()])
    selected_barrio = st.sidebar.selectbox("Barrio", all_barrios, index=0) # Default a "Todos"
else:
    st.sidebar.info("Columna 'barrio' no disponible.")

if 'nodo' in df_original.columns:
    all_nodos = ["Todos"] + sorted([str(x) for x in df_original['nodo'].dropna().unique()])
    selected_nodo = st.sidebar.selectbox("Nodo", all_nodos, index=0) # Default a "Todos"
else:
    st.sidebar.info("Columna 'nodo' no disponible.")

# --- Aplicar Filtros y Mostrar Resultados ---
print(f"DEBUG Home.py: Antes de get_filtered_data. Filtros: Fecha={date_range_selected}, Comuna='{selected_comuna}', Barrio='{selected_barrio}', Nodo='{selected_nodo}'")
filtered_df = get_filtered_data(df_original.copy(), date_range_selected, selected_comuna, selected_barrio, selected_nodo)
print(f"DEBUG Home.py: Después de get_filtered_data. Número de filas en filtered_df: {len(filtered_df)}")

# Mostrar número de encuestas filtradas en la barra lateral
st.sidebar.metric("Total de encuestas filtradas", len(filtered_df))

# Botón para refrescar datos (limpia caché y re-ejecuta)
if st.sidebar.button("Refrescar Datos"):
    st.cache_data.clear() # Limpiar caché de load_data
    st.rerun()

# --- Contenido Principal (solo si hay datos filtrados) ---
if filtered_df.empty:
    st.warning(f"No se encontraron registros con los filtros seleccionados. Por favor, ajuste los filtros en la barra lateral.")
    # Mostrar un resumen de los filtros aplicados que resultaron en cero datos
    st.info(f"Filtros actuales: Fecha={date_range_selected}, Comuna='{selected_comuna}', Barrio='{selected_barrio}', Nodo='{selected_nodo}'")
    print(f"WARN Home.py: filtered_df está vacío después de aplicar filtros.")
else:
    print(f"INFO Home.py: Mostrando contenido principal con {len(filtered_df)} filas filtradas.")
    # --- Métricas Generales ---
    st.header("Métricas Generales")

    # Calcular métricas usando filtered_df
    satisfaction_cols = get_satisfaction_columns(filtered_df)
    overall_satisfaction = None
    plazos_cumplidos = None
    proceso_sencillo = None

    if satisfaction_cols:
        # Calcular promedio de promedios de columnas de satisfacción
        all_means = []
        for col in satisfaction_cols:
             # Asegurarse que la columna sea numérica antes de calcular mean
             numeric_col = pd.to_numeric(filtered_df[col], errors='coerce')
             if numeric_col.notna().any():
                  all_means.append(numeric_col.mean())
        if all_means:
             overall_satisfaction = sum(all_means) / len(all_means)

    if '29plazos_entrega_mercados' in filtered_df.columns:
        # Convertir a string, limpiar y comparar con 'Sí' (insensible a mayúsculas)
        plazos_series = filtered_df['29plazos_entrega_mercados'].dropna().astype(str).str.strip().str.lower()
        if len(plazos_series) > 0:
            plazos_cumplidos = (plazos_series == 'sí').mean() * 100

    if '31pasos_recepcion_mercado' in filtered_df.columns:
        proceso_series = filtered_df['31pasos_recepcion_mercado'].dropna().astype(str).str.strip().str.lower()
        if len(proceso_series) > 0:
            proceso_sencillo = (proceso_series == 'sencillo').mean() * 100

    # Mostrar métricas en columnas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Satisfacción General", f"{overall_satisfaction:.2f}/5" if overall_satisfaction is not None else "No disponible")
    with col2:
        st.metric("Cumplimiento de Plazos", f"{plazos_cumplidos:.1f}%" if plazos_cumplidos is not None else "No disponible")
    with col3:
        st.metric("Proceso Sencillo", f"{proceso_sencillo:.1f}%" if proceso_sencillo is not None else "No disponible")

    # --- Áreas problemáticas ---
    st.subheader("Aspectos con Menor Satisfacción")
    try:
        problem_areas = identify_problem_areas(filtered_df)
        if not problem_areas.empty:
            # Formatear la satisfacción media a 2 decimales
            problem_areas['Satisfacción Media'] = problem_areas['Satisfacción Media'].map('{:.2f}'.format)
            st.dataframe(problem_areas, use_container_width=True, hide_index=True)
        else:
            st.info("No hay suficientes datos (después de filtrar) para identificar áreas problemáticas.")
    except Exception as e_problem:
        st.error(f"Error al identificar áreas problemáticas: {e_problem}")
        print(f"ERROR Home.py - identify_problem_areas: {e_problem}")


    # --- Gráficos principales ---
    st.header("Satisfacción Promedio por Categoría")
    try:
        satisfaction_fig = plot_satisfaction_by_category(filtered_df)
        if satisfaction_fig:
            st.plotly_chart(satisfaction_fig, use_container_width=True)
        # La función plot_satisfaction_by_category ya maneja internamente si no hay datos
        # else:
        #    st.info("No hay suficientes datos (después de filtrar) para crear el gráfico de satisfacción por categoría.")
    except Exception as e_plot_cat:
        st.error(f"Error al generar gráfico por categoría: {e_plot_cat}")
        print(f"ERROR Home.py - plot_satisfaction_by_category: {e_plot_cat}")


# --- Secciones fijas (fuera del 'else' de filtered_df) ---
st.header("Navegación por el Dashboard")
st.markdown("""
Utilice la barra lateral izquierda para navegar a las distintas secciones del dashboard:

1.  **Abarrotes**: Análisis detallado de la satisfacción con abarrotes.
2.  **Cárnicos y Huevos**: Análisis de la satisfacción con carnes y huevos.
3.  **Frutas y Verduras**: Análisis de la satisfacción con frutas, verduras, hortalizas y tubérculos.
4.  **Proceso de Entrega**: Evaluación del proceso de entrega, tiempos y atención.
5.  **Análisis Geográfico**: Comparativa de satisfacción por ubicación geográfica.

Cada sección contiene gráficos interactivos y análisis detallados.
""")

# Instrucciones de uso
with st.expander("Instrucciones de Uso"):
    st.markdown("""
    ## Cómo utilizar este dashboard

    1.  **Filtros**: Use los controles en la barra lateral para filtrar por fecha, comuna, barrio y nodo. Los datos se actualizarán automáticamente.
    2.  **Métricas Generales**: Vea un resumen de la satisfacción general y otros indicadores clave basados en los filtros aplicados.
    3.  **Navegación**: Haga clic en las opciones de la barra lateral para explorar análisis detallados por categoría o geografía.
    4.  **Refrescar Datos**: Si cree que los datos en Google Sheets han cambiado recientemente, use el botón "Refrescar Datos" para forzar una recarga desde la fuente (esto puede tomar unos segundos).
    """)

# Footer
st.markdown("---")
st.markdown(f"Dashboard de Análisis de Encuestas - {time.strftime('%Y-%m-%d %H:%M:%S')}") # Añadir timestamp
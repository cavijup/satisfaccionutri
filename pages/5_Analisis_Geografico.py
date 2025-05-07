import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data, get_filtered_data
from utils.data_processing import (
    get_satisfaction_columns,
    CATEGORIES
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
Esta sección presenta el análisis comparativo de la satisfacción por ubicación geográfica,
permitiendo identificar diferencias entre comunas, barrios, nodos y nichos.
""")

# Cargar datos
df = load_data()

if df.empty:
    st.error("No se pudieron cargar los datos. Verifica tus credenciales y la conexión a Google Sheets.")
    st.stop()

# Obtener los filtros de la página principal (si existen)
date_range = None

# Intentar obtener el rango de fechas del state
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

# Aplicar filtros (sólo fecha, ya que aquí analizamos por ubicación)
filtered_df = df.copy()

if date_range and len(date_range) == 2 and 'fecha' in df.columns:
    start_date, end_date = date_range
    filtered_df = filtered_df[(filtered_df['fecha'].dt.date >= start_date) & 
                              (filtered_df['fecha'].dt.date <= end_date)]

# Mostrar número de encuestas filtradas
st.sidebar.metric("Total de encuestas", len(filtered_df))

# Verificar variables geográficas disponibles
geo_vars = []
if 'comuna' in filtered_df.columns:
    geo_vars.append('comuna')
if 'barrio' in filtered_df.columns:
    geo_vars.append('barrio')
if 'nodo' in filtered_df.columns:
    geo_vars.append('nodo')
if 'nicho' in filtered_df.columns:
    geo_vars.append('nicho')

if not geo_vars:
    st.warning("No se encontraron variables geográficas en los datos.")
    st.stop()

# Selector de variable geográfica
selected_geo_var = st.selectbox(
    "Seleccionar variable geográfica para análisis",
    geo_vars,
    index=0
)

# Análisis por categoría de producto y ubicación
st.header("Análisis por Categoría de Producto y Ubicación")

# Selector de categoría
category_options = list(CATEGORIES.keys())
selected_category = st.selectbox(
    "Seleccionar categoría de producto",
    category_options,
    index=0
)

# Obtener columnas de la categoría seleccionada
category_cols = CATEGORIES[selected_category]
valid_cols = [col for col in category_cols if col in filtered_df.columns]

if not valid_cols:
    st.warning(f"No se encontraron datos para la categoría {selected_category}.")
else:
    # Calcular satisfacción promedio por categoría y ubicación
    for col in valid_cols:
        filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
    
    filtered_df[f'{selected_category}_avg'] = filtered_df[valid_cols].mean(axis=1)
    
    # Agrupar por variable geográfica
    geo_category_data = filtered_df.groupby(selected_geo_var)[f'{selected_category}_avg'].agg(['mean', 'count']).reset_index()
    geo_category_data.columns = [selected_geo_var, 'Satisfacción Promedio', 'Conteo']
    
    # Mostrar tabla en lugar de gráfico
    st.subheader(f"Satisfacción con {selected_category} por {selected_geo_var}")
    st.dataframe(geo_category_data.sort_values('Satisfacción Promedio', ascending=False), use_container_width=True)

# Identificación de ubicaciones problemáticas
st.header("Identificación de Ubicaciones Problemáticas")

# Calcular satisfacción promedio por ubicación
satisfaction_cols = get_satisfaction_columns(filtered_df)

if satisfaction_cols:
    filtered_df['satisfaccion_promedio'] = filtered_df[satisfaction_cols].mean(axis=1)
    
    # Agrupar por ubicación
    geo_satisfaction = filtered_df.groupby(selected_geo_var)['satisfaccion_promedio'].agg(['mean', 'count']).reset_index()
    geo_satisfaction.columns = [selected_geo_var, 'Satisfacción Promedio', 'Cantidad de Encuestas']
    
    # Ordenar de menor a mayor satisfacción
    geo_satisfaction = geo_satisfaction.sort_values('Satisfacción Promedio')
    
    # Mostrar tabla
    st.subheader(f"Ranking de {selected_geo_var} por Satisfacción")
    st.dataframe(geo_satisfaction, use_container_width=True)
    
    # Identificar las ubicaciones con menor satisfacción
    worst_locations = geo_satisfaction.head(3)
    
    st.subheader(f"{selected_geo_var.capitalize()} con menor satisfacción")
    st.markdown("""
    Las siguientes ubicaciones presentan los niveles más bajos de satisfacción 
    y podrían requerir atención prioritaria:
    """)
    
    for i, row in worst_locations.iterrows():
        st.markdown(f"""
        - **{row[selected_geo_var]}**: Satisfacción promedio de **{row['Satisfacción Promedio']:.2f}/5** 
        (basado en {row['Cantidad de Encuestas']} encuestas)
        """)
else:
    st.info("No hay columnas de satisfacción disponibles para identificar ubicaciones problemáticas.")

# Conclusiones y recomendaciones
st.header("Conclusiones y Recomendaciones")

if satisfaction_cols and len(geo_vars) > 0:
    st.markdown("""
    El análisis geográfico permite identificar patrones de satisfacción según la ubicación, 
    lo que puede ayudar a:
    
    - **Priorizar recursos** en las zonas con menor satisfacción
    - **Identificar buenas prácticas** en las zonas con mayor satisfacción
    - **Ajustar procesos** según las necesidades específicas de cada zona
    - **Mejorar la capacitación** del personal en ubicaciones específicas
    
    Recomendaciones generales:
    
    - Realizar seguimiento detallado a las ubicaciones con menor satisfacción
    - Establecer planes de acción específicos por zona
    - Considerar factores logísticos particulares de cada ubicación
    - Compartir experiencias exitosas entre diferentes ubicaciones
    """)
else:
    st.info("No hay datos suficientes para generar conclusiones y recomendaciones.")

# Footer
st.markdown("---")
st.markdown("Dashboard de Análisis de la Encuesta de Satisfacción | Sección: Análisis Geográfico")
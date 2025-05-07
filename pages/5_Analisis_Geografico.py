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
enfocándose en el proceso de entrega de mercados.
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

# Establecer 'comuna' como la variable geográfica por defecto si está disponible
selected_geo_var = 'comuna' if 'comuna' in geo_vars else geo_vars[0]

# Análisis del Proceso de Entrega por ubicación
st.header(f"Satisfacción con Proceso de Entrega por {selected_geo_var}")

# Obtener columnas del proceso de entrega
entrega_cols = [col for col in filtered_df.columns if col.startswith(('23', '24', '25', '26', '27', '28'))]

if not entrega_cols:
    st.warning("No se encontraron datos del proceso de entrega en la encuesta.")
else:
    # Convertir columnas a numéricas
    for col in entrega_cols:
        filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')
    
    # Calcular satisfacción promedio con el proceso de entrega
    filtered_df['satisfaccion_entrega'] = filtered_df[entrega_cols].mean(axis=1)
    
    # Agrupar por variable geográfica
    geo_entrega_data = filtered_df.groupby(selected_geo_var)['satisfaccion_entrega'].agg(['mean', 'count']).reset_index()
    geo_entrega_data.columns = [selected_geo_var, 'Satisfacción Promedio', 'Cantidad de Encuestas']
    
    # Ordenar por satisfacción promedio (descendente)
    geo_entrega_data = geo_entrega_data.sort_values('Satisfacción Promedio', ascending=False)
    
    # Mostrar tabla
    st.dataframe(geo_entrega_data, use_container_width=True)
    
    # Identificar ubicaciones con mayor y menor satisfacción
    if len(geo_entrega_data) > 0:
        best_location = geo_entrega_data.iloc[0]
        worst_location = geo_entrega_data.iloc[-1]
        
        # Calcular satisfacción por aspecto específico del proceso de entrega
        aspects_data = {}
        
        for col in entrega_cols:
            # Obtener descripción amigable del aspecto
            if col == '23ciclo_menus':
                aspect_name = "Ciclo de menús"
            elif col == '24notificacion_telefonica':
                aspect_name = "Notificación telefónica"
            elif col == '25tiempo_revision_alimentos':
                aspect_name = "Tiempo de revisión"
            elif col == '26tiempo_entrega_mercdos':
                aspect_name = "Tiempo entre entregas"
            elif col == '27tiempo_demora_proveedor':
                aspect_name = "Tiempo de respuesta para reposiciones"
            elif col == '28actitud_funcionario_logistico':
                aspect_name = "Actitud del funcionario"
            else:
                aspect_name = col
            
            # Calcular promedios por ubicación para este aspecto
            aspect_avg = filtered_df.groupby(selected_geo_var)[col].mean().to_dict()
            aspects_data[aspect_name] = aspect_avg
        
        # Conclusiones y recomendaciones
        st.header("Conclusiones y Recomendaciones")
        
        st.subheader("Análisis de Satisfacción por Ubicación")
        st.markdown(f"""
        Basado en el análisis del proceso de entrega por {selected_geo_var}, se observa que:
        
        - **{best_location[selected_geo_var]}** presenta la mayor satisfacción promedio con **{best_location['Satisfacción Promedio']:.2f}/5** (basado en {int(best_location['Cantidad de Encuestas'])} encuestas).
        - **{worst_location[selected_geo_var]}** presenta la menor satisfacción promedio con **{worst_location['Satisfacción Promedio']:.2f}/5** (basado en {int(worst_location['Cantidad de Encuestas'])} encuestas).
        """)
        
        # Análisis detallado de la ubicación con menor satisfacción
        st.subheader(f"Análisis Detallado de {worst_location[selected_geo_var]}")
        
        # Encontrar los aspectos con menor satisfacción en la ubicación problemática
        worst_location_aspects = {}
        for aspect_name, avg_dict in aspects_data.items():
            if worst_location[selected_geo_var] in avg_dict:
                worst_location_aspects[aspect_name] = avg_dict[worst_location[selected_geo_var]]
        
        # Ordenar aspectos por satisfacción (de menor a mayor)
        sorted_aspects = sorted(worst_location_aspects.items(), key=lambda x: x[1])
        
        # Mostrar los aspectos más problemáticos
        if sorted_aspects:
            st.markdown(f"Los aspectos con menor satisfacción en **{worst_location[selected_geo_var]}** son:")
            
            for aspect, score in sorted_aspects[:3]:  # Mostrar los 3 aspectos más problemáticos
                st.markdown(f"- **{aspect}**: {score:.2f}/5")
            
            # Recomendaciones específicas
            st.subheader("Recomendaciones")
            st.markdown(f"""
            Para mejorar la satisfacción en **{worst_location[selected_geo_var]}**, se recomienda:
            
            1. **Enfoque prioritario**: Concentrar recursos para mejorar "{sorted_aspects[0][0]}", que es el aspecto con menor satisfacción.
            2. **Capacitación específica**: Proporcionar capacitación adicional al personal que atiende esta ubicación.
            3. **Seguimiento directo**: Implementar un protocolo de seguimiento especial para esta ubicación.
            4. **Comunicación mejorada**: Establecer canales de comunicación más efectivos con los beneficiarios.
            5. **Aprendizaje de buenas prácticas**: Evaluar e implementar las prácticas exitosas observadas en **{best_location[selected_geo_var]}**.
            
            Estas acciones deberían ayudar a mejorar la satisfacción general con el proceso de entrega de mercados en las ubicaciones con menor desempeño.
            """)
        else:
            st.info(f"No hay suficientes datos para analizar aspectos específicos en {worst_location[selected_geo_var]}.")
    else:
        st.info("No hay suficientes datos para generar conclusiones y recomendaciones.")

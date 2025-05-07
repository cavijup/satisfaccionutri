import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_filtered_data
from utils.data_processing import (
    plot_question_satisfaction,
    COL_DESCRIPTIONS
)

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Frutas y Verduras",
    page_icon="🥕",
    layout="wide"
)

# Título y descripción
st.title("Análisis de Satisfacción - Frutas y Verduras")
st.markdown("""
Esta sección presenta el análisis detallado de la satisfacción con las frutas, verduras, hortalizas y tubérculos entregados,
incluyendo aspectos como frescura, maduración, calidad y estado de los productos.
""")

# Cargar datos
df = load_data()

if df.empty:
    st.error("No se pudieron cargar los datos. Verifica tus credenciales y la conexión a Google Sheets.")
    st.stop()

# Obtener los filtros de la página principal (si existen)
date_range = None
selected_comuna = None
selected_barrio = None
selected_nodo = None

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

# Filtro por ubicación geográfica
if 'comuna' in df.columns:
    all_comunas = ["Todas"] + sorted([str(x) for x in df['comuna'].unique() if pd.notna(x)])
    selected_comuna = st.sidebar.selectbox("Comuna", all_comunas)

if 'barrio' in df.columns:
    all_barrios = ["Todos"] + sorted([str(x) for x in df['barrio'].unique() if pd.notna(x)])
    selected_barrio = st.sidebar.selectbox("Barrio", all_barrios)

if 'nodo' in df.columns:
    all_nodos = ["Todos"] + sorted([str(x) for x in df['nodo'].unique() if pd.notna(x)])
    selected_nodo = st.sidebar.selectbox("Nodo", all_nodos)

# Aplicar filtros
filtered_df = get_filtered_data(df, date_range, selected_comuna, selected_barrio, selected_nodo)

# Mostrar número de encuestas filtradas
st.sidebar.metric("Total de encuestas filtradas", len(filtered_df))

# Mapeo de las columnas de frutas y verduras
frutas_verduras_cols = {
    '19frutas': 'Estado y calidad de las frutas recibidas',
    '20verduras': 'Estado y calidad de las verduras recibidas',
    '21hortalizas': 'Estado y calidad de las hortalizas recibidas',
    '22tuberculos': 'Estado y calidad de los tubérculos recibidos'
}

# Análisis de satisfacción por pregunta
st.header("Satisfacción con Frutas y Verduras")

# Comprobar si existen las columnas
available_cols = [col for col in frutas_verduras_cols.keys() if col in filtered_df.columns]

if not available_cols:
    st.warning("No se encontraron datos de satisfacción con frutas y verduras en la encuesta.")
    st.stop()

# Crear tabs para diferentes categorías
frutas_tab, verduras_tab = st.tabs(["Frutas", "Verduras y Hortalizas"])

# Definir las columnas para cada pestaña
frutas_cols = ['19frutas']
verduras_tuberculos_cols = ['20verduras', '21hortalizas', '22tuberculos']

# Obtener columnas disponibles para cada categoría
frutas_available = [col for col in frutas_cols if col in available_cols]
verduras_tuberculos_available = [col for col in verduras_tuberculos_cols if col in available_cols]

with frutas_tab:
    if frutas_available:
        st.subheader("Satisfacción con Frutas")
        
        # Mostrar gráficos para frutas
        for col in frutas_available:
            fig = plot_question_satisfaction(filtered_df, col, frutas_verduras_cols[col])
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No hay datos suficientes para '{frutas_verduras_cols[col]}'")
    else:
        st.info("No se encontraron datos de satisfacción con frutas en la encuesta.")

with verduras_tab:
    if verduras_tuberculos_available:
        st.subheader("Satisfacción con Verduras, Hortalizas y Tubérculos")
        
        # Mostrar gráficos en grid
        for i in range(0, len(verduras_tuberculos_available), 2):
            col1, col2 = st.columns(2)
            
            # Primera columna
            fig1 = plot_question_satisfaction(filtered_df, verduras_tuberculos_available[i], frutas_verduras_cols[verduras_tuberculos_available[i]])
            if fig1:
                col1.plotly_chart(fig1, use_container_width=True)
            else:
                col1.info(f"No hay datos suficientes para '{frutas_verduras_cols[verduras_tuberculos_available[i]]}'")
            
            # Segunda columna (si existe)
            if i + 1 < len(verduras_tuberculos_available):
                fig2 = plot_question_satisfaction(filtered_df, verduras_tuberculos_available[i+1], frutas_verduras_cols[verduras_tuberculos_available[i+1]])
                if fig2:
                    col2.plotly_chart(fig2, use_container_width=True)
                else:
                    col2.info(f"No hay datos suficientes para '{frutas_verduras_cols[verduras_tuberculos_available[i+1]]}'")
    else:
        st.info("No se encontraron datos de satisfacción con verduras, hortalizas o tubérculos en la encuesta.")

# Análisis de Comedores con Insatisfacción
st.header("Comedores con Niveles de Insatisfacción")

# Verificar que existan las columnas de satisfacción y la columna de identificación del comedor
satisfaccion_cols = [col for col in frutas_verduras_cols.keys() if col in filtered_df.columns]
id_comedor_col = next((col for col in ['nombre_comedor', 'comedor', 'id_comedor'] if col in filtered_df.columns), None)

if not satisfaccion_cols:
    st.warning("No se encontraron datos de satisfacción con frutas y verduras en la encuesta.")
elif not id_comedor_col:
    st.warning("No se encontró columna de identificación del comedor comunitario.")
else:
    # Crear dataframe para análisis
    analisis_df = filtered_df.copy()
    
    # Función para identificar valores de insatisfacción
    def es_insatisfecho(valor):
        if pd.isna(valor):
            return False
        
        # Si es numérico, considerar valores menores o iguales a 2 como insatisfacción
        if isinstance(valor, (int, float)):
            return valor <= 2
        
        # Si es texto, buscar las palabras clave
        valor_str = str(valor).upper()
        return "INSATISFECHO" in valor_str or "MUY INSATISFECHO" in valor_str
    
    # Identificar comedores con insatisfacción
    comedores_insatisfechos = {}
    
    for col in satisfaccion_cols:
        # Filtrar filas con insatisfacción
        insatisfaccion_mask = analisis_df[col].apply(es_insatisfecho)
        
        if insatisfaccion_mask.any():
            # Agrupar por comedor y contar insatisfacciones
            insatisfacciones = analisis_df[insatisfaccion_mask].groupby(id_comedor_col).size()
            
            # Almacenar resultados
            for comedor, count in insatisfacciones.items():
                if comedor not in comedores_insatisfechos:
                    comedores_insatisfechos[comedor] = {}
                
                comedores_insatisfechos[comedor][frutas_verduras_cols[col]] = count
    
    # Mostrar resultados
    if comedores_insatisfechos:
        # Convertir a DataFrame para mejor visualización
        resultado_df = pd.DataFrame.from_dict(comedores_insatisfechos, orient='index')
        
        # Reemplazar NaN con 0
        resultado_df = resultado_df.fillna(0)
        
        # Agregar columna de total
        resultado_df['Total Insatisfacciones'] = resultado_df.sum(axis=1)
        
        # Ordenar por total de insatisfacciones (descendente)
        resultado_df = resultado_df.sort_values('Total Insatisfacciones', ascending=False)
        
        # Mostrar como tabla
        st.write("Comedores con reportes de insatisfacción en frutas y verduras:")
        st.dataframe(resultado_df, use_container_width=True)
        
        # Conclusión textual sobre comedores con insatisfacciones
        st.subheader("Comedores con problemas de insatisfacción")
        
        # Tomar los primeros comedores (los más problemáticos)
        top_comedores = resultado_df.head(5)
        
        # Crear conclusión textual
        st.markdown("### Resumen de hallazgos")
        
        # Texto introductorio
        st.markdown(f"""
        Se han identificado **{len(resultado_df)}** comedores comunitarios que presentan reportes 
        de insatisfacción con las frutas y verduras entregadas. A continuación se detallan los comedores 
        con mayores niveles de insatisfacción:
        """)
        
        # Lista de comedores problemáticos
        for comedor, row in top_comedores.iterrows():
            # Obtener los aspectos con insatisfacción para este comedor
            aspectos_insatisfechos = []
            for aspecto, valor in row.items():
                if aspecto != 'Total Insatisfacciones' and valor > 0:
                    aspectos_insatisfechos.append(aspecto)
            
            aspectos_texto = ", ".join(aspectos_insatisfechos)
            st.markdown(f"""
            - **{comedor}**: {int(row['Total Insatisfacciones'])} reportes de insatisfacción.
              Aspectos problemáticos: {aspectos_texto}
            """)
        
        # Recomendaciones generales
        st.markdown("""
        ### Recomendaciones
        
        Se sugiere implementar un plan de seguimiento especial para estos comedores, 
        con énfasis en los aspectos señalados como problemáticos. Es recomendable:
        
        1. Revisar los procesos de selección de frutas y verduras antes de enviarlas a estos comedores
        2. Verificar el tiempo de transporte y condiciones de almacenamiento para estos destinos
        3. Asegurar que los productos perecederos lleguen con el grado de madurez adecuado
        4. Considerar aumentar la variedad de productos entregados a estos comedores
        5. Implementar un control de calidad adicional para envíos a estas ubicaciones
        """)
    else:
        st.success("No se encontraron comedores con reportes de insatisfacción en frutas y verduras.")

# Conclusiones y recomendaciones
st.header("Conclusiones y Recomendaciones")

# Análisis automático basado en los datos
if available_cols:
    # Calcular promedios de satisfacción
    satisfaction_means = {}
    for col in available_cols:
        satisfaction_means[col] = filtered_df[col].mean()
    
    # Identificar el aspecto con menor satisfacción
    min_aspect = min(satisfaction_means, key=satisfaction_means.get)
    min_score = satisfaction_means[min_aspect]
    
    # Identificar el aspecto con mayor satisfacción
    max_aspect = max(satisfaction_means, key=satisfaction_means.get)
    max_score = satisfaction_means[max_aspect]
    
    # Mostrar conclusiones
    st.markdown(f"""
    Basado en el análisis de los datos:
    
    - El aspecto con **mayor satisfacción** es "{frutas_verduras_cols[max_aspect]}" con un puntaje promedio de **{max_score:.2f}/5**.
    - El aspecto con **menor satisfacción** es "{frutas_verduras_cols[min_aspect]}" con un puntaje promedio de **{min_score:.2f}/5**.
    
    **Recomendaciones:**
    
    - Mejorar los procesos relacionados con "{frutas_verduras_cols[min_aspect]}"
    - Mantener las buenas prácticas relacionadas con "{frutas_verduras_cols[max_aspect]}"
    - Evaluar el sistema de selección, transporte y almacenaje de frutas y verduras
    - Considerar implementar controles de calidad más estrictos para estos productos perecederos
    """)
else:
    st.info("No hay datos suficientes para generar conclusiones y recomendaciones.")

# Footer
st.markdown("---")
st.markdown("Dashboard de Análisis de la Encuesta de Satisfacción | Sección: Frutas y Verduras")
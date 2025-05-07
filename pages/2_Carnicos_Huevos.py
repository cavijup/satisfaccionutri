import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_filtered_data
from utils.data_processing import (
    plot_question_satisfaction,
    COL_DESCRIPTIONS
)

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Cárnicos y Huevos",
    page_icon="🍖",
    layout="wide"
)

# Título y descripción
st.title("Análisis de Satisfacción - Cárnicos y Huevos")
st.markdown("""
Esta sección presenta el análisis detallado de la satisfacción con los cárnicos (cerdo y pollo) y huevos entregados,
incluyendo aspectos como etiquetado, estado de congelación, corte y empaque.
""")

# Cargar datos
df = load_data()

if df.empty:
    st.error("No se pudieron cargar los datos. Verifica tus credenciales y la conexión a Google Sheets.")
    st.stop()

# Obtener los filtros de la página principal (solo para mostrar en la UI)
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
            "Rango de fechas (Desactivado)",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

# Filtro por ubicación geográfica (desactivados)
if 'comuna' in df.columns:
    all_comunas = ["Todas"] + sorted([str(x) for x in df['comuna'].unique() if pd.notna(x)])
    selected_comuna = st.sidebar.selectbox("Comuna (Desactivado)", all_comunas)

if 'barrio' in df.columns:
    all_barrios = ["Todos"] + sorted([str(x) for x in df['barrio'].unique() if pd.notna(x)])
    selected_barrio = st.sidebar.selectbox("Barrio (Desactivado)", all_barrios)

if 'nodo' in df.columns:
    all_nodos = ["Todos"] + sorted([str(x) for x in df['nodo'].unique() if pd.notna(x)])
    selected_nodo = st.sidebar.selectbox("Nodo (Desactivado)", all_nodos)

# Información sobre filtros desactivados
st.sidebar.info("Los filtros están desactivados temporalmente para mostrar todos los datos disponibles.")

# NO aplicar filtros - Usar el DataFrame completo
filtered_df = df.copy()  # Usar todos los datos sin filtrar

# Mostrar número de encuestas
st.sidebar.metric("Total de encuestas", len(filtered_df))

# Mapeo de las columnas de cárnicos y huevos
carnicos_cols = {
    '12carnes_bien_etiquetadas': 'Las carnes se encuentran bien etiquetadas (peso, fechas, tipo de corte)',
    '13producto_congelado': 'El producto se encuentra congelado al momento de recibirlo',
    '14corte_recibido': 'El corte del producto recibido es el mismo que aparece en la etiqueta',
    '15fecha_vencimiento_adecuada': 'La fecha de vencimiento es adecuada para la preparación',
    '16empacado_al_vacio': 'El producto está empacado al vacío',
    '17estado_huevo': 'Estado de los huevos recibidos',
    '18panal_de_huevo_etiquetado': 'El panal de huevos se encuentra etiquetado con fecha vencimiento'
}

# Análisis de satisfacción por pregunta
st.header("Satisfacción con Cárnicos y Huevos")

# Comprobar si existen las columnas
available_cols = [col for col in carnicos_cols.keys() if col in filtered_df.columns]

if not available_cols:
    st.warning("No se encontraron datos de satisfacción con cárnicos y huevos en la encuesta.")
    st.stop()

# Crear tabs para diferentes categorías
carnes_tab, huevos_tab = st.tabs(["Cárnicos", "Huevos"])

# Columnas de cárnicos
carnes_cols = ['12carnes_bien_etiquetadas', '13producto_congelado', '14corte_recibido', 
               '15fecha_vencimiento_adecuada', '16empacado_al_vacio']
carnes_available = [col for col in carnes_cols if col in available_cols]

with carnes_tab:
    if carnes_available:
        st.subheader("Satisfacción con Cárnicos")
        
        # Mostrar gráficos en grid
        for i in range(0, len(carnes_available), 2):
            col1, col2 = st.columns(2)
            
            # Primera columna
            fig1 = plot_question_satisfaction(filtered_df, carnes_available[i], carnicos_cols[carnes_available[i]])
            if fig1:
                col1.plotly_chart(fig1, use_container_width=True)
            else:
                col1.info(f"No hay datos suficientes para '{carnicos_cols[carnes_available[i]]}'")
            
            # Segunda columna (si existe)
            if i + 1 < len(carnes_available):
                fig2 = plot_question_satisfaction(filtered_df, carnes_available[i+1], carnicos_cols[carnes_available[i+1]])
                if fig2:
                    col2.plotly_chart(fig2, use_container_width=True)
                else:
                    col2.info(f"No hay datos suficientes para '{carnicos_cols[carnes_available[i+1]]}'")
    else:
        st.info("No se encontraron datos de satisfacción con cárnicos en la encuesta.")

# Columnas de huevos
huevos_cols = ['17estado_huevo', '18panal_de_huevo_etiquetado']
huevos_available = [col for col in huevos_cols if col in available_cols]

with huevos_tab:
    if huevos_available:
        st.subheader("Satisfacción con Huevos")
        
        # Mostrar gráficos en columnas
        col1, col2 = st.columns(2)
        
        # Primera columna (si existe)
        if len(huevos_available) > 0:
            fig1 = plot_question_satisfaction(filtered_df, huevos_available[0], carnicos_cols[huevos_available[0]])
            if fig1:
                col1.plotly_chart(fig1, use_container_width=True)
            else:
                col1.info(f"No hay datos suficientes para '{carnicos_cols[huevos_available[0]]}'")
        
        # Segunda columna (si existe)
        if len(huevos_available) > 1:
            fig2 = plot_question_satisfaction(filtered_df, huevos_available[1], carnicos_cols[huevos_available[1]])
            if fig2:
                col2.plotly_chart(fig2, use_container_width=True)
            else:
                col2.info(f"No hay datos suficientes para '{carnicos_cols[huevos_available[1]]}'")
    else:
        st.info("No se encontraron datos de satisfacción con huevos en la encuesta.")

# Análisis de Comedores con Insatisfacción
st.header("Comedores con Niveles de Insatisfacción")

# Verificar que existan las columnas de satisfacción y la columna de identificación del comedor
satisfaccion_cols = [col for col in carnicos_cols.keys() if col in filtered_df.columns]
id_comedor_col = next((col for col in ['nombre_comedor', 'comedor', 'id_comedor'] if col in filtered_df.columns), None)

if not satisfaccion_cols:
    st.warning("No se encontraron datos de satisfacción con cárnicos y huevos en la encuesta.")
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
                
                comedores_insatisfechos[comedor][carnicos_cols[col]] = count
    
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
        st.write("Comedores con reportes de insatisfacción en cárnicos y huevos:")
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
        de insatisfacción con los cárnicos y huevos entregados. A continuación se detallan los comedores 
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
        
        1. Revisar con los proveedores de cárnicos los estándares de calidad, especialmente para estos comedores
        2. Verificar la cadena de frío durante el transporte a estas ubicaciones
        3. Implementar un protocolo de inspección especial para los productos destinados a estos comedores
        4. Realizar seguimiento a la calidad de los huevos, verificando su frescura y correcto etiquetado
        """)
    else:
        st.success("No se encontraron comedores con reportes de insatisfacción en cárnicos y huevos.")

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
    
    - El aspecto con **mayor satisfacción** es "{carnicos_cols[max_aspect]}" con un puntaje promedio de **{max_score:.2f}/5**.
    - El aspecto con **menor satisfacción** es "{carnicos_cols[min_aspect]}" con un puntaje promedio de **{min_score:.2f}/5**.
    
    **Recomendaciones:**
    
    - Revisar los procesos relacionados con "{carnicos_cols[min_aspect]}"
    - Fortalecer los controles de calidad para cárnicos y huevos
    - Evaluar la posibilidad de cambiar proveedores si los problemas persisten
    """)
else:
    st.info("No hay datos suficientes para generar conclusiones y recomendaciones.")

# Footer
st.markdown("---")
st.markdown("Dashboard de Análisis de la Encuesta de Satisfacción | Sección: Cárnicos y Huevos")
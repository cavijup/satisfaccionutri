import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_filtered_data
from utils.data_processing import (
    plot_question_satisfaction,
    plot_yes_no_questions,
    plot_complexity_analysis,
    COL_DESCRIPTIONS
)

# Configuración de la página
st.set_page_config(
    page_title="Análisis del Proceso de Entrega",
    page_icon="🚚",
    layout="wide"
)

# Título y descripción
st.title("Análisis de Satisfacción - Proceso de Entrega de Mercado")
st.markdown("""
Esta sección presenta el análisis detallado de la satisfacción con el proceso de entrega de mercados,
incluyendo aspectos como ciclo de menús, notificación, tiempos de revisión y atención del personal.
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

# Intentar obtener el rango de fechas (desactivado)
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

# Mapeo de las columnas del proceso de entrega
entrega_cols = {
    '23ciclo_menus': 'El ciclo de menús establecido por el proyecto',
    '24notificacion_telefonica': 'La notificación telefónica para informar fecha y hora de entrega',
    '25tiempo_revision_alimentos': 'El tiempo para revisar los alimentos al recibirlos',
    '26tiempo_entrega_mercdos': 'El tiempo entre las entregas de los mercados (10 días hábiles)',
    '27tiempo_demora_proveedor': 'El tiempo de respuesta para reposiciones o ajustes',
    '28actitud_funcionario_logistico': 'La actitud y disposición del funcionario logístico'
}

# Análisis de satisfacción por aspectos del proceso
st.header("Satisfacción con el Proceso de Entrega")

# Comprobar si existen las columnas
available_cols = [col for col in entrega_cols.keys() if col in filtered_df.columns]

if not available_cols:
    st.warning("No se encontraron datos de satisfacción con el proceso de entrega en la encuesta.")
    st.stop()

# Crear tabs para diferentes aspectos del proceso
logistica_tab, tiempos_tab, personal_tab = st.tabs(["Logística", "Tiempos", "Personal"])

# Columnas para cada tab
logistica_cols = ['23ciclo_menus', '24notificacion_telefonica']
tiempos_cols = ['25tiempo_revision_alimentos', '26tiempo_entrega_mercdos', '27tiempo_demora_proveedor']
personal_cols = ['28actitud_funcionario_logistico']

with logistica_tab:
    logistica_available = [col for col in logistica_cols if col in available_cols]
    
    if logistica_available:
        st.subheader("Satisfacción con Aspectos Logísticos")
        
        col1, col2 = st.columns(2)
        
        # Primera columna (si existe)
        if len(logistica_available) > 0:
            fig1 = plot_question_satisfaction(filtered_df, logistica_available[0], entrega_cols[logistica_available[0]])
            if fig1:
                col1.plotly_chart(fig1, use_container_width=True)
            else:
                col1.info(f"No hay datos suficientes para '{entrega_cols[logistica_available[0]]}'")
        
        # Segunda columna (si existe)
        if len(logistica_available) > 1:
            fig2 = plot_question_satisfaction(filtered_df, logistica_available[1], entrega_cols[logistica_available[1]])
            if fig2:
                col2.plotly_chart(fig2, use_container_width=True)
            else:
                col2.info(f"No hay datos suficientes para '{entrega_cols[logistica_available[1]]}'")
    else:
        st.info("No se encontraron datos de satisfacción con aspectos logísticos.")

with tiempos_tab:
    tiempos_available = [col for col in tiempos_cols if col in available_cols]
    
    if tiempos_available:
        st.subheader("Satisfacción con Tiempos")
        
        # Mostrar gráficos
        for i, col in enumerate(tiempos_available):
            fig = plot_question_satisfaction(filtered_df, col, entrega_cols[col])
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No hay datos suficientes para '{entrega_cols[col]}'")
    else:
        st.info("No se encontraron datos de satisfacción con tiempos.")

with personal_tab:
    personal_available = [col for col in personal_cols if col in available_cols]
    
    if personal_available:
        st.subheader("Satisfacción con el Personal")
        
        # Mostrar gráficos
        for col in personal_available:
            fig = plot_question_satisfaction(filtered_df, col, entrega_cols[col])
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No hay datos suficientes para '{entrega_cols[col]}'")
    else:
        st.info("No se encontraron datos de satisfacción con el personal.")

# Análisis de preguntas sí/no
st.header("Cumplimiento y Comunicación")

yes_no_fig = plot_yes_no_questions(filtered_df)
if yes_no_fig:
    st.plotly_chart(yes_no_fig, use_container_width=True)
else:
    st.info("No hay datos suficientes para el análisis de preguntas sí/no.")

# Análisis de Comedores con Insatisfacción
st.header("Comedores con Niveles de Insatisfacción")

# Verificar que existan las columnas de satisfacción y la columna de identificación del comedor
satisfaccion_cols = [col for col in entrega_cols.keys() if col in filtered_df.columns]
id_comedor_col = next((col for col in ['nombre_comedor', 'comedor', 'id_comedor'] if col in filtered_df.columns), None)

if not satisfaccion_cols:
    st.warning("No se encontraron datos de satisfacción con el proceso de entrega en la encuesta.")
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
                
                comedores_insatisfechos[comedor][entrega_cols[col]] = count
    
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
        st.write("Comedores con reportes de insatisfacción en el proceso de entrega:")
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
        de insatisfacción con el proceso de entrega de mercados. A continuación se detallan los comedores 
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
        
        1. Mejorar la comunicación con estos comedores respecto a fechas y horarios de entrega
        2. Revisar los tiempos de entrega y ajustarlos según las necesidades específicas de cada comedor
        3. Proporcionar capacitación adicional al personal que atiende estos comedores
        4. Implementar un sistema de seguimiento posterior a la entrega para verificar la satisfacción
        5. Establecer un canal directo de comunicación para resolver problemas de manera ágil
        """)
    else:
        st.success("No se encontraron comedores con reportes de insatisfacción en el proceso de entrega.")

# Análisis de sugerencias de mejora
st.header("Sugerencias de Mejora")

# Verificar si existe la columna de sugerencias
if '32aspectos_de_mejora' in filtered_df.columns:
    # En lugar de nube de palabras, mostrar las principales sugerencias agrupadas
    sugerencias = filtered_df['32aspectos_de_mejora'].dropna().astype(str)
    
    if not sugerencias.empty:
        # Mostrar conteo de sugerencias
        st.write(f"Se han registrado **{len(sugerencias)}** sugerencias de mejora. A continuación se muestran las 5 sugerencias más representativas:")
        
        # Mostrar las 5 sugerencias más largas (probablemente las más detalladas)
        sugerencias_ordenadas = sugerencias.sort_values(key=lambda x: x.str.len(), ascending=False)
        for i, sugerencia in enumerate(sugerencias_ordenadas.head(5), 1):
            if len(sugerencia) > 10:  # Solo mostrar sugerencias significativas
                st.markdown(f"**{i}. Sugerencia de mejora:** {sugerencia}")
    else:
        st.info("No se han registrado sugerencias de mejora.")
else:
    st.info("No se encontró la columna de sugerencias de mejora.")

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
    
    # Calcular si el proceso es percibido como sencillo
    if '31pasos_recepcion_mercado' in filtered_df.columns:
        proceso_sencillo = (filtered_df['31pasos_recepcion_mercado'].astype(str).str.lower() == 'sencillo').mean() * 100
    else:
        proceso_sencillo = None
    
    # Mostrar conclusiones
    st.markdown(f"""
    Basado en el análisis de los datos:
    
    - El aspecto con **mayor satisfacción** es "{entrega_cols[max_aspect]}" con un puntaje promedio de **{max_score:.2f}/5**.
    - El aspecto con **menor satisfacción** es "{entrega_cols[min_aspect]}" con un puntaje promedio de **{min_score:.2f}/5**.
    """)
    
    if proceso_sencillo is not None:
        st.markdown(f"- El **{proceso_sencillo:.1f}%** de los encuestados considera que el proceso de recepción es **sencillo**.")
    
    st.markdown("""
    **Recomendaciones:**
    
    - Revisar y optimizar los aspectos con menor satisfacción
    - Mantener un canal de comunicación abierto con los beneficiarios
    - Evaluar posibles ajustes en los tiempos y la logística del proceso
    - Proporcionar capacitación adicional al personal de entrega
    """)
else:
    st.info("No hay datos suficientes para generar conclusiones y recomendaciones.")

# Footer
st.markdown("---")
st.markdown("Dashboard de Análisis de la Encuesta de Satisfacción | Sección: Proceso de Entrega de Mercado")
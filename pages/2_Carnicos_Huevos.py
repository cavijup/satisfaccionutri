import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_filtered_data
from utils.data_processing import (
    plot_question_satisfaction,
    COL_DESCRIPTIONS
)

# Función para convertir gráficos a barras horizontales
def make_horizontal_chart(fig, title_with_icon=None):
    """
    Convierte cualquier gráfico de barras verticales a horizontales y aplica fondo blanco
    """
    if fig is None:
        return None
    
    try:
        # Intercambiar x e y para hacer horizontal
        for trace in fig.data:
            if hasattr(trace, 'x') and hasattr(trace, 'y'):
                # Intercambiar valores
                temp_x = trace.x
                trace.x = trace.y
                trace.y = temp_x
                
                # Cambiar orientación
                if hasattr(trace, 'orientation'):
                    trace.orientation = 'h'
        
        # Actualizar layout para fondo blanco y ajustar ejes
        layout_updates = {
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'xaxis_title': "Número de Respuestas",
            'yaxis_title': "Categorías de Respuesta",
            'yaxis': {'categoryorder': 'total ascending'}  # Ordenar por valores
        }
        
        # Agregar título con icono si se proporciona
        if title_with_icon:
            layout_updates['title'] = {
                'text': title_with_icon,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            }
        
        fig.update_layout(**layout_updates)
        
        return fig
        
    except Exception as e:
        print(f"Error convirtiendo a horizontal: {e}")
        return fig

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Cárnicos y Huevos",
    page_icon="🍖",
    layout="wide"
)

# Título y descripción
st.title("🍖 Análisis de Satisfacción - Cárnicos y Huevos")
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

# Sidebar con iconos
st.sidebar.title("🔧 Filtros (Desactivados)")

# Intentar obtener el rango de fechas del state
if 'fecha' in df.columns:
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    valid_dates = df.dropna(subset=['fecha'])
    
    if not valid_dates.empty:
        min_date = valid_dates['fecha'].min().date()
        max_date = valid_dates['fecha'].max().date()
        
        date_range = st.sidebar.date_input(
            "📅 Rango de fechas (Desactivado)",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

# Filtro por ubicación geográfica (desactivados)
if 'comuna' in df.columns:
    all_comunas = ["Todas"] + sorted([str(x) for x in df['comuna'].unique() if pd.notna(x)])
    selected_comuna = st.sidebar.selectbox("🏘️ Comuna (Desactivado)", all_comunas)

if 'barrio' in df.columns:
    all_barrios = ["Todos"] + sorted([str(x) for x in df['barrio'].unique() if pd.notna(x)])
    selected_barrio = st.sidebar.selectbox("🏠 Barrio (Desactivado)", all_barrios)

if 'nodo' in df.columns:
    all_nodos = ["Todos"] + sorted([str(x) for x in df['nodo'].unique() if pd.notna(x)])
    selected_nodo = st.sidebar.selectbox("📍 Nodo (Desactivado)", all_nodos)

# Información sobre filtros desactivados
st.sidebar.info("ℹ️ Los filtros están desactivados temporalmente para mostrar todos los datos disponibles.")

# NO aplicar filtros - Usar el DataFrame completo
filtered_df = df.copy()  # Usar todos los datos sin filtrar

# Mostrar número de encuestas
st.sidebar.metric("📊 Total de encuestas", len(filtered_df))

# Mapeo de las columnas de cárnicos y huevos con iconos
carnicos_cols = {
    '12carnes_bien_etiquetadas': {
        'description': 'Las carnes se encuentran bien etiquetadas (peso, fechas, tipo de corte)',
        'icon': '🏷️',
        'title_with_icon': '🏷️ Etiquetado de Carnes'
    },
    '13producto_congelado': {
        'description': 'El producto se encuentra congelado al momento de recibirlo',
        'icon': '🧊',
        'title_with_icon': '🧊 Estado de Congelación'
    },
    '14corte_recibido': {
        'description': 'El corte del producto recibido es el mismo que aparece en la etiqueta',
        'icon': '🔪',
        'title_with_icon': '🔪 Correspondencia del Corte'
    },
    '15fecha_vencimiento_adecuada': {
        'description': 'La fecha de vencimiento es adecuada para la preparación',
        'icon': '📅',
        'title_with_icon': '📅 Fecha de Vencimiento Adecuada'
    },
    '16empacado_al_vacio': {
        'description': 'El producto está empacado al vacío',
        'icon': '📦',
        'title_with_icon': '📦 Empacado al Vacío'
    },
    '17estado_huevo': {
        'description': 'Estado de los huevos recibidos',
        'icon': '🥚',
        'title_with_icon': '🥚 Estado de los Huevos'
    },
    '18panal_de_huevo_etiquetado': {
        'description': 'El panal de huevos se encuentra etiquetado con fecha vencimiento',
        'icon': '📋',
        'title_with_icon': '📋 Etiquetado del Panal de Huevos'
    }
}

# Análisis de satisfacción por pregunta
st.header("📊 Satisfacción con Cárnicos y Huevos")

# Comprobar si existen las columnas
available_cols = [col for col in carnicos_cols.keys() if col in filtered_df.columns]

if not available_cols:
    st.warning("No se encontraron datos de satisfacción con cárnicos y huevos en la encuesta.")
    st.stop()

# Crear tabs para diferentes categorías
carnes_tab, huevos_tab = st.tabs(["🥩 Cárnicos", "🥚 Huevos"])

# Columnas de cárnicos
carnes_cols = ['12carnes_bien_etiquetadas', '13producto_congelado', '14corte_recibido', 
               '15fecha_vencimiento_adecuada', '16empacado_al_vacio']
carnes_available = [col for col in carnes_cols if col in available_cols]

with carnes_tab:
    if carnes_available:
        st.subheader("🥩 Satisfacción con Cárnicos")
        
        # Mostrar gráficos en grid
        for i in range(0, len(carnes_available), 2):
            col1, col2 = st.columns(2)
            
            # Primera columna
            col_info = carnicos_cols[carnes_available[i]]
            fig1 = plot_question_satisfaction(filtered_df, carnes_available[i], col_info['description'])
            if fig1:
                fig1_horizontal = make_horizontal_chart(fig1, col_info['title_with_icon'])
                col1.plotly_chart(fig1_horizontal, use_container_width=True)
            else:
                col1.info(f"No hay datos suficientes para '{col_info['description']}'")
            
            # Segunda columna (si existe)
            if i + 1 < len(carnes_available):
                col_info2 = carnicos_cols[carnes_available[i+1]]
                fig2 = plot_question_satisfaction(filtered_df, carnes_available[i+1], col_info2['description'])
                if fig2:
                    fig2_horizontal = make_horizontal_chart(fig2, col_info2['title_with_icon'])
                    col2.plotly_chart(fig2_horizontal, use_container_width=True)
                else:
                    col2.info(f"No hay datos suficientes para '{col_info2['description']}'")
    else:
        st.info("No se encontraron datos de satisfacción con cárnicos en la encuesta.")

# Columnas de huevos
huevos_cols = ['17estado_huevo', '18panal_de_huevo_etiquetado']
huevos_available = [col for col in huevos_cols if col in available_cols]

with huevos_tab:
    if huevos_available:
        st.subheader("🥚 Satisfacción con Huevos")
        
        # Mostrar gráficos en columnas
        col1, col2 = st.columns(2)
        
        # Primera columna (si existe)
        if len(huevos_available) > 0:
            col_info = carnicos_cols[huevos_available[0]]
            fig1 = plot_question_satisfaction(filtered_df, huevos_available[0], col_info['description'])
            if fig1:
                fig1_horizontal = make_horizontal_chart(fig1, col_info['title_with_icon'])
                col1.plotly_chart(fig1_horizontal, use_container_width=True)
            else:
                col1.info(f"No hay datos suficientes para '{col_info['description']}'")
        
        # Segunda columna (si existe)
        if len(huevos_available) > 1:
            col_info2 = carnicos_cols[huevos_available[1]]
            fig2 = plot_question_satisfaction(filtered_df, huevos_available[1], col_info2['description'])
            if fig2:
                fig2_horizontal = make_horizontal_chart(fig2, col_info2['title_with_icon'])
                col2.plotly_chart(fig2_horizontal, use_container_width=True)
            else:
                col2.info(f"No hay datos suficientes para '{col_info2['description']}'")
    else:
        st.info("No se encontraron datos de satisfacción con huevos en la encuesta.")

# Análisis de Comedores con Insatisfacción
st.header("⚠️ Comedores con Niveles de Insatisfacción")

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
                
                comedores_insatisfechos[comedor][carnicos_cols[col]['description']] = count
    
    # Mostrar resultados
    if comedores_insatisfechos:
        # Convertir a DataFrame para mejor visualización
        resultado_df = pd.DataFrame.from_dict(comedores_insatisfechos, orient='index')
        
        # Reemplazar NaN con 0
        resultado_df = resultado_df.fillna(0)
        
        # Agregar columna de total
        resultado_df['📊 Total Insatisfacciones'] = resultado_df.sum(axis=1)
        
        # Ordenar por total de insatisfacciones (descendente)
        resultado_df = resultado_df.sort_values('📊 Total Insatisfacciones', ascending=False)
        
        # Mostrar como tabla
        st.write("🍽️ Comedores con reportes de insatisfacción en cárnicos y huevos:")
        st.dataframe(resultado_df, use_container_width=True)
        
        # Conclusión textual sobre comedores con insatisfacciones
        st.subheader("🎯 Comedores con problemas de insatisfacción")
        
        # Tomar los primeros comedores (los más problemáticos)
        top_comedores = resultado_df.head(5)
        
        # Crear conclusión textual
        st.markdown("### 📈 Resumen de hallazgos")
        
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
                if aspecto != '📊 Total Insatisfacciones' and valor > 0:
                    aspectos_insatisfechos.append(aspecto)
            
            aspectos_texto = ", ".join(aspectos_insatisfechos)
            st.markdown(f"""
            - **🏪 {comedor}**: {int(row['📊 Total Insatisfacciones'])} reportes de insatisfacción.
              **Aspectos problemáticos:** {aspectos_texto}
            """)
        
        # Recomendaciones generales
        st.markdown("""
        ### 🎯 Recomendaciones
        
        Se sugiere implementar un plan de seguimiento especial para estos comedores, 
        con énfasis en los aspectos señalados como problemáticos. Es recomendable:
        
        1. 🔍 **Revisar con los proveedores** de cárnicos los estándares de calidad, especialmente para estos comedores
        2. 🧊 **Verificar la cadena de frío** durante el transporte a estas ubicaciones
        3. ✅ **Implementar un protocolo de inspección** especial para los productos destinados a estos comedores
        4. 🥚 **Realizar seguimiento** a la calidad de los huevos, verificando su frescura y correcto etiquetado
        """)
    else:
        st.success("✅ No se encontraron comedores con reportes de insatisfacción en cárnicos y huevos.")

# Conclusiones y recomendaciones
st.header("💡 Conclusiones y Recomendaciones")

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
    
    # Obtener información con iconos
    min_info = carnicos_cols[min_aspect]
    max_info = carnicos_cols[max_aspect]
    
    # Mostrar conclusiones
    st.markdown(f"""
    📈 **Basado en el análisis de los datos:**
    
    - 🏆 El aspecto con **mayor satisfacción** es "{max_info['icon']} {max_info['description']}" con un puntaje promedio de **{max_score:.2f}/5**.
    - ⚠️ El aspecto con **menor satisfacción** es "{min_info['icon']} {min_info['description']}" con un puntaje promedio de **{min_score:.2f}/5**.
    
    **🎯 Recomendaciones:**
    
    - 🔧 Revisar los procesos relacionados con "{min_info['icon']} {min_info['description']}"
    - 💪 Fortalecer los controles de calidad para cárnicos y huevos
    - 🔄 Evaluar la posibilidad de cambiar proveedores si los problemas persisten
    - ✅ Mantener las buenas prácticas relacionadas con "{max_info['icon']} {max_info['description']}"
    """)
else:
    st.info("ℹ️ No hay datos suficientes para generar conclusiones y recomendaciones.")

# Footer
st.markdown("---")
st.markdown("📊 Dashboard de Análisis de la Encuesta de Satisfacción | 🍖 Sección: Cárnicos y Huevos")
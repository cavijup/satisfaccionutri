import streamlit as st
import pandas as pd
# Eliminar 'get_filtered_data' de la importación
from utils.data_loader import load_data
from utils.data_processing import (
    plot_question_satisfaction,
    COL_DESCRIPTIONS # Asegúrate que COL_DESCRIPTIONS esté definido en data_processing.py
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
incluyendo aspectos como etiquetado, estado de congelación, corte y empaque, basado en **todos los datos recolectados**.
""")

# Cargar datos
# @st.cache_data(show_spinner="Cargando datos...") # No cachear aquí si Home.py ya lo hace
def get_data():
    df_page = load_data()
    return df_page

df = get_data() # Usar 'df' directamente

if df is None or df.empty:
    st.error("2_Carnicos_Huevos.py: No se pudieron cargar los datos iniciales desde load_data().")
    st.stop()

# --- Barra Lateral (Solo navegación y métrica total) ---
st.sidebar.title("Navegación")
# st.sidebar.info("...") # Puedes añadir información aquí si quieres
st.sidebar.metric("Total de encuestas analizadas", len(df)) # Mostrar total de registros

# --- SECCIÓN DE FILTROS ELIMINADA ---
# Ya no se definen los widgets de filtro aquí
# Ya no se llama a get_filtered_data

# --- Contenido de la Página (Siempre usa 'df') ---
print(f"INFO 2_Carnicos_Huevos.py: Mostrando contenido con {len(df)} filas (sin filtros).")

# Mapeo de las columnas de cárnicos y huevos
# Usar COL_DESCRIPTIONS importado de data_processing
carnicos_huevos_cols_map = {
    '12carnes_bien_etiquetadas': COL_DESCRIPTIONS.get('12carnes_bien_etiquetadas', 'Etiquetado carnes'),
    '13producto_congelado': COL_DESCRIPTIONS.get('13producto_congelado', 'Producto congelado'),
    '14corte_recibido': COL_DESCRIPTIONS.get('14corte_recibido', 'Corte recibido'),
    '15fecha_vencimiento_adecuada': COL_DESCRIPTIONS.get('15fecha_vencimiento_adecuada', 'Fecha vencimiento adecuada'),
    '16empacado_al_vacio': COL_DESCRIPTIONS.get('16empacado_al_vacio', 'Empacado al vacío'),
    '17estado_huevo': COL_DESCRIPTIONS.get('17estado_huevo', 'Estado huevos'),
    '18panal_de_huevo_etiquetado': COL_DESCRIPTIONS.get('18panal_de_huevo_etiquetado', 'Etiquetado panal huevos')
}


# Análisis de satisfacción por pregunta
st.header("Satisfacción con Cárnicos y Huevos (Global)")

# Comprobar si existen las columnas y tienen datos válidos
valid_display_cols = []
for col_key in carnicos_huevos_cols_map.keys():
    label_col = col_key + '_label'
    if label_col in df.columns and df[label_col].notna().any():
        valid_display_cols.append(col_key)
    elif col_key in df.columns and pd.api.types.is_numeric_dtype(df[col_key].dtype) and df[col_key].notna().any():
        valid_display_cols.append(col_key)
        print(f"WARN 2_Carnicos_Huevos.py: Usando columna numérica '{col_key}' porque '{label_col}' falta o está vacía.")

if not valid_display_cols:
    st.warning("No se encontraron datos de satisfacción válidos para Cárnicos y Huevos.")
    st.stop()

# Crear tabs para diferentes categorías
carnes_tab, huevos_tab = st.tabs(["Cárnicos", "Huevos"])

# Columnas de cárnicos
carnes_cols_keys = ['12carnes_bien_etiquetadas', '13producto_congelado', '14corte_recibido',
                   '15fecha_vencimiento_adecuada', '16empacado_al_vacio']
carnes_available = [col for col in carnes_cols_keys if col in valid_display_cols]

with carnes_tab:
    if carnes_available:
        st.subheader("Satisfacción con Cárnicos")
        num_cols_carnes = 2
        cols_layout_carnes = st.columns(num_cols_carnes)
        col_index_carnes = 0
        for col_key in carnes_available:
            col_description = carnicos_huevos_cols_map[col_key]
            with cols_layout_carnes[col_index_carnes % num_cols_carnes]:
                try:
                    # Usar el DataFrame completo 'df'
                    fig = plot_question_satisfaction(df, col_key, col_description)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"No hay datos suficientes para '{col_description}'")
                except Exception as e_plot:
                     st.error(f"Error al graficar '{col_description}': {e_plot}")
                     print(f"ERROR 2_Carnicos_Huevos.py - plot_question_satisfaction para '{col_key}': {e_plot}")
            col_index_carnes += 1
    else:
        st.info("No se encontraron datos de satisfacción con cárnicos.")

# Columnas de huevos
huevos_cols_keys = ['17estado_huevo', '18panal_de_huevo_etiquetado']
huevos_available = [col for col in huevos_cols_keys if col in valid_display_cols]

with huevos_tab:
    if huevos_available:
        st.subheader("Satisfacción con Huevos")
        num_cols_huevos = 2
        cols_layout_huevos = st.columns(num_cols_huevos)
        col_index_huevos = 0
        for col_key in huevos_available:
            col_description = carnicos_huevos_cols_map[col_key]
            with cols_layout_huevos[col_index_huevos % num_cols_huevos]:
                try:
                     # Usar el DataFrame completo 'df'
                    fig = plot_question_satisfaction(df, col_key, col_description)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"No hay datos suficientes para '{col_description}'")
                except Exception as e_plot:
                     st.error(f"Error al graficar '{col_description}': {e_plot}")
                     print(f"ERROR 2_Carnicos_Huevos.py - plot_question_satisfaction para '{col_key}': {e_plot}")
            col_index_huevos += 1
    else:
        st.info("No se encontraron datos de satisfacción con huevos.")

# Análisis de Comedores con Insatisfacción
st.header("Comedores con Niveles de Insatisfacción (Global)")

# Verificar columnas necesarias
id_comedor_candidates = ['nombre_comedor', 'comedor', 'id_comedor', 'nombre del comedor']
id_comedor_col = next((col for col in id_comedor_candidates if col in df.columns), None)
# Usar las columnas que son numéricas después del procesamiento
satisfaction_numeric_cols = [col for col in carnicos_huevos_cols_map.keys() if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]


if not satisfaction_numeric_cols:
    st.warning("No se encontraron datos numéricos de satisfacción con cárnicos/huevos para analizar.")
elif not id_comedor_col:
    st.warning("No se encontró columna de identificación del comedor.")
else:
    print(f"DEBUG 2_Carnicos_Huevos.py: Analizando insatisfacción (global). ID Comedor: '{id_comedor_col}', Columnas numéricas: {satisfaction_numeric_cols}")
    try:
        # Usar el DataFrame completo 'df'
        analisis_df = df[[id_comedor_col] + satisfaction_numeric_cols].copy()
        for col in satisfaction_numeric_cols:
            analisis_df[col] = pd.to_numeric(analisis_df[col], errors='coerce')

        # Función para identificar valores de insatisfacción (puntaje <= 2)
        def es_insatisfecho_numeric(valor):
             if pd.isna(valor): return False
             return valor <= 2

        # Identificar filas con insatisfacción
        # Aplicar a cada columna numérica y ver si alguna es True para la fila
        insatisfaccion_mask = analisis_df[satisfaction_numeric_cols].apply(lambda row: row.apply(es_insatisfecho_numeric).any(), axis=1)


        if not insatisfaccion_mask.any():
            st.success("No se encontraron reportes de insatisfacción (puntaje <= 2) para Cárnicos/Huevos.")
        else:
            insatisfechos_df = analisis_df[insatisfaccion_mask]
            print(f"DEBUG 2_Carnicos_Huevos.py: {len(insatisfechos_df)} filas totales con insatisfacción.")

            # Crear tabla resumen
            comedor_insatisfaccion_detalle = {}
            for idx, row in insatisfechos_df.iterrows():
                comedor_nombre = row[id_comedor_col]
                if comedor_nombre not in comedor_insatisfaccion_detalle:
                    comedor_insatisfaccion_detalle[comedor_nombre] = {'count': 0, 'aspects': set()}
                comedor_insatisfaccion_detalle[comedor_nombre]['count'] += 1
                for col in satisfaction_numeric_cols:
                    if es_insatisfecho_numeric(row[col]):
                        comedor_insatisfaccion_detalle[comedor_nombre]['aspects'].add(carnicos_huevos_cols_map.get(col, col))

            # Convertir a DataFrame para mostrar
            resultado_lista = []
            for comedor, data in comedor_insatisfaccion_detalle.items():
                resultado_lista.append({
                    'Comedor': comedor,
                    'Número de Reportes con Insatisfacción': data['count'],
                    'Aspectos Problemáticos': ', '.join(sorted(list(data['aspects'])))
                })

            if resultado_lista:
                resultado_display_df = pd.DataFrame(resultado_lista)
                st.write("Comedores con al menos un reporte de insatisfacción (puntaje <= 2) en Cárnicos/Huevos (Global):")
                st.dataframe(resultado_display_df.sort_values('Número de Reportes con Insatisfacción', ascending=False),
                             hide_index=True, use_container_width=True)
            else: # Esto no debería ocurrir si insatisfaccion_mask.any() fue True, pero por seguridad
                 st.success("No se encontraron reportes de insatisfacción (puntaje <= 2) para Cárnicos/Huevos.")


    except Exception as e_insat:
        st.error(f"Error analizando comedores insatisfechos: {e_insat}")
        print(f"ERROR 2_Carnicos_Huevos.py - Análisis Insatisfacción: {e_insat}")


# Conclusiones y recomendaciones
st.header("Conclusiones y Recomendaciones (Global - Cárnicos y Huevos)")

# Usar 'valid_display_cols' que ya verificó si hay datos
if valid_display_cols:
    try:
        # Calcular promedios de satisfacción usando el df completo
        satisfaction_means = {}
        valid_cols_for_mean = [col for col in carnicos_huevos_cols_map.keys() if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]

        if valid_cols_for_mean:
             for col in valid_cols_for_mean:
                 numeric_data = pd.to_numeric(df[col], errors='coerce')
                 if numeric_data.notna().any():
                     satisfaction_means[col] = numeric_data.mean()

        if satisfaction_means:
             min_aspect_col = min(satisfaction_means, key=satisfaction_means.get)
             min_score = satisfaction_means[min_aspect_col]
             max_aspect_col = max(satisfaction_means, key=satisfaction_means.get)
             max_score = satisfaction_means[max_aspect_col]

             min_desc = carnicos_huevos_cols_map.get(min_aspect_col, min_aspect_col)
             max_desc = carnicos_huevos_cols_map.get(max_aspect_col, max_aspect_col)

             st.markdown(f"""
             Basado en el análisis de **todos** los datos:

             - El aspecto con **mayor satisfacción** global es "{max_desc}" ({max_score:.2f}/5).
             - El aspecto con **menor satisfacción** global es "{min_desc}" ({min_score:.2f}/5).

             **Recomendaciones Generales:**
             - Investigar las causas de la menor satisfacción en "{min_desc}".
             - Reforzar las prácticas relacionadas con "{max_desc}".
             - Fortalecer controles de calidad y cadena de frío para cárnicos y huevos.
             """)
        else:
             st.info("No hay datos numéricos de satisfacción suficientes para generar conclusiones.")
    except Exception as e_conclu:
        st.error(f"Error generando conclusiones: {e_conclu}")
        print(f"ERROR 2_Carnicos_Huevos.py - Conclusiones: {e_conclu}")
else:
    # Esto se maneja arriba con st.warning si no hay 'valid_display_cols'
    pass

# Footer
st.markdown("---")
st.markdown("Dashboard de Análisis de la Encuesta de Satisfacción | Sección: Cárnicos y Huevos")
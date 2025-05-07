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
    page_title="Análisis de Frutas y Verduras",
    page_icon="🥕",
    layout="wide"
)

# Título y descripción
st.title("Análisis de Satisfacción - Frutas y Verduras")
st.markdown("""
Esta sección presenta el análisis detallado de la satisfacción con las frutas, verduras, hortalizas y tubérculos entregados,
incluyendo aspectos como frescura, maduración, calidad y estado de los productos, basado en **todos los datos recolectados**.
""")

# --- Carga de Datos ---
# @st.cache_data(show_spinner="Cargando datos...") # No cachear aquí si Home.py ya lo hace
def get_data():
    df_page = load_data()
    return df_page

df = get_data() # Usar 'df' directamente

if df is None or df.empty:
    st.error("3_Frutas_Verduras.py: No se pudieron cargar los datos iniciales desde load_data().")
    st.stop()

# --- Barra Lateral (Solo navegación y métrica total) ---
st.sidebar.title("Navegación")
st.sidebar.metric("Total de encuestas analizadas", len(df)) # Mostrar total de registros

# --- SECCIÓN DE FILTROS ELIMINADA ---

# --- Contenido de la Página (Siempre usa 'df') ---
print(f"INFO 3_Frutas_Verduras.py: Mostrando contenido con {len(df)} filas (sin filtros).")

# Mapeo de las columnas de frutas y verduras
# Usar COL_DESCRIPTIONS importado de data_processing
frutas_verduras_cols_map = {
    '19frutas': COL_DESCRIPTIONS.get('19frutas', 'Estado y calidad de las frutas'),
    '20verduras': COL_DESCRIPTIONS.get('20verduras', 'Estado y calidad de las verduras'),
    '21hortalizas': COL_DESCRIPTIONS.get('21hortalizas', 'Estado y calidad de las hortalizas'),
    '22tuberculos': COL_DESCRIPTIONS.get('22tuberculos', 'Estado y calidad de los tubérculos')
}

# Análisis de satisfacción por pregunta
st.header("Satisfacción con Frutas y Verduras (Global)")

# Comprobar si existen las columnas y tienen datos válidos
valid_display_cols = []
for col_key in frutas_verduras_cols_map.keys():
    label_col = col_key + '_label'
    if label_col in df.columns and df[label_col].notna().any():
        valid_display_cols.append(col_key)
    elif col_key in df.columns and pd.api.types.is_numeric_dtype(df[col_key].dtype) and df[col_key].notna().any():
        valid_display_cols.append(col_key)
        print(f"WARN 3_Frutas_Verduras.py: Usando columna numérica '{col_key}' porque '{label_col}' falta o está vacía.")

if not valid_display_cols:
    st.warning("No se encontraron datos de satisfacción válidos para Frutas y Verduras.")
    st.stop()

# Crear tabs para diferentes categorías (si quieres mantenerlas)
# O mostrarlos directamente si prefieres
frutas_tab, verduras_tab, hortalizas_tab, tuberculos_tab = st.tabs(["Frutas", "Verduras", "Hortalizas", "Tubérculos"])

# Columnas por tab
tabs_cols = {
    frutas_tab: ['19frutas'],
    verduras_tab: ['20verduras'],
    hortalizas_tab: ['21hortalizas'],
    tuberculos_tab: ['22tuberculos']
}

for tab, cols_keys in tabs_cols.items():
    with tab:
        tab_available_cols = [col for col in cols_keys if col in valid_display_cols]
        if tab_available_cols:
            # st.subheader(f"Satisfacción con {tab.label}") # El título del tab ya lo indica
            num_cols_tab = 1 # Mostrar un gráfico por tab en este caso
            cols_layout_tab = st.columns(num_cols_tab)
            col_index_tab = 0
            for col_key in tab_available_cols:
                col_description = frutas_verduras_cols_map[col_key]
                with cols_layout_tab[col_index_tab % num_cols_tab]:
                    try:
                         # Usar el DataFrame completo 'df'
                        fig = plot_question_satisfaction(df, col_key, col_description)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info(f"No hay datos suficientes para '{col_description}'")
                    except Exception as e_plot:
                        st.error(f"Error al graficar '{col_description}': {e_plot}")
                        print(f"ERROR 3_Frutas_Verduras.py - plot_question_satisfaction para '{col_key}': {e_plot}")
                col_index_tab += 1
        else:
            st.info(f"No se encontraron datos de satisfacción para esta categoría.")


# Análisis de Comedores con Insatisfacción
st.header("Comedores con Niveles de Insatisfacción (Global)")

# Verificar columnas necesarias
id_comedor_candidates = ['nombre_comedor', 'comedor', 'id_comedor', 'nombre del comedor']
id_comedor_col = next((col for col in id_comedor_candidates if col in df.columns), None)
# Usar las columnas que son numéricas después del procesamiento
satisfaction_numeric_cols = [col for col in frutas_verduras_cols_map.keys() if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]


if not satisfaction_numeric_cols:
    st.warning("No se encontraron datos numéricos de satisfacción con frutas/verduras para analizar.")
elif not id_comedor_col:
    st.warning("No se encontró columna de identificación del comedor.")
else:
    print(f"DEBUG 3_Frutas_Verduras.py: Analizando insatisfacción (global). ID Comedor: '{id_comedor_col}', Columnas numéricas: {satisfaction_numeric_cols}")
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
        insatisfaccion_mask = analisis_df[satisfaction_numeric_cols].apply(lambda row: row.apply(es_insatisfecho_numeric).any(), axis=1)


        if not insatisfaccion_mask.any():
            st.success("No se encontraron reportes de insatisfacción (puntaje <= 2) para Frutas/Verduras.")
        else:
            insatisfechos_df = analisis_df[insatisfaccion_mask]
            print(f"DEBUG 3_Frutas_Verduras.py: {len(insatisfechos_df)} filas totales con insatisfacción.")

            # Crear tabla resumen
            comedor_insatisfaccion_detalle = {}
            for idx, row in insatisfechos_df.iterrows():
                comedor_nombre = row[id_comedor_col]
                if comedor_nombre not in comedor_insatisfaccion_detalle:
                    comedor_insatisfaccion_detalle[comedor_nombre] = {'count': 0, 'aspects': set()}
                comedor_insatisfaccion_detalle[comedor_nombre]['count'] += 1
                for col in satisfaction_numeric_cols:
                    if es_insatisfecho_numeric(row[col]):
                        comedor_insatisfaccion_detalle[comedor_nombre]['aspects'].add(frutas_verduras_cols_map.get(col, col))

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
                st.write("Comedores con al menos un reporte de insatisfacción (puntaje <= 2) en Frutas/Verduras (Global):")
                st.dataframe(resultado_display_df.sort_values('Número de Reportes con Insatisfacción', ascending=False),
                             hide_index=True, use_container_width=True)
            else:
                 st.success("No se encontraron reportes de insatisfacción (puntaje <= 2) para Frutas/Verduras.")

    except Exception as e_insat:
        st.error(f"Error analizando comedores insatisfechos: {e_insat}")
        print(f"ERROR 3_Frutas_Verduras.py - Análisis Insatisfacción: {e_insat}")


# Conclusiones y recomendaciones
st.header("Conclusiones y Recomendaciones (Global - Frutas y Verduras)")

# Usar 'valid_display_cols' que ya verificó si hay datos
if valid_display_cols:
    try:
        # Calcular promedios de satisfacción usando el df completo
        satisfaction_means = {}
        valid_cols_for_mean = [col for col in frutas_verduras_cols_map.keys() if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]

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

             min_desc = frutas_verduras_cols_map.get(min_aspect_col, min_aspect_col)
             max_desc = frutas_verduras_cols_map.get(max_aspect_col, max_aspect_col)

             st.markdown(f"""
             Basado en el análisis de **todos** los datos:

             - El aspecto con **mayor satisfacción** global es "{max_desc}" ({max_score:.2f}/5).
             - El aspecto con **menor satisfacción** global es "{min_desc}" ({min_score:.2f}/5).

             **Recomendaciones Generales:**
             - Investigar las causas de la menor satisfacción en "{min_desc}" (calidad, frescura, variedad).
             - Reforzar las buenas prácticas relacionadas con "{max_desc}".
             - Evaluar la cadena de suministro y almacenamiento de productos frescos.
             """)
        else:
             st.info("No hay datos numéricos de satisfacción suficientes para generar conclusiones.")
    except Exception as e_conclu:
        st.error(f"Error generando conclusiones: {e_conclu}")
        print(f"ERROR 3_Frutas_Verduras.py - Conclusiones: {e_conclu}")
else:
    # Esto se maneja arriba con st.warning si no hay 'valid_display_cols'
    pass

# Footer
st.markdown("---")
st.markdown("Dashboard de Análisis de la Encuesta de Satisfacción | Sección: Frutas y Verduras")
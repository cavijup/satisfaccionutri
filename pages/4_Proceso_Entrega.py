import streamlit as st
import pandas as pd
# Eliminar 'get_filtered_data' de la importación
from utils.data_loader import load_data
from utils.data_processing import (
    plot_question_satisfaction,
    plot_yes_no_questions,
    plot_complexity_analysis,
    COL_DESCRIPTIONS # Asegúrate que COL_DESCRIPTIONS esté definido en data_processing.py
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
incluyendo aspectos como ciclo de menús, notificación, tiempos de revisión y atención del personal,
basado en **todos los datos recolectados**.
""")

# --- Carga de Datos ---
# @st.cache_data(show_spinner="Cargando datos...") # No cachear aquí si Home.py ya lo hace
def get_data():
    df_page = load_data()
    return df_page

df = get_data() # Usar 'df' directamente

if df is None or df.empty:
    st.error("4_Proceso_Entrega.py: No se pudieron cargar los datos iniciales desde load_data().")
    st.stop()

# --- Barra Lateral (Solo navegación y métrica total) ---
st.sidebar.title("Navegación")
st.sidebar.metric("Total de encuestas analizadas", len(df)) # Mostrar total de registros

# --- SECCIÓN DE FILTROS ELIMINADA ---

# --- Contenido de la Página (Siempre usa 'df') ---
print(f"INFO 4_Proceso_Entrega.py: Mostrando contenido con {len(df)} filas (sin filtros).")

# Mapeo de las columnas del proceso de entrega
# Usar COL_DESCRIPTIONS importado de data_processing
entrega_cols_map = {
    '23ciclo_menus': COL_DESCRIPTIONS.get('23ciclo_menus', 'Ciclo de menús'),
    '24notificacion_telefonica': COL_DESCRIPTIONS.get('24notificacion_telefonica', 'Notificación telefónica'),
    '25tiempo_revision_alimentos': COL_DESCRIPTIONS.get('25tiempo_revision_alimentos', 'Tiempo revisión alimentos'),
    '26tiempo_entrega_mercdos': COL_DESCRIPTIONS.get('26tiempo_entrega_mercdos', 'Tiempo entre entregas'),
    '27tiempo_demora_proveedor': COL_DESCRIPTIONS.get('27tiempo_demora_proveedor', 'Tiempo respuesta proveedor'),
    '28actitud_funcionario_logistico': COL_DESCRIPTIONS.get('28actitud_funcionario_logistico', 'Actitud funcionario')
}

# Análisis de satisfacción por aspectos del proceso
st.header("Satisfacción con el Proceso de Entrega (Global)")

# Comprobar si existen las columnas y tienen datos válidos
valid_display_cols = []
for col_key in entrega_cols_map.keys():
    label_col = col_key + '_label'
    if label_col in df.columns and df[label_col].notna().any():
        valid_display_cols.append(col_key)
    elif col_key in df.columns and pd.api.types.is_numeric_dtype(df[col_key].dtype) and df[col_key].notna().any():
        valid_display_cols.append(col_key)
        print(f"WARN 4_Proceso_Entrega.py: Usando columna numérica '{col_key}' porque '{label_col}' falta o está vacía.")

if not valid_display_cols:
    st.warning("No se encontraron datos de satisfacción válidos para el Proceso de Entrega.")
    st.stop()

# Crear tabs para diferentes aspectos del proceso
logistica_tab, tiempos_tab, personal_tab = st.tabs(["Logística", "Tiempos", "Personal"])

# Columnas para cada tab
logistica_cols_keys = ['23ciclo_menus', '24notificacion_telefonica']
tiempos_cols_keys = ['25tiempo_revision_alimentos', '26tiempo_entrega_mercdos', '27tiempo_demora_proveedor']
personal_cols_keys = ['28actitud_funcionario_logistico']

with logistica_tab:
    logistica_available = [col for col in logistica_cols_keys if col in valid_display_cols]
    if logistica_available:
        st.subheader("Satisfacción con Aspectos Logísticos")
        num_cols_log = 2
        cols_layout_log = st.columns(num_cols_log)
        col_index_log = 0
        for col_key in logistica_available:
            col_description = entrega_cols_map[col_key]
            with cols_layout_log[col_index_log % num_cols_log]:
                try:
                    # Usar el DataFrame completo 'df'
                    fig = plot_question_satisfaction(df, col_key, col_description)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"No hay datos suficientes para '{col_description}'")
                except Exception as e_plot:
                    st.error(f"Error al graficar '{col_description}': {e_plot}")
                    print(f"ERROR 4_Proceso_Entrega.py - plot_question_satisfaction para '{col_key}': {e_plot}")
            col_index_log += 1
    else:
        st.info("No se encontraron datos de satisfacción con aspectos logísticos.")

with tiempos_tab:
    tiempos_available = [col for col in tiempos_cols_keys if col in valid_display_cols]
    if tiempos_available:
        st.subheader("Satisfacción con Tiempos")
        num_cols_tiempos = min(len(tiempos_available), 2) # Mostrar hasta 2 por fila
        cols_layout_tiempos = st.columns(num_cols_tiempos)
        col_index_tiempos = 0
        for col_key in tiempos_available:
            col_description = entrega_cols_map[col_key]
            with cols_layout_tiempos[col_index_tiempos % num_cols_tiempos]:
                try:
                    # Usar el DataFrame completo 'df'
                    fig = plot_question_satisfaction(df, col_key, col_description)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"No hay datos suficientes para '{col_description}'")
                except Exception as e_plot:
                    st.error(f"Error al graficar '{col_description}': {e_plot}")
                    print(f"ERROR 4_Proceso_Entrega.py - plot_question_satisfaction para '{col_key}': {e_plot}")
            col_index_tiempos += 1
    else:
        st.info("No se encontraron datos de satisfacción con tiempos.")

with personal_tab:
    personal_available = [col for col in personal_cols_keys if col in valid_display_cols]
    if personal_available:
        st.subheader("Satisfacción con el Personal")
        num_cols_pers = 1 # Mostrar uno solo
        cols_layout_pers = st.columns(num_cols_pers)
        col_index_pers = 0
        for col_key in personal_available:
            col_description = entrega_cols_map[col_key]
            with cols_layout_pers[col_index_pers % num_cols_pers]:
                try:
                    # Usar el DataFrame completo 'df'
                    fig = plot_question_satisfaction(df, col_key, col_description)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"No hay datos suficientes para '{col_description}'")
                except Exception as e_plot:
                     st.error(f"Error al graficar '{col_description}': {e_plot}")
                     print(f"ERROR 4_Proceso_Entrega.py - plot_question_satisfaction para '{col_key}': {e_plot}")
            col_index_pers += 1
    else:
        st.info("No se encontraron datos de satisfacción con el personal.")

# Análisis de preguntas sí/no
st.header("Cumplimiento y Comunicación (Global)")
try:
    yes_no_fig = plot_yes_no_questions(df) # Usar df completo
    if yes_no_fig:
        st.plotly_chart(yes_no_fig, use_container_width=True)
    else:
        st.info("No hay datos suficientes para el análisis de preguntas sí/no.")
except Exception as e_yesno:
    st.error(f"Error al graficar preguntas Sí/No: {e_yesno}")
    print(f"ERROR 4_Proceso_Entrega.py - plot_yes_no_questions: {e_yesno}")


# Análisis de complejidad del proceso
st.header("Percepción de Complejidad del Proceso (Global)")
try:
    complexity_fig = plot_complexity_analysis(df) # Usar df completo
    if complexity_fig:
        st.plotly_chart(complexity_fig, use_container_width=True)
    else:
        st.info("No hay datos suficientes para el análisis de complejidad.")
except Exception as e_complex:
    st.error(f"Error al graficar complejidad: {e_complex}")
    print(f"ERROR 4_Proceso_Entrega.py - plot_complexity_analysis: {e_complex}")


# Análisis de Comedores con Insatisfacción
st.header("Comedores con Niveles de Insatisfacción (Global)")

# Verificar columnas necesarias
id_comedor_candidates = ['nombre_comedor', 'comedor', 'id_comedor', 'nombre del comedor']
id_comedor_col = next((col for col in id_comedor_candidates if col in df.columns), None)
# Usar las columnas que son numéricas después del procesamiento
satisfaction_numeric_cols = [col for col in entrega_cols_map.keys() if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]

if not satisfaction_numeric_cols:
    st.warning("No se encontraron datos numéricos de satisfacción con el proceso de entrega para analizar.")
elif not id_comedor_col:
    st.warning("No se encontró columna de identificación del comedor.")
else:
    print(f"DEBUG 4_Proceso_Entrega.py: Analizando insatisfacción (global). ID Comedor: '{id_comedor_col}', Columnas numéricas: {satisfaction_numeric_cols}")
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
            st.success("No se encontraron reportes de insatisfacción (puntaje <= 2) para Proceso de Entrega.")
        else:
            insatisfechos_df = analisis_df[insatisfaccion_mask]
            print(f"DEBUG 4_Proceso_Entrega.py: {len(insatisfechos_df)} filas totales con insatisfacción.")

            # Crear tabla resumen
            comedor_insatisfaccion_detalle = {}
            for idx, row in insatisfechos_df.iterrows():
                comedor_nombre = row[id_comedor_col]
                if comedor_nombre not in comedor_insatisfaccion_detalle:
                    comedor_insatisfaccion_detalle[comedor_nombre] = {'count': 0, 'aspects': set()}
                comedor_insatisfaccion_detalle[comedor_nombre]['count'] += 1
                for col in satisfaction_numeric_cols:
                    if es_insatisfecho_numeric(row[col]):
                        comedor_insatisfaccion_detalle[comedor_nombre]['aspects'].add(entrega_cols_map.get(col, col))

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
                st.write("Comedores con al menos un reporte de insatisfacción (puntaje <= 2) en Proceso de Entrega (Global):")
                st.dataframe(resultado_display_df.sort_values('Número de Reportes con Insatisfacción', ascending=False),
                             hide_index=True, use_container_width=True)
            else:
                 st.success("No se encontraron reportes de insatisfacción (puntaje <= 2) para Proceso de Entrega.")

    except Exception as e_insat:
        st.error(f"Error analizando comedores insatisfechos: {e_insat}")
        print(f"ERROR 4_Proceso_Entrega.py - Análisis Insatisfacción: {e_insat}")


# Análisis de sugerencias de mejora
st.header("Sugerencias de Mejora (Global)")

sugestiones_col = '32aspectos_de_mejora' # Asegúrate que este es el nombre correcto de la columna
if sugestiones_col in df.columns:
    sugerencias = df[sugestiones_col].dropna().astype(str)
    sugerencias = sugerencias[sugerencias.str.strip().str.len() > 5] # Filtrar strings muy cortos

    if not sugerencias.empty:
        st.write(f"Se registraron {len(sugerencias)} sugerencias de mejora. Algunas de ellas:")
        # Mostrar algunas sugerencias textuales (ej. las 10 primeras no vacías)
        for i, sugerencia in enumerate(sugerencias.head(10), 1):
            st.markdown(f"- *{sugerencia.strip()}*")
        # Podrías añadir aquí un wordcloud si descomentas la importación y llamada a create_wordcloud
        # try:
        #     fig_wc, terms_wc = create_wordcloud(df, sugestiones_col)
        #     if fig_wc:
        #         st.pyplot(fig_wc)
        #     else:
        #         st.info("No se pudo generar la nube de palabras de sugerencias.")
        # except Exception as e_wc:
        #      st.error(f"Error generando nube de palabras: {e_wc}")

    else:
        st.info("No se han registrado sugerencias de mejora significativas.")
else:
    st.info(f"No se encontró la columna '{sugestiones_col}'.")


# Conclusiones y recomendaciones
st.header("Conclusiones y Recomendaciones (Global - Proceso Entrega)")

# Usar 'valid_display_cols' que ya verificó si hay datos
if valid_display_cols:
    try:
        # Calcular promedios de satisfacción usando el df completo
        satisfaction_means = {}
        valid_cols_for_mean = [col for col in entrega_cols_map.keys() if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]

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

             min_desc = entrega_cols_map.get(min_aspect_col, min_aspect_col)
             max_desc = entrega_cols_map.get(max_aspect_col, max_aspect_col)

             st.markdown(f"""
             Basado en el análisis de **todos** los datos:

             - El aspecto con **mayor satisfacción** global es "{max_desc}" ({max_score:.2f}/5).
             - El aspecto con **menor satisfacción** global es "{min_desc}" ({min_score:.2f}/5).
             """)

             # Añadir info de Sí/No y Complejidad si están disponibles
             if '29plazos_entrega_mercados' in df.columns:
                  plazos_series = df['29plazos_entrega_mercados'].dropna().astype(str).str.strip().str.lower()
                  if len(plazos_series) > 0:
                      plazos_si = (plazos_series == 'sí').mean() * 100
                      st.markdown(f"- El **{plazos_si:.1f}%** reporta que **Sí** se cumplen los plazos.")

             if '31pasos_recepcion_mercado' in df.columns:
                 proceso_series = df['31pasos_recepcion_mercado'].dropna().astype(str).str.strip().str.lower()
                 if len(proceso_series) > 0:
                     proceso_si = (proceso_series == 'sencillo').mean() * 100
                     st.markdown(f"- El **{proceso_si:.1f}%** considera el proceso de recepción **sencillo**.")


             st.markdown("""
             **Recomendaciones Generales:**
             - Enfocarse en mejorar los procesos relacionados con "{min_desc}".
             - Optimizar la comunicación sobre fechas/horas de entrega (si '{entrega_cols_map.get('24notificacion_telefonica')}' tiene baja puntuación).
             - Simplificar pasos de recepción si el porcentaje de 'sencillo' es bajo.
             - Mantener la buena actitud del personal si '{entrega_cols_map.get('28actitud_funcionario_logistico')}' tiene alta puntuación.
             """)
        else:
             st.info("No hay datos numéricos de satisfacción suficientes para generar conclusiones.")
    except Exception as e_conclu:
        st.error(f"Error generando conclusiones: {e_conclu}")
        print(f"ERROR 4_Proceso_Entrega.py - Conclusiones: {e_conclu}")
else:
    # Esto se maneja arriba con st.warning si no hay 'valid_display_cols'
    pass


# Footer
st.markdown("---")
st.markdown("Dashboard de Análisis de la Encuesta de Satisfacción | Sección: Proceso de Entrega de Mercado")
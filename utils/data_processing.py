import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud
import streamlit as st
from collections import Counter
import re

# Mapeo de columnas a descripciones (Usado en varias páginas)
COL_DESCRIPTIONS = {
    '9fecha_vencimiento': 'Fecha de vencimiento de abarrotes',
    '10tipo_empaque': 'Tipo de empaque de abarrotes',
    '11productos_iguales_lista_mercado': 'Correspondencia con lista de mercado',
    '12carnes_bien_etiquetadas': 'Etiquetado de carnes',
    '13producto_congelado': 'Estado de congelación',
    '14corte_recibido': 'Correspondencia del corte',
    '15fecha_vencimiento_adecuada': 'Fecha de vencimiento adecuada',
    '16empacado_al_vacio': 'Empacado al vacío',
    '17estado_huevo': 'Estado de los huevos',
    '18panal_de_huevo_etiquetado': 'Etiquetado del panal de huevos',
    '19frutas': 'Estado de las frutas',
    '20verduras': 'Estado de las verduras',
    '21hortalizas': 'Estado de las hortalizas',
    '22tuberculos': 'Estado de los tubérculos',
    '23ciclo_menus': 'Ciclo de menús establecido',
    '24notificacion_telefonica': 'Notificación telefónica',
    '25tiempo_revision_alimentos': 'Tiempo para revisar alimentos',
    '26tiempo_entrega_mercdos': 'Tiempo entre entregas', # Nota: posible typo 'mercdos' vs 'mercados'
    '27tiempo_demora_proveedor': 'Tiempo de respuesta del proveedor',
    '28actitud_funcionario_logistico': 'Actitud del funcionario logístico'
    # Añade aquí más mapeos si tienes otras columnas
}

# Definiciones de categorías para análisis (Usado en Home.py y 5_Analisis_Geografico.py)
CATEGORIES = {
    "Abarrotes": ["9fecha_vencimiento", "10tipo_empaque", "11productos_iguales_lista_mercado"],
    "Cárnicos y Huevos": ["12carnes_bien_etiquetadas", "13producto_congelado", "14corte_recibido",
                           "15fecha_vencimiento_adecuada", "16empacado_al_vacio", "17estado_huevo",
                           "18panal_de_huevo_etiquetado"],
    "Frutas y Verduras": ["19frutas", "20verduras", "21hortalizas", "22tuberculos"],
    "Proceso de Entrega": ["23ciclo_menus", "24notificacion_telefonica", "25tiempo_revision_alimentos",
                            "26tiempo_entrega_mercdos", "27tiempo_demora_proveedor", "28actitud_funcionario_logistico"]
}

# Preguntas sí/no (Usado en 4_Proceso_Entrega.py)
YES_NO_COLS = {
    "29plazos_entrega_mercados": "¿Se cumplen los plazos establecidos?",
    "30brindan_informacion_productos": "¿Brindan información sobre los productos?"
}

# --- INICIO FUNCIONES ---

def get_satisfaction_columns(df):
    """
    Identifica las columnas de satisfacción disponibles y válidas en el DataFrame.
    Se asume que estas columnas ya han sido procesadas a numéricas por data_loader.
    """
    # Columnas que POTENCIALMENTE son de satisfacción (basado en prefijos)
    potential_cols = [col for col in df.columns if col.startswith(('9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28'))]
    valid_numeric_cols = []

    for col in potential_cols:
        # Excluir columnas auxiliares creadas en data_loader
        if col.endswith(('_label', '_original', '_original_val_temp')):
            continue

        # Verificar si la columna existe y es numérica (o convertible)
        if col in df.columns:
            try:
                # Forzar conversión a numérico aquí por si acaso, aunque debería venir de data_loader
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                # Considerar válida si tiene al menos un valor numérico no-NaN
                if numeric_data.notna().any():
                    valid_numeric_cols.append(col)
                # else:
                #     print(f"DEBUG get_satisfaction_columns: Columna '{col}' no contiene valores numéricos válidos.")
            except Exception as e:
                print(f"DEBUG get_satisfaction_columns: Error verificando columna '{col}': {str(e)}")
        # else:
        #     print(f"DEBUG get_satisfaction_columns: Columna potencial '{col}' no encontrada en df.")


    # print(f"DEBUG get_satisfaction_columns: Columnas válidas encontradas: {valid_numeric_cols}")
    return valid_numeric_cols


def calculate_category_satisfaction(df, category_name):
    """
    Calcula la satisfacción promedio para una categoría específica.
    Utiliza get_satisfaction_columns para asegurar que se usan columnas válidas.
    """
    if category_name not in CATEGORIES:
        print(f"WARN calculate_category_satisfaction: Categoría '{category_name}' no definida.")
        return None

    # Obtener todas las columnas de satisfacción numéricas válidas del df ACTUAL
    all_valid_satisfaction_cols = get_satisfaction_columns(df)

    # Filtrar las que pertenecen a la categoría solicitada
    category_cols_in_df = [col for col in CATEGORIES[category_name] if col in all_valid_satisfaction_cols]

    if not category_cols_in_df:
        # print(f"DEBUG calculate_category_satisfaction: No hay columnas válidas para la categoría '{category_name}' en el dataframe actual.")
        return None

    # Calcular el promedio de los promedios de cada columna válida en la categoría
    category_means = []
    for col in category_cols_in_df:
        # La columna ya debería ser numérica por get_satisfaction_columns, pero re-verificar por seguridad
        numeric_data = pd.to_numeric(df[col], errors='coerce')
        if numeric_data.notna().any():
            col_mean = numeric_data.mean()
            if not pd.isna(col_mean):
                category_means.append(col_mean)

    if not category_means:
        # print(f"DEBUG calculate_category_satisfaction: No se pudieron calcular promedios para las columnas de '{category_name}'.")
        return None

    return sum(category_means) / len(category_means)


def plot_satisfaction_by_category(df):
    """
    Crea un gráfico de barras con la satisfacción promedio por categoría.
    """
    category_means_data = []
    for category in CATEGORIES:
        mean = calculate_category_satisfaction(df, category)
        if mean is not None:
            category_means_data.append({
                "Categoría": category,
                "Promedio de Satisfacción": mean
            })

    if not category_means_data:
        print("INFO plot_satisfaction_by_category: No hay datos de promedios por categoría para graficar.")
        # Podrías retornar un mensaje o una figura vacía en lugar de None
        # return None
        # Opcional: retornar figura con mensaje
        fig = px.bar(title="Satisfacción Promedio por Categoría")
        fig.update_layout(annotations=[dict(text="No hay datos suficientes", showarrow=False)])
        return fig


    category_df = pd.DataFrame(category_means_data)

    fig = px.bar(
        category_df,
        x="Categoría",
        y="Promedio de Satisfacción",
        title="Satisfacción Promedio por Categoría",
        color="Categoría",
        color_discrete_sequence=px.colors.qualitative.Set2, # Puedes cambiar la paleta de colores
        text='Promedio de Satisfacción', # Mostrar valor en las barras
        height=450 # Ajustar altura si es necesario
    )

    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside') # Formato del texto
    fig.update_layout(
        yaxis_range=[1, 5], # Asegurar rango de 1 a 5
        yaxis_title="Promedio (1=Muy Insatisfecho, 5=Muy Satisfecho)",
        xaxis_title="Categoría de Productos/Servicio",
        uniformtext_minsize=8, uniformtext_mode='hide' # Para manejar texto en barras pequeñas
    )
    return fig


def plot_question_satisfaction(df, question_col, question_text):
    """
    Crea un gráfico de barras para la distribución de respuestas a una pregunta específica.
    Usa la columna '_label' creada por process_satisfaction_columns.
    """
    label_col = question_col + '_label'

    if label_col not in df.columns:
        print(f"ERROR plot_question_satisfaction: Columna de etiquetas '{label_col}' no encontrada para la pregunta '{question_col}'.")
        # Intentar usar la columna original si _label no existe
        if question_col in df.columns:
             print(f"WARN plot_question_satisfaction: Usando columna original '{question_col}' porque '{label_col}' no existe.")
             col_to_use = question_col
        else:
             print(f"ERROR plot_question_satisfaction: Ni '{label_col}' ni '{question_col}' encontradas.")
             # Opcional: retornar figura con mensaje
             fig = px.bar(title=f"Distribución de Respuestas: {question_text}")
             fig.update_layout(annotations=[dict(text="Columna no encontrada", showarrow=False)])
             return fig
    elif df[label_col].isna().all():
        print(f"INFO plot_question_satisfaction: Columna de etiquetas '{label_col}' solo contiene NaNs para '{question_col}'.")
        # Opcional: retornar figura con mensaje
        fig = px.bar(title=f"Distribución de Respuestas: {question_text}")
        fig.update_layout(annotations=[dict(text="No hay datos válidos", showarrow=False)])
        return fig
    else:
        col_to_use = label_col

    # Contar frecuencias de las respuestas/etiquetas válidas
    count_df = df[col_to_use].dropna().value_counts().reset_index()
    count_df.columns = ['Respuesta', 'Conteo']


    if count_df.empty:
        print(f"INFO plot_question_satisfaction: No hay datos válidos (no-NaN) para graficar en la columna '{col_to_use}' para '{question_col}'.")
        # Opcional: retornar figura con mensaje
        fig = px.bar(title=f"Distribución de Respuestas: {question_text}")
        fig.update_layout(annotations=[dict(text="No hay datos válidos", showarrow=False)])
        return fig

    # Ordenar por nivel de satisfacción (usando las etiquetas estándar)
    satisfaction_order = [
        "MUY INSATISFECHO/A",
        "INSATISFECHO/A",
        "NI SATISFECHO/A NI INSATISFECHO/A",
        "SATISFECHO/A",
        "MUY SATISFECHO/A"
    ]
    # Convertir la columna 'Respuesta' a categórica con el orden deseado
    # Solo incluir categorías que realmente existen en los datos para evitar errores
    existing_categories = [cat for cat in satisfaction_order if cat in count_df['Respuesta'].unique()]

    if existing_categories:
         count_df['Respuesta'] = pd.Categorical(count_df['Respuesta'], categories=existing_categories, ordered=True)
         count_df = count_df.sort_values('Respuesta')
    # else: si las respuestas no coinciden (p.ej., eran números), no se ordena por satisfacción textual.

    # Crear gráfico de barras
    # Definir un mapeo de colores para las categorías de satisfacción
    color_map = {
        "MUY INSATISFECHO/A": "#D32F2F", # Rojo oscuro
        "INSATISFECHO/A": "#FF9800",     # Naranja
        "NI SATISFECHO/A NI INSATISFECHO/A": "#FFEB3B", # Amarillo
        "SATISFECHO/A": "#4CAF50",     # Verde
        "MUY SATISFECHO/A": "#1E88E5"      # Azul
        # Añade otros colores si tienes otras respuestas posibles
    }

    fig = px.bar(
        count_df,
        x='Respuesta',
        y='Conteo',
        title=f"Distribución: {question_text}", # Título más corto
        color='Respuesta',
        color_discrete_map=color_map, # Aplicar el mapeo de colores
        text='Conteo' # Mostrar conteo en las barras
    )

    fig.update_layout(
        xaxis_title="Nivel de Satisfacción",
        yaxis_title="Cantidad de Respuestas",
        xaxis={'categoryorder':'array', 'categoryarray':satisfaction_order}, # Asegurar orden en el eje X
        height=400 # Ajustar altura
    )
    fig.update_traces(textposition='outside')

    return fig


def create_wordcloud(df, comment_col):
    """
    Crea una nube de palabras a partir de los comentarios de una columna.
    """
    if comment_col not in df.columns:
        return None, f"La columna '{comment_col}' no está disponible."

    # Concatenar comentarios, asegurando que sean strings y no nulos/vacíos
    comments = df[comment_col].dropna().astype(str)
    all_comments_text = ' '.join(comments[comments.str.strip() != ''])

    if not all_comments_text:
        return None, "No hay comentarios disponibles para analizar."

    try:
        wordcloud_generator = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='viridis', # Puedes probar otras paletas: 'plasma', 'inferno', 'magma', 'cividis'
            max_words=100,
            contour_width=1,
            contour_color='steelblue',
            stopwords=None # Usaremos nuestro propio filtro después
        ).generate(all_comments_text)

        # Crear figura de matplotlib para mostrar la nube
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud_generator, interpolation='bilinear')
        ax.axis('off')
        plt.tight_layout(pad=0) # Ajustar layout

        # Obtener términos más frecuentes (filtrando stopwords comunes en español)
        words = re.findall(r'\b\w+\b', all_comments_text.lower())
        stopwords_es = [
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'y', 'o', 'u', 'de', 'del', 'a', 'al', 'en',
            'con', 'por', 'para', 'se', 'su', 'sus', 'lo', 'que', 'como', 'pero', 'mas', 'más', 'mi', 'si', 'sin',
            'sobre', 'este', 'esta', 'esto', 'estos', 'estas', 'es', 'son', 'fue', 'fueron', 'ser', 'soy', 'eres',
            'somos', 'sois', 'sido', 'sea', 'sean', 'siendo', 'no', 'ni', 'muy', 'mucho', 'poco', 'todo', 'nada',
            'algo', 'alguien', 'nadie', 'donde', 'quien', 'cual', 'cuyo', 'cuya', 'cuyos', 'cuyas', 'le', 'les',
            'me', 'te', 'nos', 'os', 'ya', 'ha', 'han', 'he', 'has', 'hemos', 'habeis', 'haya', 'hayan', 'hay',
            'pero', 'sino', 'tambien', 'también', 'porque', 'pues', 'cuando', 'mientras', 'aunque', 'siempre',
            'nunca', 'tal', 'vez', 'asi', 'así', 'bien', 'mal', 'desde', 'hasta', 'entre', 'contra', 'hacia',
            'ante', 'bajo', 'cabe', 'con', 'de', 'en', 'por', 'segun', 'sin', 'so', 'tras', 'durante', 'mediante',
            'versus', 'vía', 'yo', 'tu', 'el', 'ella', 'ello', 'nosotros', 'nosotras', 'vosotros', 'vosotras',
            'ellos', 'ellas', 'usted', 'ustedes', 'bueno', 'buena', 'productos', 'mercado', 'gracias', 'calidad',
            'entrega', 'recibido', 'atencion', 'gracias', 'servicio', 'grano', 'frijol', 'lenteja', 'arroz' # Añadir palabras comunes específicas del contexto
        ]
        word_counts = Counter(w for w in words if w not in stopwords_es and len(w) > 2) # Palabras > 2 letras
        frequent_terms = word_counts.most_common(15) # Obtener las 15 más comunes

        return fig, frequent_terms

    except Exception as e_wc:
        print(f"ERROR create_wordcloud: {e_wc}")
        return None, f"Error al generar nube de palabras: {e_wc}"


def plot_geographic_satisfaction(df, region_col):
    """
    Crea un gráfico de barras para la satisfacción promedio por región geográfica.
    """
    if region_col not in df.columns:
        print(f"ERROR plot_geographic_satisfaction: Columna de región '{region_col}' no encontrada.")
        return None

    # Obtener columnas de satisfacción ya procesadas a numéricas
    satisfaction_cols = get_satisfaction_columns(df)
    if not satisfaction_cols:
        print("INFO plot_geographic_satisfaction: No hay columnas de satisfacción válidas.")
        return None

    # Asegurar que las columnas de satisfacción sean numéricas (por si acaso)
    for col in satisfaction_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calcular el promedio de satisfacción para cada fila (encuesta)
    # Usar skipna=True es importante
    df['satisfaccion_promedio_fila'] = df[satisfaction_cols].mean(axis=1, skipna=True)

    # Verificar si se pudo calcular algún promedio por fila
    if df['satisfaccion_promedio_fila'].isna().all():
         print(f"INFO plot_geographic_satisfaction: No se pudo calcular 'satisfaccion_promedio_fila' para ninguna fila (quizás todas las columnas de satisfacción son NaN).")
         return None

    # Agrupar por la columna de región y calcular la media y el conteo
    # Asegurarse de tratar la columna de región como string para agrupar correctamente
    region_col_str = df[region_col].astype(str)
    region_stats = df.groupby(region_col_str)['satisfaccion_promedio_fila'].agg(['mean', 'count']).reset_index()
    region_stats.columns = [region_col, 'Satisfacción Promedio', 'Conteo']

    # Filtrar regiones con conteo muy bajo si se desea (opcional)
    # min_count = 3
    # region_stats = region_stats[region_stats['Conteo'] >= min_count]

    if region_stats.empty:
        print(f"INFO plot_geographic_satisfaction: No hay datos suficientes por región '{region_col}' para graficar.")
        return None

    # Ordenar por satisfacción promedio para mejor visualización
    region_stats = region_stats.sort_values('Satisfacción Promedio', ascending=False)

    # Crear gráfico de barras
    fig = px.bar(
        region_stats,
        x=region_col,
        y='Satisfacción Promedio',
        title=f"Satisfacción Promedio por {region_col.capitalize()}",
        color='Satisfacción Promedio',
        color_continuous_scale='RdYlGn', # Rojo-Amarillo-Verde (bajo a alto)
        range_color=[1,5], # Forzar escala de color de 1 a 5
        # Se puede usar 'Conteo' para el tamaño, pero puede hacer el gráfico complejo si hay muchas regiones
        # size='Conteo',
        text='Conteo', # Mostrar conteo en las barras
        height=500 # Ajustar altura
    )

    fig.update_layout(
        yaxis_range=[1, 5],
        yaxis_title="Promedio (1=Muy Insatisfecho, 5=Muy Satisfecho)",
        xaxis_title=region_col.capitalize(),
        coloraxis_colorbar=dict(title="Satisfacción")
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside') # Mostrar conteo fuera de la barra

    return fig


def plot_yes_no_questions(df):
    """
    Crea un gráfico de barras agrupadas para las preguntas de Sí/No.
    """
    valid_cols = {k: v for k, v in YES_NO_COLS.items() if k in df.columns}
    if not valid_cols:
        print("INFO plot_yes_no_questions: No se encontraron columnas Sí/No válidas.")
        return None

    yes_no_data = []
    for col, question in valid_cols.items():
        # Limpiar respuestas (string, quitar espacios, capitalizar 'Sí'/'No')
        cleaned_responses = df[col].dropna().astype(str).str.strip().str.capitalize()
        counts = cleaned_responses.value_counts().reset_index()
        counts.columns = ['Respuesta', 'Conteo']
        counts['Pregunta'] = question # Usar descripción corta para eje X
        yes_no_data.append(counts)

    if not yes_no_data:
        print("INFO plot_yes_no_questions: No hay datos válidos para las preguntas Sí/No.")
        return None

    yes_no_df = pd.concat(yes_no_data)

    # Asegurar que solo graficamos respuestas 'Sí' y 'No' estandarizadas
    yes_no_df = yes_no_df[yes_no_df['Respuesta'].isin(['Sí', 'Si', 'No'])]
    # Corregir 'Si' a 'Sí' si es necesario
    yes_no_df['Respuesta'] = yes_no_df['Respuesta'].replace({'Si': 'Sí'})


    if yes_no_df.empty:
        print("INFO plot_yes_no_questions: No hay respuestas 'Sí' o 'No' válidas encontradas.")
        return None

    fig = px.bar(
        yes_no_df,
        x='Pregunta',
        y='Conteo',
        color='Respuesta',
        barmode='group', # Barras agrupadas
        title="Respuestas a Preguntas Sí/No",
        color_discrete_map={'Sí': '#4CAF50', 'No': '#D32F2F'}, # Verde para Sí, Rojo para No
        text='Conteo'
    )

    fig.update_layout(
        xaxis_title="", # Preguntas en el eje X
        yaxis_title="Cantidad de Respuestas",
        legend_title="Respuesta",
        height=400
    )
    fig.update_traces(textposition='outside')
    return fig


def plot_complexity_analysis(df):
    """
    Crea un gráfico circular para la percepción de complejidad del proceso.
    """
    complexity_col = '31pasos_recepcion_mercado'
    if complexity_col not in df.columns:
         print(f"INFO plot_complexity_analysis: Columna '{complexity_col}' no encontrada.")
         return None

    # Limpiar y contar frecuencias
    cleaned_complexity = df[complexity_col].dropna().astype(str).str.strip().str.capitalize()
    complexity_counts = cleaned_complexity.value_counts().reset_index()
    complexity_counts.columns = ['Complejidad', 'Conteo']

    if complexity_counts.empty:
         print(f"INFO plot_complexity_analysis: No hay datos válidos en '{complexity_col}'.")
         return None

    # Ordenar categorías si es posible (Sencillo, Complejo, Muy complejo)
    complexity_order = ['Sencillo', 'Complejo', 'Muy complejo'] # Asegúrate que estos textos coincidan con tus datos
    existing_categories = [cat for cat in complexity_order if cat in complexity_counts['Complejidad'].unique()]

    if existing_categories:
         complexity_counts['Complejidad'] = pd.Categorical(complexity_counts['Complejidad'], categories=existing_categories, ordered=True)
         complexity_counts = complexity_counts.sort_values('Complejidad')

    # Mapeo de colores
    color_map = {'Sencillo': '#4CAF50', 'Complejo': '#FFC107', 'Muy complejo': '#D32F2F'}

    fig = px.pie(
        complexity_counts,
        names='Complejidad',
        values='Conteo',
        title="Percepción de Complejidad del Proceso de Recepción",
        color='Complejidad',
        color_discrete_map=color_map,
        hole=0.4 # Para gráfico de dona (opcional)
    )

    fig.update_traces(textposition='inside', textinfo='percent+label', pull=[0.05 if cat == 'Muy complejo' else 0 for cat in complexity_counts['Complejidad']]) # Destacar "Muy complejo"

    return fig


def identify_problem_areas(df):
    """
    Identifica las áreas (preguntas de satisfacción) con menor satisfacción promedio.
    """
    satisfaction_cols = get_satisfaction_columns(df)
    if not satisfaction_cols:
        return pd.DataFrame() # Retornar df vacío si no hay columnas

    # Calcular promedio para cada columna válida
    col_means = {}
    for col in satisfaction_cols:
        # Asegurar que la columna es numérica antes de calcular la media
        numeric_data = pd.to_numeric(df[col], errors='coerce')
        if numeric_data.notna().any():
             col_means[col] = numeric_data.mean()

    if not col_means:
         return pd.DataFrame() # Retornar df vacío si no se calcularon medias

    # Crear DataFrame con promedios y descripciones
    problem_df = pd.DataFrame(col_means.items(), columns=['Columna', 'Satisfacción Media'])
    # Usar el mapeo COL_DESCRIPTIONS para obtener nombres legibles
    problem_df['Aspecto'] = problem_df['Columna'].map(COL_DESCRIPTIONS).fillna(problem_df['Columna']) # Usar nombre de columna si no hay descripción

    # Ordenar de menor a mayor satisfacción
    problem_df = problem_df.sort_values('Satisfacción Media', ascending=True)

    # Devolver los 5 peores (o menos si no hay tantos)
    return problem_df[['Aspecto', 'Satisfacción Media']].head(5)


def plot_satisfaction_trend(df):
    """
    Crea un gráfico de líneas para la tendencia de satisfacción promedio por mes y categoría.
    """
    if 'fecha' not in df.columns:
        print("WARN plot_satisfaction_trend: Columna 'fecha' no encontrada.")
        return None

    # Asegurar que la fecha esté en formato datetime y eliminar NaNs
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df_trend = df.dropna(subset=['fecha']).copy()

    if df_trend.empty:
        print("INFO plot_satisfaction_trend: No hay datos con fechas válidas.")
        return None

    # Crear columna de mes (Periodo)
    df_trend['mes'] = df_trend['fecha'].dt.to_period('M')

    # Obtener columnas de satisfacción válidas
    satisfaction_cols = get_satisfaction_columns(df_trend)
    if not satisfaction_cols:
        print("INFO plot_satisfaction_trend: No hay columnas de satisfacción válidas.")
        return None

    # Calcular promedio por categoría y mes
    trends_data = []
    for category, cols_in_category in CATEGORIES.items():
        # Usar solo las columnas de satisfacción válidas que pertenecen a esta categoría
        valid_category_cols = [col for col in cols_in_category if col in satisfaction_cols]
        if not valid_category_cols:
            continue # Saltar si no hay columnas válidas para esta categoría

        # Calcular promedio por fila para esta categoría
        # Asegurar que las columnas sean numéricas aquí
        for col in valid_category_cols:
             df_trend[col] = pd.to_numeric(df_trend[col], errors='coerce')
        df_trend[f'{category}_avg'] = df_trend[valid_category_cols].mean(axis=1, skipna=True)

        # Agrupar por mes y calcular el promedio mensual de la categoría
        # Usar dropna() antes de groupby para evitar error con tipos mixtos si hay NaNs en la columna de promedio
        monthly_avg = df_trend.dropna(subset=['mes', f'{category}_avg']).groupby('mes')[f'{category}_avg'].mean().reset_index()
        monthly_avg['Mes'] = monthly_avg['mes'].astype(str) # Convertir periodo a string para el eje X
        monthly_avg['Categoría'] = category
        monthly_avg.rename(columns={f'{category}_avg': 'Satisfacción Promedio'}, inplace=True)

        trends_data.append(monthly_avg[['Mes', 'Satisfacción Promedio', 'Categoría']])

    if not trends_data:
        print("INFO plot_satisfaction_trend: No se pudieron calcular datos de tendencia.")
        return None

    trends_df = pd.concat(trends_data)

    # Crear gráfico de líneas
    fig = px.line(
        trends_df,
        x='Mes',
        y='Satisfacción Promedio',
        color='Categoría',
        title="Tendencia de Satisfacción Promedio por Mes",
        markers=True, # Añadir marcadores a los puntos
        line_shape='spline', # Línea suavizada (opcional, puedes usar 'linear')
        height=500
    )

    fig.update_layout(
        xaxis_title="Mes",
        yaxis_title="Promedio (1=Muy Insatisfecho, 5=Muy Satisfecho)",
        yaxis_range=[1, 5] # Rango fijo para comparación
    )

    return fig

# --- FIN FUNCIONES ---
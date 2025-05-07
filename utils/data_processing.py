import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud
import streamlit as st
from collections import Counter
import re

# Mapeo de columnas a descripciones
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
    '26tiempo_entrega_mercdos': 'Tiempo entre entregas',
    '27tiempo_demora_proveedor': 'Tiempo de respuesta del proveedor',
    '28actitud_funcionario_logistico': 'Actitud del funcionario logístico'
}

# Definiciones de categorías para análisis
CATEGORIES = {
    "Abarrotes": ["9fecha_vencimiento", "10tipo_empaque", "11productos_iguales_lista_mercado"],
    "Cárnicos y Huevos": ["12carnes_bien_etiquetadas", "13producto_congelado", "14corte_recibido", 
                           "15fecha_vencimiento_adecuada", "16empacado_al_vacio", "17estado_huevo", 
                           "18panal_de_huevo_etiquetado"],
    "Frutas y Verduras": ["19frutas", "20verduras", "21hortalizas", "22tuberculos"],
    "Proceso de Entrega": ["23ciclo_menus", "24notificacion_telefonica", "25tiempo_revision_alimentos",
                            "26tiempo_entrega_mercdos", "27tiempo_demora_proveedor", "28actitud_funcionario_logistico"]
}

# Preguntas sí/no
YES_NO_COLS = {
    "29plazos_entrega_mercados": "¿Se cumplen los plazos establecidos?",
    "30brindan_informacion_productos": "¿Brindan información sobre los productos?"
}

def get_satisfaction_columns(df):
    """
    Identifica las columnas de satisfacción disponibles en el DataFrame.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        
    Returns:
        list: Lista de columnas de satisfacción válidas.
    """
    base_cols = [col for col in df.columns if col.startswith(('9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28'))]
    valid_cols = []
    
    for col in base_cols:
        # Excluir columnas con sufijos especiales
        if col.endswith(('_label', '_original')):
            continue
        
        # Verificar si hay valores válidos
        try:
            # Si la columna tiene al menos algunos valores numéricos válidos, la incluimos
            numeric_data = pd.to_numeric(df[col], errors='coerce')
            if numeric_data.notna().any():
                valid_cols.append(col)
            else:
                print(f"Columna {col} no contiene valores numéricos válidos")
        except Exception as e:
            print(f"Error verificando columna {col}: {str(e)}")
    
    return valid_cols

def calculate_category_satisfaction(df, category_name):
    """
    Calcula la satisfacción promedio para una categoría específica.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        category_name (str): Nombre de la categoría ("Abarrotes", "Cárnicos y Huevos", etc.)
        
    Returns:
        float: Satisfacción promedio para la categoría.
    """
    if category_name not in CATEGORIES:
        return None
    
    cols = CATEGORIES[category_name]
    valid_cols = [col for col in cols if col in df.columns]
    
    if not valid_cols:
        return None
    
    # Asegurar que las columnas son numéricas y calcular solo con valores válidos
    category_means = []
    
    for col in valid_cols:
        # Convertir a numérico y manejar valores no numéricos
        numeric_data = pd.to_numeric(df[col], errors='coerce')
        
        # Solo incluir si hay datos válidos
        if numeric_data.notna().any():
            col_mean = numeric_data.mean()
            if not pd.isna(col_mean):
                category_means.append(col_mean)
    
    # Si no hay datos válidos para ninguna columna, retornar None
    if not category_means:
        return None
    
    # Calcular promedio de los promedios por columna
    return sum(category_means) / len(category_means)

def plot_satisfaction_by_category(df):
    """
    Crea un gráfico de barras con la satisfacción promedio por categoría.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        
    Returns:
        plotly.graph_objects.Figure or None: Figura de Plotly o None si no hay datos suficientes.
    """
    # Calcular promedio por categoría
    category_means = []
    
    for category in CATEGORIES:
        mean = calculate_category_satisfaction(df, category)
        if mean is not None:
            category_means.append({
                "Categoría": category,
                "Promedio de Satisfacción": mean
            })
    
    if not category_means:
        return None
    
    category_df = pd.DataFrame(category_means)
    
    # Crear gráfico
    fig = px.bar(
        category_df, 
        x="Categoría", 
        y="Promedio de Satisfacción",
        title="Satisfacción Promedio por Categoría",
        color="Categoría",
        color_discrete_sequence=px.colors.qualitative.Set2,
        text_auto=True
    )
    
    fig.update_layout(
        yaxis_range=[1, 5],
        yaxis_title="Promedio (1=Muy Insatisfecho, 5=Muy Satisfecho)"
    )
    
    return fig

def plot_question_satisfaction(df, question_col, question_text):
    """
    Crea un gráfico de barras para la distribución de respuestas a una pregunta específica.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        question_col (str): Nombre de la columna.
        question_text (str): Texto descriptivo de la pregunta.
        
    Returns:
        plotly.graph_objects.Figure or None: Figura de Plotly o None si la columna no existe.
    """
    # Verificar si la columna existe
    if question_col not in df.columns:
        print(f"Columna {question_col} no encontrada en el DataFrame")
        return None
    
    # Si no existe la columna de etiquetas, asegurarse de que tengamos etiquetas adecuadas
    label_col = question_col + '_label'
    if label_col not in df.columns:
        # Mapeo de valores numéricos a etiquetas de satisfacción
        num_to_text_map = {
            1: "MUY SATISFECHO/A",
            2: "INSATISFECHO/A",
            3: "NI SATISFECHO/A NI INSATISFECHO/A",
            4: "SATISFECHO/A",
            5: "MUY INSATISFECHO/A"
        }
        # Convertir la columna a numérica si es necesario
        numeric_data = pd.to_numeric(df[question_col], errors='coerce')
        df[label_col] = numeric_data.map(num_to_text_map)
    
    # Contar frecuencias de las etiquetas
    if df[label_col].notna().any():
        count_df = df[label_col].value_counts().reset_index()
        count_df.columns = ['Respuesta', 'Conteo']
    else:
        # Si no hay etiquetas válidas, intentar usar la columna original
        # Esto puede ocurrir si los valores son textuales pero no coinciden con el mapeo
        count_df = df[question_col].value_counts().reset_index()
        count_df.columns = ['Respuesta', 'Conteo']
    
    # Verificar si hay datos para graficar
    if count_df.empty:
        print(f"No hay datos válidos para graficar en la columna {question_col}")
        return None
    
    # Ordenar por nivel de satisfacción si es posible
    satisfaction_order = ["Muy insatisfecho/a", "Insatisfecho/a", "Ni satisfecho/a ni insatisfecho/a", 
                          "Satisfecho/a", "Muy satisfecho/a"]
    try:
        # Verificar si las respuestas coinciden con el orden esperado
        if all(resp in satisfaction_order for resp in count_df['Respuesta']):
            count_df['Respuesta'] = pd.Categorical(count_df['Respuesta'], categories=satisfaction_order, ordered=True)
            count_df = count_df.sort_values('Respuesta')
    except Exception as e:
        print(f"Error al ordenar las respuestas: {str(e)}")
    
    # Crear gráfico
    colors = ['#D32F2F', '#FF9800', '#FFEB3B', '#4CAF50', '#1E88E5']
    
    fig = px.bar(
        count_df, 
        x='Respuesta', 
        y='Conteo',
        title=f"Distribución de Respuestas: {question_text}",
        color='Respuesta',
        color_discrete_sequence=colors,
        text_auto=True
    )
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Cantidad de Respuestas"
    )
    
    return fig

def create_wordcloud(df, comment_col):
    """
    Crea una nube de palabras a partir de los comentarios de una columna.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        comment_col (str): Nombre de la columna de comentarios.
        
    Returns:
        tuple: (matplotlib.figure.Figure, list) Figura de Matplotlib y lista de términos frecuentes,
               o (None, str) si no hay comentarios.
    """
    # Verificar si la columna existe
    if comment_col not in df.columns:
        return None, f"La columna {comment_col} no está disponible en los datos."
    
    # Concatenar todos los comentarios no vacíos
    all_comments = ' '.join([str(comment) for comment in df[comment_col] if comment and not pd.isna(comment)])
    
    # Si no hay comentarios, mostrar mensaje
    if not all_comments or all_comments.isspace():
        return None, "No hay comentarios disponibles para analizar."
    
    # Crear nube de palabras
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap='viridis',
        max_words=100,
        contour_width=1,
        contour_color='steelblue'
    ).generate(all_comments)
    
    # Crear figura de matplotlib
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    
    # Obtener términos más frecuentes
    words = re.findall(r'\b\w+\b', all_comments.lower())
    word_count = Counter(words)
    # Filtrar palabras comunes en español
    stopwords = ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'y', 'o', 'de', 'del', 'a', 'en', 'con',
                'por', 'para', 'se', 'su', 'sus', 'al', 'lo', 'que', 'como', 'pero', 'más', 'mi', 'si', 'sin',
                'sobre', 'este', 'esta', 'estos', 'estas', 'aquel', 'aquella', 'aquellos', 'aquellas', 'es', 'son']
    frequent_terms = [(word, count) for word, count in word_count.most_common(10) if word not in stopwords and len(word) > 3]
    
    return fig, frequent_terms

def plot_geographic_satisfaction(df, region_col):
    """
    Crea un gráfico de barras para la satisfacción promedio por región geográfica.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        region_col (str): Nombre de la columna de región (comuna, barrio, nodo, etc.)
        
    Returns:
        plotly.graph_objects.Figure or None: Figura de Plotly o None si no hay datos suficientes.
    """
    # Verificar si la columna existe
    if region_col not in df.columns:
        return None
    
    # Columnas de satisfacción
    satisfaction_cols = get_satisfaction_columns(df)
    
    if not satisfaction_cols:
        return None
    
    # Asegurar que todas las columnas son numéricas
    for col in satisfaction_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Calculamos el promedio de satisfacción para cada fila, excluyendo NaN
    df['satisfaccion_promedio'] = df[satisfaction_cols].mean(axis=1)
    
    # Agrupamos por la columna de región
    region_satisfaction = df.groupby(region_col)['satisfaccion_promedio'].mean().reset_index()
    region_satisfaction.columns = [region_col, 'Satisfacción Promedio']
    
    # Contar el número de encuestas por región
    region_counts = df[region_col].value_counts().reset_index()
    region_counts.columns = [region_col, 'Conteo']
    
    # Combinar ambos dataframes
    region_data = pd.merge(region_satisfaction, region_counts, on=region_col)
    
    # Crear gráfico
    fig = px.bar(
        region_data,
        x=region_col,
        y='Satisfacción Promedio',
        title=f"Satisfacción Promedio por {region_col}",
        color='Satisfacción Promedio',
        size='Conteo',
        color_continuous_scale='RdYlGn',
        text='Conteo'
    )
    
    fig.update_layout(
        yaxis_range=[1, 5],
        yaxis_title="Promedio (1=Muy Insatisfecho, 5=Muy Satisfecho)"
    )
    
    return fig

def plot_yes_no_questions(df):
    """
    Crea un gráfico de barras para las preguntas de Sí/No.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        
    Returns:
        plotly.graph_objects.Figure or None: Figura de Plotly o None si no hay datos suficientes.
    """
    # Filtrar columnas válidas
    valid_cols = {k: v for k, v in YES_NO_COLS.items() if k in df.columns}
    
    if not valid_cols:
        return None
    
    # Crear datos para el gráfico
    yes_no_data = []
    
    for col, question in valid_cols.items():
        counts = df[col].value_counts().reset_index()
        counts.columns = ['Respuesta', 'Conteo']
        counts['Pregunta'] = question
        yes_no_data.append(counts)
    
    if not yes_no_data:
        return None
    
    yes_no_df = pd.concat(yes_no_data)
    
    # Crear gráfico
    fig = px.bar(
        yes_no_df,
        x='Pregunta',
        y='Conteo',
        color='Respuesta',
        barmode='group',
        title="Respuestas a Preguntas Sí/No",
        color_discrete_map={'Sí': '#4CAF50', 'No': '#D32F2F'},
        text_auto=True
    )
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Cantidad de Respuestas"
    )
    
    return fig

def plot_complexity_analysis(df):
    """
    Crea un gráfico circular para la percepción de complejidad del proceso.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        
    Returns:
        plotly.graph_objects.Figure or None: Figura de Plotly o None si no hay datos suficientes.
    """
    # Verificar si la columna existe
    if '31pasos_recepcion_mercado' not in df.columns:
        return None
    
    # Contar frecuencias
    complexity_counts = df['31pasos_recepcion_mercado'].value_counts().reset_index()
    complexity_counts.columns = ['Complejidad', 'Conteo']
    
    # Ordenar categorías si es posible
    try:
        complexity_order = ['Sencillo', 'Complejo', 'Muy complejo']
        complexity_counts['Complejidad'] = pd.Categorical(complexity_counts['Complejidad'], categories=complexity_order, ordered=True)
        complexity_counts = complexity_counts.sort_values('Complejidad')
    except:
        pass  # Si no funciona, usar el orden predeterminado
    
    # Crear gráfico
    colors = ['#4CAF50', '#FF9800', '#D32F2F']
    
    fig = px.pie(
        complexity_counts,
        names='Complejidad',
        values='Conteo',
        title="Percepción de Complejidad del Proceso",
        color='Complejidad',
        color_discrete_sequence=colors,
        hole=0.4
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def identify_problem_areas(df):
    """
    Identifica las áreas con menor satisfacción.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        
    Returns:
        pandas.DataFrame: DataFrame con las áreas problemáticas.
    """
    # Obtener columnas de satisfacción
    satisfaction_cols = get_satisfaction_columns(df)
    
    if not satisfaction_cols:
        return pd.DataFrame()
    
    # Filtrar solo columnas válidas en col_descriptions
    valid_descriptions = {k: v for k, v in COL_DESCRIPTIONS.items() if k in satisfaction_cols}
    
    # Calcular promedio por columna
    col_means = {}
    for col in satisfaction_cols:
        if col in valid_descriptions:
            # Asegurar que los datos son numéricos
            numeric_data = pd.to_numeric(df[col], errors='coerce')
            if numeric_data.notna().any():
                col_means[col] = numeric_data.mean()
    
    if not col_means:
        return pd.DataFrame()
    
    # Ordenar de menor a mayor satisfacción
    sorted_means = sorted(col_means.items(), key=lambda x: x[1])
    
    # Crear DataFrame para los 5 aspectos más problemáticos (o menos si no hay suficientes)
    top_n = min(5, len(sorted_means))
    problem_df = pd.DataFrame(sorted_means[:top_n], columns=['Columna', 'Satisfacción Media'])
    problem_df['Aspecto'] = problem_df['Columna'].map(valid_descriptions)
    
    return problem_df[['Aspecto', 'Satisfacción Media']]

def plot_satisfaction_trend(df):
    """
    Crea un gráfico de líneas para la tendencia de satisfacción por mes.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos.
        
    Returns:
        plotly.graph_objects.Figure or None: Figura de Plotly o None si no hay datos suficientes.
    """
    # Verificar si la columna fecha existe
    if 'fecha' not in df.columns:
        return None
    
    # Asegurar que la fecha esté en el formato correcto
    df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    df = df.dropna(subset=['fecha'])  # Eliminar filas con fechas inválidas
    
    if df.empty:
        return None
    
    # Crear columna de mes
    df['mes'] = df['fecha'].dt.to_period('M')
    
    # Columnas de satisfacción
    satisfaction_cols = get_satisfaction_columns(df)
    
    if not satisfaction_cols:
        return None
    
    # Categorías para agrupar
    categories = {}
    for category, cols in CATEGORIES.items():
        # Filtrar solo las columnas válidas para esta categoría
        valid_category_cols = [col for col in cols if col in satisfaction_cols]
        if valid_category_cols:
            categories[category] = valid_category_cols
    
    # Calcular promedios por mes y categoría
    trends_data = []
    
    for category, cols in categories.items():
        # Asegurar que todas las columnas son numéricas
        for col in cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calcular promedio por categoría, excluyendo NaN
        df[f'{category}_avg'] = df[cols].mean(axis=1)
        
        # Agrupar por mes
        monthly_avg = df.groupby('mes')[f'{category}_avg'].mean().reset_index()
        monthly_avg['mes_str'] = monthly_avg['mes'].astype(str)
        monthly_avg['Categoría'] = category
        
        trends_data.append(monthly_avg[['mes_str', f'{category}_avg', 'Categoría']])
    
    if not trends_data:
        return None
    
    # Combinar datos
    trends_df = pd.concat(trends_data)
    trends_df.columns = ['Mes', 'Satisfacción Promedio', 'Categoría']
    
    # Crear gráfico
    fig = px.line(
        trends_df,
        x='Mes',
        y='Satisfacción Promedio',
        color='Categoría',
        title="Tendencia de Satisfacción por Mes",
        markers=True,
        line_shape='linear'
    )
    
    fig.update_layout(
        xaxis_title="Mes",
        yaxis_title="Promedio (1=Muy Insatisfecho, 5=Muy Satisfecho)",
        yaxis_range=[1, 5]
    )
    
    return fig
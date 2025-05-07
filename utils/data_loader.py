import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

@st.cache_data(ttl=600)  # Caché por 10 minutos
def load_data():
    """
    Carga los datos desde la hoja de Google Sheets.
    
    Returns:
        pandas.DataFrame: DataFrame con los datos de la encuesta, o DataFrame vacío en caso de error.
    """
    try:
        # Establecer credenciales para acceder a Google Sheets
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        gc = gspread.authorize(credentials)
        
        # Abrir la hoja de cálculo por su ID y seleccionar la hoja "ENCUESTA"
        sheet = gc.open_by_key('1-PcFOekoC42u-DpxmKP7byKsUHbiqMb96gZ9rbH5I_0')
        worksheet = sheet.worksheet('ENCUESTA')
        
        # Obtener todos los datos
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Procesamiento básico de datos
        if df.empty:
            st.warning("La hoja de cálculo está vacía.")
            return pd.DataFrame()
        
        # Convertir fechas a formato datetime si existe la columna
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        
        # Mostrar los valores únicos en las columnas de satisfacción
        print_unique_values(df)
        
        # Crear columnas con etiquetas para las columnas de satisfacción
        process_satisfaction_columns(df)
        
        return df
    
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        # Retornar DataFrame vacío si hay un error
        return pd.DataFrame()

def print_unique_values(df):
    """
    Imprime los valores únicos de las columnas de satisfacción.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos de la encuesta.
    """
    # Columnas de satisfacción
    satisfaction_cols = [col for col in df.columns if col.startswith(('9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28'))]
    
    print("="*50)
    print("VALORES ÚNICOS EN LAS COLUMNAS DE SATISFACCIÓN:")
    print("="*50)
    
    for col in satisfaction_cols:
        if col in df.columns:
            unique_values = df[col].dropna().unique()
            print(f"\nColumna {col}:")
            for i, value in enumerate(unique_values):
                print(f"  {i+1}. '{value}' (tipo: {type(value).__name__})")
            if len(unique_values) == 0:
                print("  No hay valores (todos son NaN)")
    
    print("="*50)

def process_satisfaction_columns(df):
    """
    Procesa las columnas de satisfacción para convertirlas a formato numérico
    y agregar etiquetas descriptivas.
    
    Args:
        df (pandas.DataFrame): DataFrame con los datos de la encuesta.
    """
    # SOLUCIÓN DIRECTA: Mapear manualmente las respuestas de la encuesta a valores numéricos
    # Ajustado para valores en MAYÚSCULAS
    satisfaction_mapping = {
        # Valores en MAYÚSCULAS
        "MUY SATISFECHO": 5,
        "SATISFECHO": 4,
        "NI SATISFECHO NI INSATISFECHO": 3,
        "INSATISFECHO": 2,
        "MUY INSATISFECHO": 1,
        
        # Valores en MAYÚSCULAS con género
        "MUY SATISFECHO/A": 5,
        "SATISFECHO/A": 4,
        "NI SATISFECHO/A NI INSATISFECHO/A": 3,
        "INSATISFECHO/A": 2,
        "MUY INSATISFECHO/A": 1,
        
        # Variantes adicionales en MAYÚSCULAS (si existen)
        "MUY SATISFECH@": 5,
        "SATISFECH@": 4,
        "NEUTRAL": 3,
        "INSATISFECH@": 2,
        "MUY INSATISFECH@": 1,
        
        # Variantes numéricas (si existen)
        "5": 5,
        "4": 4,
        "3": 3,
        "2": 2,
        "1": 1,
        5: 5,
        4: 4,
        3: 3,
        2: 2,
        1: 1
    }
    
    # Etiquetas para mostrar en los gráficos (en formato consistente)
    label_mapping = {
        5: "MUY SATISFECHO/A",
        4: "SATISFECHO/A",
        3: "NI SATISFECHO/A NI INSATISFECHO/A",
        2: "INSATISFECHO/A",
        1: "MUY INSATISFECHO/A"
    }
    
    # Procesar cada columna de satisfacción
    satisfaction_cols = [col for col in df.columns if col.startswith(('9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28'))]
    
    for col in satisfaction_cols:
        try:
            # Guardar valores originales
            df[col + '_original'] = df[col].copy()
            
            # Aplicar el mapeo directamente
            df[col + '_numeric'] = df[col].map(satisfaction_mapping)
            
            # Verificar cuántos valores se convirtieron exitosamente
            na_count = df[col + '_numeric'].isna().sum()
            if na_count > 0:
                print(f"Advertencia: Columna {col}: {na_count} valores no pudieron ser convertidos a formato numérico")
                
                # Mostrar algunos valores problemáticos
                if na_count < df.shape[0]:
                    problematic_values = df.loc[df[col + '_numeric'].isna() & df[col].notna(), col].unique()
                    if len(problematic_values) > 0:
                        print(f"Ejemplos de valores problemáticos en {col}: {problematic_values[:5]}")
            
            # Usar la columna numérica como la principal si hay al menos algunos valores convertidos
            if na_count < df.shape[0]:
                df[col] = df[col + '_numeric']
                # Crear columna con etiquetas para visualización
                df[col + '_label'] = df[col].map(label_mapping)
            else:
                print(f"No se pudo convertir ningún valor en la columna {col} a formato numérico")
                
                # SOLUCIÓN ALTERNATIVA:
                # Si todas las respuestas están en formato desconocido, asignar valores numéricos arbitrarios
                unique_values = df[col].dropna().unique()
                if len(unique_values) > 0:
                    # Crear un mapeo temporal para estos valores
                    temp_mapping = {}
                    for i, value in enumerate(unique_values, 1):
                        # Mapear a valores del 1 al 5 dependiendo del número de opciones
                        norm_value = 1 + (i - 1) * 4 / (len(unique_values) - 1) if len(unique_values) > 1 else 3
                        temp_mapping[value] = round(norm_value)
                        print(f"Mapeo temporal: '{value}' -> {round(norm_value)}")
                    
                    # Aplicar el mapeo temporal
                    df[col] = df[col].map(temp_mapping)
                    # Crear etiquetas usando los valores originales
                    df[col + '_label'] = df[col + '_original']
                    
                    print(f"Aviso: Se aplicó un mapeo temporal para la columna {col}")
        
        except Exception as e:
            print(f"Error procesando columna {col}: {str(e)}")
    
    # Eliminar columnas temporales después de procesar
    for col in satisfaction_cols:
        if col + '_numeric' in df.columns:
            df.drop(columns=[col + '_numeric'], inplace=True, errors='ignore')

def get_filtered_data(df, date_range=None, comuna=None, barrio=None, nodo=None):
    """
    Filtra el DataFrame según los criterios seleccionados.
    
    Args:
        df (pandas.DataFrame): DataFrame original.
        date_range (list, optional): Lista con dos fechas [fecha_inicio, fecha_fin].
        comuna (str, optional): Valor de comuna para filtrar.
        barrio (str, optional): Valor de barrio para filtrar.
        nodo (str, optional): Valor de nodo para filtrar.
        
    Returns:
        pandas.DataFrame: DataFrame filtrado.
    """
    filtered_df = df.copy()
    
    # Aplicar filtro de fecha
    if date_range and len(date_range) == 2 and 'fecha' in df.columns:
        start_date, end_date = date_range
        filtered_df = filtered_df[(filtered_df['fecha'].dt.date >= start_date) & 
                                 (filtered_df['fecha'].dt.date <= end_date)]
    
    # Aplicar filtros de ubicación
    if comuna and comuna != "Todas" and 'comuna' in df.columns:
        filtered_df = filtered_df[filtered_df['comuna'].astype(str) == str(comuna)]
    
    if barrio and barrio != "Todos" and 'barrio' in df.columns:
        filtered_df = filtered_df[filtered_df['barrio'].astype(str) == str(barrio)]
    
    if nodo and nodo != "Todos" and 'nodo' in df.columns:
        filtered_df = filtered_df[filtered_df['nodo'].astype(str) == str(nodo)]
    
    return filtered_df
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials # Para gspread < 6.0
import os

# --- INICIO DE FUNCIONES DE TU data_loader.py ORIGINAL ---
# (Con añadidos para depuración en la nube)

def print_unique_values(df):
    """
    Imprime los valores únicos de las columnas de satisfacción (ANTES del procesamiento).
    """
    satisfaction_cols = [col for col in df.columns if col.startswith(('9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28'))]
    
    # DEBUGGING EN LA NUBE (imprime a los logs de Streamlit Cloud)
    print("="*50)
    print("DEBUG: VALORES ÚNICOS ANTES de process_satisfaction_columns:")
    print("="*50)
    for col in satisfaction_cols:
        if col in df.columns:
            # Convertir a string para .unique() para evitar errores con tipos mixtos si los hay
            try:
                unique_values = df[col].astype(str).unique()
                print(f"\nColumna '{col}' (dtype original: {df[col].dtype}):")
                for i, value in enumerate(unique_values[:10]): # Mostrar solo los primeros 10
                    # No es necesario mostrar el tipo aquí ya que lo convertimos a str para .unique()
                    print(f"  {i+1}. '{value}'")
                if len(unique_values) == 0:
                    print("  No hay valores o la columna está vacía.")
            except Exception as e_unique:
                print(f"\nColumna '{col}' (dtype original: {df[col].dtype}): Error al obtener únicos: {e_unique}")

        else:
            print(f"Columna '{col}' NO ENCONTRADA.")
    print("="*50)


def process_satisfaction_columns(df):
    """
    Procesa las columnas de satisfacción para convertirlas a formato numérico
    y agregar etiquetas descriptivas. (BASADO EN TU LÓGICA ORIGINAL)
    """
    print("DEBUG: Iniciando process_satisfaction_columns (lógica original adaptada)")
    satisfaction_mapping = {
        "MUY SATISFECHO": 5, "SATISFECHO": 4, "NI SATISFECHO NI INSATISFECHO": 3,
        "INSATISFECHO": 2, "MUY INSATISFECHO": 1,
        "MUY SATISFECHO/A": 5, "SATISFECHO/A": 4, "NI SATISFECHO/A NI INSATISFECHO/A": 3,
        "INSATISFECHO/A": 2, "MUY INSATISFECHO/A": 1,
        "MUY SATISFECH@": 5, "SATISFECH@": 4, "NEUTRAL": 3,
        "INSATISFECH@": 2, "MUY INSATISFECH@": 1,
        "5": 5, "4": 4, "3": 3, "2": 2, "1": 1, # Numéricos como string
        5: 5, 4: 4, 3: 3, 2: 2, 1: 1           # Numéricos como int/float
    }
    label_mapping = {
        5: "MUY SATISFECHO/A", 4: "SATISFECHO/A", 3: "NI SATISFECHO/A NI INSATISFECHO/A",
        2: "INSATISFECHO/A", 1: "MUY INSATISFECHO/A"
    }
    satisfaction_cols = [col for col in df.columns if col.startswith(('9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28'))]

    # Excluir '23por_que' si no es una columna de satisfacción numérica
    # Basado en tus logs, parece que '23por_que' SÍ está siendo procesada.
    # Si NO debe serlo, necesitas quitarla de `satisfaction_cols` o manejarla específicamente.
    # Ejemplo:
    # if '23por_que' in satisfaction_cols:
    #     print("DEBUG: '23por_que' será excluida del procesamiento de satisfacción numérica.")
    #     satisfaction_cols.remove('23por_que')


    for col in satisfaction_cols:
        if col not in df.columns:
            print(f"  INFO: Columna de satisfacción esperada '{col}' no encontrada en el DataFrame. Saltando.")
            continue
        try:
            print(f"  Procesando columna: '{col}'")
            # Guardar una copia de los valores originales para comparar después del mapeo
            df[col + '_original_val_temp'] = df[col].copy() # Usar un nombre temporal diferente si '_original' ya existe
            
            # LÓGICA DE TU VERSIÓN ORIGINAL:
            # Paso 1: Aplicar el mapeo directamente.
            # Para mayor robustez, convertir a string, limpiar (mayúsculas, espacios) ANTES de mapear.
            # Si tu versión original no hacía esto y funcionaba, es porque tus datos locales eran muy consistentes.
            # Vamos a añadir la limpieza para la nube, ya que es más seguro.
            
            series_to_map = df[col].astype(str).str.upper().str.strip()
            series_to_map.replace(['', 'NAN', 'NONE', '<NA>'], pd.NA, inplace=True) # Manejar strings vacíos/NaN
            
            df[col + '_numeric_temp'] = series_to_map.map(satisfaction_mapping)
            
            # Paso 2 (de tu lógica original): Verificar cuántos valores NO se convirtieron
            na_mask = df[col + '_numeric_temp'].isna()
            # Para identificar problemáticos, mirar en la serie que se intentó mapear (series_to_map) donde el resultado es NaN
            # y el valor original en series_to_map no era ya pd.NA (es decir, era un string real que no se mapeó)
            unconverted_cleaned_values = series_to_map[na_mask & series_to_map.notna()].unique()

            if len(unconverted_cleaned_values) > 0:
                print(f"    ADVERTENCIA: Columna '{col}': {len(unconverted_cleaned_values)} tipos de valores únicos (después de limpiar) no pudieron ser convertidos.")
                print(f"    Ejemplos de valores LIMPIADOS (str, upper, strip) NO convertidos en '{col}': {unconverted_cleaned_values[:10]}")
            
            # Paso 3 (de tu lógica original): Usar la columna numérica si algunos se convirtieron
            if df[col + '_numeric_temp'].notna().sum() > 0 : # Si al menos algunos valores se convirtieron
                df[col] = df[col + '_numeric_temp'] # Reemplaza la columna original
                df[col + '_label'] = df[col].map(label_mapping)
                print(f"    INFO: Columna '{col}' convertida. Valores numéricos únicos (hasta 5): {df[col].dropna().unique()[:5]}")
            else:
                print(f"    ERROR: No se pudo convertir NINGÚN valor en la columna '{col}' a numérico o todos resultaron NaN.")
                # Si no se convirtió nada, la columna `df[col]` original no se modifica.
                # Crear `_label` basado en el original para evitar errores downstream.
                if col + '_original_val_temp' in df: # Asegurarse que la copia existe
                     df[col + '_label'] = df[col + '_original_val_temp']
                else: # Fallback si la copia no se hizo por alguna razón
                     df[col + '_label'] = df[col]


            # Limpiar columnas temporales
            if col + '_numeric_temp' in df.columns:
                df.drop(columns=[col + '_numeric_temp'], inplace=True, errors='ignore')
            if col + '_original_val_temp' in df.columns: # Limpiar la copia temporal
                df.drop(columns=[col + '_original_val_temp'], inplace=True, errors='ignore')
            
            # Lógica de tu `else` original (mapeo temporal) - Generalmente no la recomendaría para producción
            # Si decides usarla, asegúrate que df[col + '_original'] exista.
            # La he omitido aquí para enfocarnos en que el mapeo principal funcione.

        except Exception as e:
            print(f"    ERROR CRÍTICO procesando columna '{col}': {str(e)}")
            # Si hay un error, es mejor no modificar df[col] y quizás crear _label con NaNs o los originales
            if col + '_original_val_temp' in df:
                df[col + '_label'] = df[col + '_original_val_temp']
            elif col in df: # Si _original_val_temp no se creó pero col existe
                df[col + '_label'] = df[col]
            # Limpiar por si acaso
            if col + '_numeric_temp' in df.columns: df.drop(columns=[col + '_numeric_temp'], inplace=True, errors='ignore')
            if col + '_original_val_temp' in df.columns: df.drop(columns=[col + '_original_val_temp'], inplace=True, errors='ignore')

    print("DEBUG: Fin process_satisfaction_columns")
    return df # Es buena práctica devolver el df, aunque se modifique in-place


@st.cache_data(ttl=600)
def load_data():
    print("DEBUG: Iniciando load_data()")
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        using_secrets = False # Bandera para saber de dónde se cargaron

        # Intentar cargar credenciales desde Streamlit Secrets
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            using_secrets = True
            print("INFO: Credenciales cargadas desde Streamlit Secrets.")
        else:
            # Caer de nuevo a archivo local si no está en secrets (para desarrollo local)
            current_dir = os.path.dirname(os.path.abspath(__file__)) # Directorio 'utils'
            project_root = os.path.dirname(current_dir) # Raíz del proyecto
            credentials_path = os.path.join(project_root, 'credentials.json')

            if not os.path.exists(credentials_path):
                # Mostrar error en la app y en logs
                st.error(f"Credenciales NO ENCONTRADAS: Archivo 'credentials.json' no hallado en '{credentials_path}' y 'gcp_service_account' no está en st.secrets.")
                print(f"ERROR FATAL: Credenciales NO ENCONTRADAS. 'credentials.json' no en '{credentials_path}' y no hay secrets.")
                return pd.DataFrame() # Retornar DataFrame vacío es crucial aquí
            credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
            print("INFO: Credenciales cargadas desde archivo local 'credentials.json'.")

        gc = gspread.authorize(credentials)
        google_sheet_id = '1-PcFOekoC42u-DpxmKP7byKsUHbiqMb96gZ9rbH5I_0'
        worksheet_name = 'ENCUESTA'
        
        # Mostrar en la app de dónde se cargaron las credenciales (solo si no da error antes)
        # Este mensaje se debe mover después de la carga exitosa o podría no aparecer si hay errores tempranos.
        # O usar print() para logs y st.sidebar para la UI después de que df se cargue.

        print(f"INFO: Abriendo hoja '{worksheet_name}' con ID '{google_sheet_id}'...")
        sheet = gc.open_by_key(google_sheet_id)
        worksheet = sheet.worksheet(worksheet_name)
        
        print("INFO: Obteniendo todos los registros...")
        data = worksheet.get_all_records(empty_value=None) # Usar empty_value=None o '' para consistencia
        df = pd.DataFrame(data)
        print(f"INFO: {len(df)} registros cargados desde Google Sheets.")

        if df.empty:
            st.warning("La hoja de cálculo está vacía o no se pudieron leer registros.")
            print("WARN: El DataFrame está vacío después de cargar desde Google Sheets.")
            return pd.DataFrame()
        
        # Mostrar mensajes de carga de credenciales en la sidebar DESPUÉS de una carga exitosa de df
        if using_secrets:
            st.sidebar.success("Credenciales cargadas desde Streamlit Secrets.")
        else:
            st.sidebar.info("Credenciales cargadas desde archivo local.")
            
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
        
        # Llamar a print_unique_values ANTES del procesamiento
        print_unique_values(df.copy()) # Pasar copia para no modificarla antes de procesar
        
        # Llamar a process_satisfaction_columns.
        # La versión de arriba ahora devuelve df.
        df = process_satisfaction_columns(df)

        # Imprimir información DESPUÉS del procesamiento para verificar
        print("="*50)
        print("DEBUG: ESTADO FINAL DE COLUMNAS DE SATISFACCIÓN (después de process_satisfaction_columns):")
        print("="*50)
        final_satisfaction_cols_check = [col for col in df.columns if col.startswith(('9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28')) and not col.endswith('_label')] # Excluir _label
        
        for col_check in final_satisfaction_cols_check:
            if col_check in df.columns:
                # Para columnas que deberían ser numéricas, mostrar su dtype y algunos valores
                print(f"  Columna Final '{col_check}' (dtype: {df[col_check].dtype}), Valores únicos (hasta 5): {df[col_check].dropna().unique()[:5]}")
                if not pd.api.types.is_numeric_dtype(df[col_check].dtype) and df[col_check].notna().any():
                     print(f"    ALERTA: La columna '{col_check}' NO ES NUMÉRICA después del procesamiento.")
            else:
                print(f"  Columna Final '{col_check}' no encontrada (¿fue eliminada o renombrada?).")
        print("="*50)
        
        print("DEBUG: load_data() completado.")
        return df
    
    except gspread.exceptions.APIError as e:
        error_msg = f"Error de API de Google Sheets: {e}."
        details_msg = ""
        if hasattr(e, 'response') and hasattr(e.response, 'json'):
            try:
                details_msg = f" Detalles del error de API: {e.response.json()}"
            except Exception:
                details_msg = f" No se pudieron obtener detalles JSON del error de API. Código de estado: {e.response.status_code if hasattr(e.response, 'status_code') else 'N/A'}"
        full_error = error_msg + details_msg
        st.error(full_error) # Para la UI de Streamlit
        print(f"ERROR_API: {full_error}") # Para los logs de Streamlit Cloud
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error general al cargar los datos: {e} (Tipo: {type(e).__name__})")
        print(f"ERROR_GENERAL: Error al cargar los datos: {e} (Tipo: {type(e).__name__})")
        return pd.DataFrame()


def get_filtered_data(df, date_range=None, comuna=None, barrio=None, nodo=None):
    if df is None or df.empty:
        return pd.DataFrame()
        
    filtered_df = df.copy()
    if date_range and len(date_range) == 2 and 'fecha' in df.columns:
        try:
            # Asegurar que los valores de date_range son convertibles a fechas
            start_val, end_val = date_range
            start_date = pd.to_datetime(start_val).date()
            end_date = pd.to_datetime(end_val).date()

            if not pd.api.types.is_datetime64_any_dtype(filtered_df['fecha']):
                filtered_df['fecha'] = pd.to_datetime(filtered_df['fecha'], errors='coerce')
            
            if filtered_df['fecha'].notna().any():
                 filtered_df = filtered_df[
                     (filtered_df['fecha'].dt.date >= start_date) & 
                     (filtered_df['fecha'].dt.date <= end_date)
                 ]
        except Exception as e:
            print(f"WARN: Error al procesar filtro de fecha: {e}. Rango de fechas: {date_range}. Filtro de fecha no aplicado.")
            # Decide si quieres que la app continúe sin filtro de fecha o lance un error más visible.

    location_filters = {'comuna': comuna, 'barrio': barrio, 'nodo': nodo}
    for col_name, selected_value in location_filters.items():
        if selected_value and selected_value != "Todas" and col_name in filtered_df.columns:
            if filtered_df[col_name].notna().any():
                # Convertir la columna del df a string para comparación robusta
                # Asegurar que el valor seleccionado también sea string
                filtered_df = filtered_df[filtered_df[col_name].astype(str).str.strip() == str(selected_value).strip()]
            else:
                print(f"WARN: La columna de filtro '{col_name}' solo contiene NaNs (o está vacía después de filtros previos). El filtro por '{selected_value}' no encontrará coincidencias.")
                # Si la columna del filtro está vacía o toda NaN, filtrar resultará en un df vacío.
                # Esto es a menudo un comportamiento esperado, pero el warning es útil.
    return filtered_df
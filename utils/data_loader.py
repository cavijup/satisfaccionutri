import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials # Para gspread < 6.0
# from google.oauth2.service_account import Credentials # Para gspread >= 6.0 y google-auth
import os
# import json # json no es estrictamente necesario aquí si st.secrets maneja la deserialización

@st.cache_data(ttl=600)  # Caché por 10 minutos
def load_data():
    """
    Carga los datos desde la hoja de Google Sheets.
    Utiliza Streamlit Secrets para las credenciales cuando se despliega,
    y un archivo local 'credentials.json' para desarrollo.
    """
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = None

        # Intentar cargar credenciales desde Streamlit Secrets
        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            # Para oauth2client (gspread < 6.0)
            # gspread.service_account_from_dict() es una forma más directa si el formato del secret es el JSON completo.
            # O puedes usar from_json_keyfile_dict si tu secret es un dict que representa el JSON.
            # Asegúrate de que creds_dict sea un diccionario aquí.
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

            # Si usas gspread >= 6.0 y google-auth:
            # credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
            st.sidebar.success("Credenciales cargadas desde Streamlit Secrets.")

        else:
            # Caer de nuevo a archivo local si no está en secrets (para desarrollo local)
            # Esta ruta asume que data_loader.py está en 'utils' y credentials.json en la raíz del proyecto
            # __file__ es la ruta al script actual (data_loader.py)
            # os.path.dirname(__file__) es el directorio 'utils'
            # os.path.dirname(os.path.dirname(__file__)) es la raíz del proyecto
            credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'credentials.json')

            if not os.path.exists(credentials_path):
                st.error(f"Archivo credentials.json no encontrado en '{credentials_path}' para desarrollo local y no hay secrets configurados.")
                return pd.DataFrame()

            # Para oauth2client (gspread < 6.0)
            credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)

            # Si usas gspread >= 6.0 y google-auth:
            # credentials = Credentials.from_service_account_file(credentials_path, scopes=scope)
            st.sidebar.info("Credenciales cargadas desde archivo local 'credentials.json'.")

        gc = gspread.authorize(credentials)

        # Abrir la hoja de cálculo por su ID y seleccionar la hoja "ENCUESTA"
        # También podrías obtener estos de st.secrets si lo deseas.
        google_sheet_id = '1-PcFOekoC42u-DpxmKP7byKsUHbiqMb96gZ9rbH5I_0'
        worksheet_name = 'ENCUESTA'
        
        # if "google_sheet_id" in st.secrets and "worksheet_name" in st.secrets:
        #     google_sheet_id = st.secrets["google_sheet_id"]
        #     worksheet_name = st.secrets["worksheet_name"]
        # else:
        #     # Fallback a valores hardcodeados si no están en secrets (opcional)
        #     google_sheet_id = '1-PcFOekoC42u-DpxmKP7byKsUHbiqMb96gZ9rbH5I_0'
        #     worksheet_name = 'ENCUESTA'


        sheet = gc.open_by_key(google_sheet_id)
        worksheet = sheet.worksheet(worksheet_name)

        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        if df.empty:
            st.warning("La hoja de cálculo parece estar vacía o no se pudieron obtener registros.")
            return pd.DataFrame()

        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

        print_unique_values(df) # Asegúrate de que esta función esté definida abajo
        process_satisfaction_columns(df) # Asegúrate de que esta función esté definida abajo

        return df

    except gspread.exceptions.APIError as e:
        st.error(f"Error de API de Google Sheets: {e}. Verifica los permisos de la cuenta de servicio y el ID de la hoja.")
        if hasattr(e, 'response') and hasattr(e.response, 'json'):
            st.error(f"Detalles del error: {e.response.json()}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error general al cargar los datos: {e}")
        st.error(f"Tipo de error: {type(e).__name__}")
        return pd.DataFrame()

def print_unique_values(df):
    """
    Imprime los valores únicos de las columnas de satisfacción.
    Args:
        df (pandas.DataFrame): DataFrame con los datos de la encuesta.
    """
    satisfaction_cols_prefixes = ('9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28')
    satisfaction_cols = [col for col in df.columns if col.startswith(satisfaction_cols_prefixes)]

    # Descomenta las siguientes líneas si quieres ver esta salida en la consola de Streamlit (local)
    # o en los logs de Streamlit Cloud.
    # print("="*50)
    # print("VALORES ÚNICOS EN LAS COLUMNAS DE SATISFACCIÓN (DEBUG):")
    # print("="*50)
    # for col in satisfaction_cols:
    #     if col in df.columns:
    #         unique_values = df[col].dropna().unique()
    #         print(f"\nColumna {col}:")
    #         for i, value in enumerate(unique_values):
    #             print(f"  {i+1}. '{value}' (tipo: {type(value).__name__})")
    #         if len(unique_values) == 0:
    #             print("  No hay valores (todos son NaN o la columna no tiene datos para este filtro)")
    # print("="*50)
    pass # Puedes mantener esta función o eliminarla si el debug ya no es necesario


def process_satisfaction_columns(df):
    """
    Procesa las columnas de satisfacción para convertirlas a formato numérico
    y agregar etiquetas descriptivas.
    Args:
        df (pandas.DataFrame): DataFrame con los datos de la encuesta.
    """
    satisfaction_mapping = {
        "MUY SATISFECHO": 5, "SATISFECHO": 4, "NI SATISFECHO NI INSATISFECHO": 3,
        "INSATISFECHO": 2, "MUY INSATISFECHO": 1,
        "MUY SATISFECHO/A": 5, "SATISFECHO/A": 4, "NI SATISFECHO/A NI INSATISFECHO/A": 3,
        "INSATISFECHO/A": 2, "MUY INSATISFECHO/A": 1,
        "MUY SATISFECH@": 5, "SATISFECH@": 4, "NEUTRAL": 3,
        "INSATISFECH@": 2, "MUY INSATISFECH@": 1,
        "5": 5, "4": 4, "3": 3, "2": 2, "1": 1,
        5: 5, 4: 4, 3: 3, 2: 2, 1: 1
    }
    label_mapping = {
        5: "MUY SATISFECHO/A", 4: "SATISFECHO/A", 3: "NI SATISFECHO/A NI INSATISFECHO/A",
        2: "INSATISFECHO/A", 1: "MUY INSATISFECHO/A"
    }

    satisfaction_cols_prefixes = ('9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28')
    satisfaction_cols = [col for col in df.columns if col.startswith(satisfaction_cols_prefixes)]

    for col in satisfaction_cols:
        if col in df.columns: # Verificar que la columna exista antes de procesar
            df[col + '_original'] = df[col].copy()
            # Convertir a string, luego a mayúsculas y quitar espacios para un mapeo más robusto
            df[col + '_numeric'] = df[col].astype(str).str.upper().str.strip().map(satisfaction_mapping)

            # Manejar casos donde la conversión directa a numérico podría ser útil si el mapeo falla
            # Esto es útil si los datos ya son números pero como strings '1.0', '2.0', etc.
            # O si el mapeo no cubrió alguna variante textual
            df[col + '_numeric'] = pd.to_numeric(df[col + '_numeric'], errors='coerce').fillna(
                pd.to_numeric(df[col], errors='coerce') # Intentar convertir la columna original directamente
            )


            na_count_after_mapping = df[col + '_numeric'].isna().sum()
            total_rows = len(df)

            if na_count_after_mapping > 0 and na_count_after_mapping < total_rows:
                # Descomenta si necesitas este debug en los logs
                # print(f"Advertencia: Columna {col}: {na_count_after_mapping} de {total_rows} valores no pudieron ser convertidos a formato numérico después del mapeo.")
                # problematic_values = df.loc[df[col + '_numeric'].isna() & df[col].notna(), col].unique()
                # if len(problematic_values) > 0:
                #     print(f"Ejemplos de valores problemáticos en {col} (después del mapeo): {problematic_values[:5]}")
                pass


            if na_count_after_mapping < total_rows : # Si al menos algunos valores se convirtieron
                df[col] = df[col + '_numeric']
                df[col + '_label'] = df[col].map(label_mapping)
            else:
                # print(f"No se pudo convertir ningún valor en la columna {col} a formato numérico o todos son NaN.")
                # Si no se pudo convertir nada y la columna original no era numérica,
                # la columna _label podría quedar vacía o con errores si no se maneja.
                # Se podría intentar crear etiquetas desde los valores originales si son consistentes.
                if pd.api.types.is_numeric_dtype(df[col + '_original']):
                     df[col + '_label'] = df[col + '_original'].map(label_mapping) # Si eran numéricos originalmente
                else:
                     df[col + '_label'] = df[col + '_original'] # Usar originales como etiquetas si son texto

    # Eliminar columnas temporales después de procesar
    for col in satisfaction_cols:
        if col + '_numeric' in df.columns:
            df.drop(columns=[col + '_numeric'], inplace=True, errors='ignore')
        # No eliminar '_original' si se usa como fallback para '_label'
        # if col + '_original' in df.columns and col + '_label' in df.columns and df[col+'_label'].equals(df[col+'_original']):
        #     pass # No borrar si se está usando
        # else:
        #     if col + '_original' in df.columns:
        #         df.drop(columns=[col + '_original'], inplace=True, errors='ignore')


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
    if df is None or df.empty:
        return pd.DataFrame()

    filtered_df = df.copy()

    # Aplicar filtro de fecha
    if date_range and len(date_range) == 2 and 'fecha' in filtered_df.columns:
        try:
            start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            # Asegurar que la columna 'fecha' es datetime
            if not pd.api.types.is_datetime64_any_dtype(filtered_df['fecha']):
                filtered_df['fecha'] = pd.to_datetime(filtered_df['fecha'], errors='coerce')

            # Filtrar solo si la columna de fecha es válida y no todos NaN después de la conversión
            if filtered_df['fecha'].notna().any():
                filtered_df = filtered_df[
                    (filtered_df['fecha'].dt.date >= start_date.date()) &
                    (filtered_df['fecha'].dt.date <= end_date.date())
                ]
        except Exception as e:
            st.warning(f"Error al aplicar filtro de fecha: {e}. Asegúrate de que las fechas sean válidas.")


    # Aplicar filtros de ubicación (asegurando que las columnas existan y convirtiendo a string para comparación)
    location_filters = {'comuna': comuna, 'barrio': barrio, 'nodo': nodo}
    for col_name, selected_value in location_filters.items():
        if selected_value and selected_value != "Todas" and col_name in filtered_df.columns:
            # Convertir tanto la columna del df como el valor seleccionado a string para una comparación robusta
            # y manejar NaNs en la columna convirtiéndolos a un string que no coincida o filtrándolos antes.
            filtered_df = filtered_df[filtered_df[col_name].astype(str).str.strip() == str(selected_value).strip()]

    return filtered_df
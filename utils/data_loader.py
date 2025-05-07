import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials # Para gspread < 6.0
import os
import numpy as np # Necesario para pd.NA y quizás dtypes

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
            try:
                unique_values = df[col].dropna().astype(str).unique()
                print(f"\nColumna '{col}' (dtype original: {df[col].dtype}):")
                for i, value in enumerate(unique_values[:10]): # Mostrar solo los primeros 10
                    print(f"  {i+1}. '{value}'")
                if len(unique_values) == 0:
                    print("  No hay valores no-NaN o la columna está vacía.")
            except Exception as e_unique:
                print(f"\nColumna '{col}' (dtype original: {df[col].dtype}): Error al obtener únicos: {e_unique}")

        else:
            print(f"Columna '{col}' NO ENCONTRADA.")
    print("="*50)


def process_satisfaction_columns(df):
    """
    Procesa las columnas de satisfacción para convertirlas a formato numérico
    y agregar etiquetas descriptivas. (BASADO EN TU LÓGICA ORIGINAL CON MEJORAS)
    """
    print("DEBUG: Iniciando process_satisfaction_columns")
    satisfaction_mapping = {
        "MUY SATISFECHO": 5, "SATISFECHO": 4, "NI SATISFECHO NI INSATISFECHO": 3,
        "INSATISFECHO": 2, "MUY INSATISFECHO": 1,
        "MUY SATISFECHO/A": 5, "SATISFECHO/A": 4, "NI SATISFECHO/A NI INSATISFECHO/A": 3,
        "INSATISFECHO/A": 2, "MUY INSATISFECHO/A": 1,
        "MUY SATISFECH@": 5, "SATISFECH@": 4, "NEUTRAL": 3,
        "INSATISFECH@": 2, "MUY INSATISFECH@": 1,
        "5": 5, "4": 4, "3": 3, "2": 2, "1": 1, # Numéricos como string
        5: 5, 4: 4, 3: 3, 2: 2, 1: 1           # Numéricos como int/float
        # ---> AÑADE AQUÍ cualquier otro valor encontrado en los logs de DEBUG <---
    }
    label_mapping = {
        5: "MUY SATISFECHO/A", 4: "SATISFECHO/A", 3: "NI SATISFECHO/A NI INSATISFECHO/A",
        2: "INSATISFECHO/A", 1: "MUY INSATISFECHO/A"
    }
    satisfaction_cols = [col for col in df.columns if col.startswith(('9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28'))]

    cols_to_exclude = ['23por_que'] # Añade otras si es necesario
    satisfaction_cols = [col for col in satisfaction_cols if col not in cols_to_exclude]
    print(f"DEBUG: Columnas a procesar como satisfacción: {satisfaction_cols}")

    for col in satisfaction_cols:
        if col not in df.columns:
            print(f"  INFO: Columna de satisfacción esperada '{col}' no encontrada. Saltando.")
            continue
        try:
            print(f"  Procesando columna: '{col}'")
            original_series = df[col].copy()

            series_to_map = df[col].astype(str).str.upper().str.strip()
            series_to_map.replace(['', 'NAN', 'NONE', '<NA>', 'N/A', 'NA'], pd.NA, inplace=True)

            numeric_temp = series_to_map.map(satisfaction_mapping)

            na_mask = numeric_temp.isna()
            unconverted_cleaned_values = series_to_map[na_mask & series_to_map.notna()].unique()

            if len(unconverted_cleaned_values) > 0:
                print(f"    ADVERTENCIA: Columna '{col}': {len(unconverted_cleaned_values)} tipos de valores únicos (limpiados) no convertidos.")
                print(f"    -> NECESITAS AÑADIR ESTOS AL satisfaction_mapping SI SON VÁLIDOS: {unconverted_cleaned_values[:10]}")

            if numeric_temp.notna().sum() > 0 :
                df[col] = pd.to_numeric(numeric_temp, errors='coerce')
                df[col + '_label'] = df[col].map(label_mapping)
                print(f"    INFO: Columna '{col}' convertida a numérica. Dtype: {df[col].dtype}. Valores únicos (hasta 5): {df[col].dropna().unique()[:5]}")
            else:
                print(f"    ERROR: No se pudo convertir NINGÚN valor en '{col}' a numérico. Columna se mantiene original.")
                df[col + '_label'] = original_series

            if col + '_label' in df.columns:
                 label_na_mask = df[col + '_label'].isna()
                 if label_na_mask.any():
                     df[col + '_label'] = df[col + '_label'].fillna(original_series[label_na_mask])

        except Exception as e:
            print(f"    ERROR CRÍTICO procesando columna '{col}': {str(e)}")
            if col in df.columns and col + '_label' not in df.columns :
                 df[col + '_label'] = df[col].copy()

    print("DEBUG: Fin process_satisfaction_columns")
    return df


@st.cache_data(ttl=600)
def load_data():
    """
    Carga y preprocesa datos desde Google Sheets usando st.secrets o archivo local.
    """
    print("DEBUG: Iniciando load_data()")
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        using_secrets = False

        if "gcp_service_account" in st.secrets:
            creds_dict = st.secrets["gcp_service_account"]
            try:
                credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                using_secrets = True
                print("INFO: Credenciales cargadas desde Streamlit Secrets.")
            except Exception as e_secrets:
                st.error(f"Error al procesar credenciales desde st.secrets: {e_secrets}. Verifica el formato en la configuración de Secrets.")
                print(f"ERROR FATAL: Error al procesar credenciales desde st.secrets: {e_secrets}")
                return pd.DataFrame()
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            credentials_path = os.path.join(project_root, 'credentials.json')

            if not os.path.exists(credentials_path):
                st.error(f"Credenciales NO ENCONTRADAS: Archivo 'credentials.json' no hallado en '{credentials_path}' y 'gcp_service_account' no está en st.secrets.")
                print(f"ERROR FATAL: Credenciales NO ENCONTRADAS. 'credentials.json' no en '{credentials_path}' y no hay secrets.")
                return pd.DataFrame()
            try:
                credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
                print("INFO: Credenciales cargadas desde archivo local 'credentials.json'.")
            except Exception as e_local_creds:
                st.error(f"Error al cargar credenciales desde archivo local '{credentials_path}': {e_local_creds}")
                print(f"ERROR FATAL: Error al cargar credenciales desde archivo local '{credentials_path}': {e_local_creds}")
                return pd.DataFrame()

        # --- Acceder a Google Sheets ---
        try:
            gc = gspread.authorize(credentials)
            google_sheet_id = '1-PcFOekoC42u-DpxmKP7byKsUHbiqMb96gZ9rbH5I_0'
            worksheet_name = 'ENCUESTA'

            print(f"INFO: Abriendo hoja '{worksheet_name}' con ID '{google_sheet_id}'...")
            sheet = gc.open_by_key(google_sheet_id)
            worksheet = sheet.worksheet(worksheet_name)

            print("INFO: Obteniendo todos los registros...")
            # --- CORRECCIÓN AQUÍ ---
            # Usar head=1 y default_blank=None en lugar de empty_value=None
            data = worksheet.get_all_records(head=1, default_blank=None)
            # -----------------------
            df = pd.DataFrame(data)
            print(f"INFO: {len(df)} registros cargados desde Google Sheets.")

        except gspread.exceptions.APIError as e_api:
            error_msg = f"Error de API de Google Sheets: {e_api}."
            details_msg = ""
            if hasattr(e_api, 'response') and hasattr(e_api.response, 'json'):
                try: details_msg = f" Detalles: {e_api.response.json()}"
                except Exception: details_msg = f" Código estado: {e_api.response.status_code if hasattr(e_api.response, 'status_code') else 'N/A'}"
            full_error = error_msg + details_msg + " Verifica permisos de cuenta de servicio y ID/nombre de hoja."
            st.error(full_error)
            print(f"ERROR_API: {full_error}")
            return pd.DataFrame()
        except Exception as e_gspread:
            st.error(f"Error inesperado al interactuar con Google Sheets: {e_gspread} (Tipo: {type(e_gspread).__name__})")
            print(f"ERROR_GSPREAD: {e_gspread} (Tipo: {type(e_gspread).__name__})")
            return pd.DataFrame()

        # --- Procesamiento del DataFrame ---
        if df.empty:
            st.warning("El DataFrame está vacío después de cargar desde Google Sheets.")
            print("WARN: El DataFrame está vacío después de cargar desde Google Sheets.")
            return pd.DataFrame()

        # Mostrar mensajes de carga de credenciales después de éxito
        if st.runtime.exists():
            if using_secrets: st.sidebar.success("Credenciales cargadas desde Secrets.")
            else: st.sidebar.info("Credenciales cargadas desde archivo local.")

        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

        print_unique_values(df.copy()) # ANTES de procesar

        df = process_satisfaction_columns(df) # Procesar

        # DESPUÉS de procesar
        print("="*50)
        print("DEBUG: ESTADO FINAL DE COLUMNAS DE SATISFACCIÓN:")
        print("="*50)
        final_satisfaction_cols_check = [col for col in df.columns if col.startswith(('9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28')) and not col.endswith('_label')]

        for col_check in final_satisfaction_cols_check:
            if col_check in df.columns:
                print(f"  Columna Final '{col_check}' (dtype: {df[col_check].dtype}), Valores únicos (hasta 5): {df[col_check].dropna().unique()[:5]}")
                if not pd.api.types.is_numeric_dtype(df[col_check].dtype) and df[col_check].notna().any():
                     print(f"    ----> ALERTA: La columna '{col_check}' NO ES NUMÉRICA después del procesamiento.")
            else:
                print(f"  Columna Final '{col_check}' no encontrada.")
        print("="*50)

        print("DEBUG: load_data() completado.")
        return df

    except Exception as e_load:
        st.error(f"Error general inesperado en load_data: {e_load} (Tipo: {type(e_load).__name__})")
        print(f"ERROR_LOAD_GENERAL: {e_load} (Tipo: {type(e_load).__name__})")
        return pd.DataFrame()


def get_filtered_data(df, date_range=None, comuna=None, barrio=None, nodo=None):
    """
    Filtra el DataFrame según los criterios seleccionados.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    filtered_df = df.copy()

    # Filtro de fecha
    if date_range and len(date_range) == 2 and 'fecha' in filtered_df.columns:
        try:
            start_val, end_val = date_range
            start_date = pd.to_datetime(start_val).date()
            end_date = pd.to_datetime(end_val).date()
            if not pd.api.types.is_datetime64_any_dtype(filtered_df['fecha']):
                filtered_df['fecha'] = pd.to_datetime(filtered_df['fecha'], errors='coerce')
            if filtered_df['fecha'].notna().any():
                 filtered_df = filtered_df[(filtered_df['fecha'].dt.date >= start_date) & (filtered_df['fecha'].dt.date <= end_date)]
        except Exception as e_date_filter:
            print(f"WARN: Error procesando filtro de fecha: {e_date_filter}. Rango: {date_range}. Filtro no aplicado.")

    # Filtros de ubicación
    location_filters = {'comuna': comuna, 'barrio': barrio, 'nodo': nodo}
    for col_name, selected_value in location_filters.items():
        if selected_value and selected_value != "Todas" and col_name in filtered_df.columns:
            if not filtered_df.empty and filtered_df[col_name].notna().any():
                filtered_df = filtered_df[filtered_df[col_name].astype(str).str.strip() == str(selected_value).strip()]
            # else: # No filtrar si df ya está vacío o la columna filtro es toda NaN
                # print(f"WARN: No se aplica filtro por '{col_name}'='{selected_value}' (df vacío o columna NaN).")

    return filtered_df

# --- FIN DE FUNCIONES DE data_loader.py ---
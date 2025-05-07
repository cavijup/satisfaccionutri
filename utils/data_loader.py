import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials # Para gspread < 6.0
import os
import numpy as np # Necesario para pd.NA y quizás dtypes

# --- Funciones de data_loader.py ---

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
                # Usar dropna() antes de unique() para evitar mostrar NaN explícitamente si no es necesario
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
        "NEUTRAL": 3, # Asegúrate que este mapeo sea correcto para 'NEUTRAL'
        "INSATISFECH@": 2,
        "MUY INSATISFECH@": 1,
        # Variantes numéricas (si existen)
        "5": 5, "4": 4, "3": 3, "2": 2, "1": 1, # Numéricos como string
        5: 5, 4: 4, 3: 3, 2: 2, 1: 1           # Numéricos como int/float
        # ---> AÑADE AQUÍ cualquier otro valor encontrado en los logs de DEBUG <---
        # "REGULAR": 3, # Ejemplo
    }
    label_mapping = {
        5: "MUY SATISFECHO/A",
        4: "SATISFECHO/A",
        3: "NI SATISFECHO/A NI INSATISFECHO/A",
        2: "INSATISFECHO/A",
        1: "MUY INSATISFECHO/A"
    }
    # Columnas que deben ser procesadas como escala de satisfacción 1-5
    satisfaction_cols = [col for col in df.columns if col.startswith(('9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28'))]

    # EXCLUIR explícitamente columnas que NO son de satisfacción numérica (ej. '23por_que')
    cols_to_exclude = ['23por_que'] # Añade otras si es necesario
    satisfaction_cols = [col for col in satisfaction_cols if col not in cols_to_exclude]
    print(f"DEBUG: Columnas a procesar como satisfacción: {satisfaction_cols}")

    for col in satisfaction_cols:
        if col not in df.columns:
            print(f"  INFO: Columna de satisfacción esperada '{col}' no encontrada. Saltando.")
            continue
        try:
            print(f"  Procesando columna: '{col}'")
            # Guardar copia original para referencia y fallback de etiquetas
            original_series = df[col].copy()

            # Limpiar y mapear
            # Convertir a string, luego a mayúsculas, quitar espacios y manejar NaNs
            series_to_map = df[col].astype(str).str.upper().str.strip()
            # Reemplazar varios posibles marcadores de vacío/NaN con pd.NA real
            series_to_map.replace(['', 'NAN', 'NONE', '<NA>', 'N/A', 'NA'], pd.NA, inplace=True)

            # Aplicar el mapeo
            numeric_temp = series_to_map.map(satisfaction_mapping)

            # Identificar valores que no se mapearon (y no eran NA originalmente en la serie limpia)
            na_mask = numeric_temp.isna()
            unconverted_cleaned_values = series_to_map[na_mask & series_to_map.notna()].unique()

            if len(unconverted_cleaned_values) > 0:
                print(f"    ADVERTENCIA: Columna '{col}': {len(unconverted_cleaned_values)} tipos de valores únicos (después de limpiar) no pudieron ser convertidos.")
                print(f"    -> NECESITAS AÑADIR ESTOS AL satisfaction_mapping SI SON VÁLIDOS: {unconverted_cleaned_values[:10]}")

            # Reemplazar la columna original SOLO si el mapeo tuvo éxito (al menos un valor convertido)
            if numeric_temp.notna().sum() > 0 :
                # Asegurarse de que el tipo sea numérico (float para permitir NaNs)
                df[col] = pd.to_numeric(numeric_temp, errors='coerce')
                df[col + '_label'] = df[col].map(label_mapping)
                print(f"    INFO: Columna '{col}' convertida a numérica. Dtype: {df[col].dtype}. Valores únicos (hasta 5): {df[col].dropna().unique()[:5]}")
            else:
                # Si NADA se convirtió, dejar la columna original como estaba pero asegurar que _label exista
                print(f"    ERROR: No se pudo convertir NINGÚN valor en '{col}' a numérico o todos resultaron NaN. La columna se mantiene como estaba.")
                df[col + '_label'] = original_series # Usar originales como etiqueta

            # Intentar rellenar NaNs en _label con el valor original si no se pudo mapear
            if col + '_label' in df.columns:
                 label_na_mask = df[col + '_label'].isna()
                 if label_na_mask.any():
                     # Rellenar solo donde _label es NaN pero el original no lo era
                     df[col + '_label'] = df[col + '_label'].fillna(original_series[label_na_mask])


        except Exception as e:
            print(f"    ERROR CRÍTICO procesando columna '{col}': {str(e)}")
            # En caso de error inesperado, crear la columna _label con los originales
            if col in df.columns and col + '_label' not in df.columns : # Evitar sobreescribir si ya se creó
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
        using_secrets = False # Bandera para saber de dónde se cargaron

        # Intentar cargar credenciales desde Streamlit Secrets
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
            # Caer de nuevo a archivo local si no está en secrets (para desarrollo local)
            current_dir = os.path.dirname(os.path.abspath(__file__)) # Directorio 'utils'
            project_root = os.path.dirname(current_dir) # Raíz del proyecto
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
            # empty_value=None puede ayudar a que gspread no convierta celdas vacías a ''
            # header_row=1 es el default, asume que la fila 1 es encabezado.
            data = worksheet.get_all_records(empty_value=None, head=1, default_blank=None)
            df = pd.DataFrame(data)
            print(f"INFO: {len(df)} registros cargados desde Google Sheets.")

        except gspread.exceptions.APIError as e_api:
            error_msg = f"Error de API de Google Sheets: {e_api}."
            details_msg = ""
            if hasattr(e_api, 'response') and hasattr(e_api.response, 'json'):
                try:
                    details_msg = f" Detalles: {e_api.response.json()}"
                except Exception:
                    details_msg = f" Código estado: {e_api.response.status_code if hasattr(e_api.response, 'status_code') else 'N/A'}"
            full_error = error_msg + details_msg + " Verifica permisos de la cuenta de servicio y el ID/nombre de la hoja."
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
            # Retornar vacío es correcto aquí, pero quizás quieras investigar por qué la hoja está vacía si no debería.
            return pd.DataFrame()

        # Mostrar mensajes de carga de credenciales en la sidebar DESPUÉS de una carga exitosa
        if st.runtime.exists(): # Verificar si estamos en un entorno Streamlit activo
            if using_secrets:
                st.sidebar.success("Credenciales cargadas desde Secrets.")
            else:
                st.sidebar.info("Credenciales cargadas desde archivo local.")

        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

        # Llamar a print_unique_values ANTES del procesamiento
        print_unique_values(df.copy())

        # Llamar a process_satisfaction_columns. Devuelve el df modificado.
        df = process_satisfaction_columns(df) # Reasignar el resultado

        # Imprimir información DESPUÉS del procesamiento para verificar
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
                print(f"  Columna Final '{col_check}' no encontrada (¿fue eliminada o renombrada?).")
        print("="*50)

        print("DEBUG: load_data() completado.")
        return df

    except Exception as e_load:
        # Captura errores generales que puedan ocurrir fuera de los bloques try específicos
        st.error(f"Error general inesperado en load_data: {e_load} (Tipo: {type(e_load).__name__})")
        print(f"ERROR_LOAD_GENERAL: {e_load} (Tipo: {type(e_load).__name__})")
        # Considera imprimir traceback para depuración más profunda si es necesario:
        # import traceback
        # print(traceback.format_exc())
        return pd.DataFrame()


def get_filtered_data(df, date_range=None, comuna=None, barrio=None, nodo=None):
    """
    Filtra el DataFrame según los criterios seleccionados.
    """
    if df is None or df.empty:
        # print("DEBUG get_filtered_data: DataFrame de entrada vacío o None.")
        return pd.DataFrame()

    filtered_df = df.copy()
    # print(f"DEBUG get_filtered_data: Iniciando con {len(filtered_df)} filas.")

    # Aplicar filtro de fecha
    if date_range and len(date_range) == 2 and 'fecha' in filtered_df.columns:
        try:
            start_val, end_val = date_range
            # Intentar convertir a pd.Timestamp primero para manejo robusto, luego a date
            start_date = pd.to_datetime(start_val).date()
            end_date = pd.to_datetime(end_val).date()

            # Asegurar que la columna 'fecha' es datetime y manejar errores
            if not pd.api.types.is_datetime64_any_dtype(filtered_df['fecha']):
                filtered_df['fecha'] = pd.to_datetime(filtered_df['fecha'], errors='coerce')

            # Filtrar solo si la columna de fecha es válida y no todos NaN después de la conversión
            if filtered_df['fecha'].notna().any():
                 # Guardar filas antes de filtrar fecha
                 # rows_before_date_filter = len(filtered_df)
                 filtered_df = filtered_df[
                     (filtered_df['fecha'].dt.date >= start_date) &
                     (filtered_df['fecha'].dt.date <= end_date)
                 ]
                 # print(f"DEBUG get_filtered_data: Después filtro fecha ({start_date} a {end_date}): {len(filtered_df)} filas (de {rows_before_date_filter}).")
            else:
                 print(f"DEBUG get_filtered_data: Columna 'fecha' no contiene fechas válidas. Filtro no aplicado.")

        except Exception as e_date_filter:
            print(f"WARN: Error al procesar filtro de fecha: {e_date_filter}. Rango: {date_range}. Filtro de fecha no aplicado.")

    # Aplicar filtros de ubicación
    location_filters = {'comuna': comuna, 'barrio': barrio, 'nodo': nodo}
    for col_name, selected_value in location_filters.items():
        # Asegurarse que selected_value no sea None o vacío además de "Todas"
        if selected_value and selected_value != "Todas" and col_name in filtered_df.columns:
            # Solo proceder si hay datos para filtrar
            if not filtered_df.empty:
                # Convertir columna a string y comparar con valor seleccionado como string
                # Esto maneja números y texto en la columna de forma consistente
                # .astype(str) convertirá NaN a la cadena 'nan' o similar, así que comparar con str(selected_value) funciona.
                # Usar .strip() en ambos lados por seguridad.
                rows_before_loc_filter = len(filtered_df)
                filtered_df = filtered_df[filtered_df[col_name].astype(str).str.strip() == str(selected_value).strip()]
                # print(f"DEBUG get_filtered_data: Después filtro '{col_name}' == '{selected_value}': {len(filtered_df)} filas (de {rows_before_loc_filter}).")
            # else:
                # print(f"DEBUG get_filtered_data: DataFrame ya estaba vacío antes de filtrar por '{col_name}'.")
        # else:
            # print(f"DEBUG get_filtered_data: Filtro por '{col_name}' no aplicado (valor='{selected_value}' o columna no existe).")

    # print(f"DEBUG get_filtered_data: Finalizando con {len(filtered_df)} filas.")
    return filtered_df

# --- FIN DE FUNCIONES DE data_loader.py ---
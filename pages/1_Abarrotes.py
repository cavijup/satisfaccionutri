# pages/1_Abarrotes_Mejorado.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
from utils.data_loader import load_data
from utils.data_processing import plot_question_satisfaction, COL_DESCRIPTIONS

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Abarrotes",
    page_icon="📦",
    layout="wide"
)

# Función para aplicar filtros mejorados
def render_filtros_mejorados(df):
    """Renderiza filtros mejorados en la sidebar"""
    st.sidebar.title("🔍 Filtros Avanzados")
    
    # Toggle para activar/desactivar filtros
    filtros_activos = st.sidebar.checkbox("🎛️ Activar Filtros", value=False, key="filtros_abarrotes")
    
    if not filtros_activos:
        st.sidebar.info("📊 Mostrando todos los datos disponibles")
        return df.copy(), False
    
    st.sidebar.success("✅ Filtros Activados")
    df_filtrado = df.copy()
    
    # Filtro de fecha
    if 'fecha' in df.columns:
        fecha_col = pd.to_datetime(df['fecha'], errors='coerce')
        valid_dates = fecha_col.dropna()
        
        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
            
            date_range = st.sidebar.date_input(
                "📅 Rango de fechas",
                value=[min_date, max_date],
                min_value=min_date,
                max_value=max_date,
                key="fecha_abarrotes"
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                mask = (fecha_col.dt.date >= start_date) & (fecha_col.dt.date <= end_date)
                df_filtrado = df_filtrado[mask]
    
    # Filtros geográficos
    filtros_geo = ['comuna', 'barrio', 'nodo']
    for filtro in filtros_geo:
        if filtro in df.columns:
            valores = ["Todos"] + sorted(df[filtro].dropna().unique().astype(str))
            seleccion = st.sidebar.selectbox(
                f"🏢 {filtro.capitalize()}",
                valores,
                key=f"{filtro}_abarrotes"
            )
            
            if seleccion != "Todos":
                df_filtrado = df_filtrado[df_filtrado[filtro].astype(str) == seleccion]
    
    # Filtro por nivel de satisfacción
    st.sidebar.subheader("📊 Filtro por Satisfacción")
    satisfaccion_minima = st.sidebar.slider(
        "Satisfacción mínima promedio",
        min_value=1.0,
        max_value=5.0,
        value=1.0,
        step=0.1,
        key="satisfaccion_min_abarrotes"
    )
    
    # Aplicar filtro de satisfacción
    abarrotes_cols = ['9fecha_vencimiento', '10tipo_empaque', '11productos_iguales_lista_mercado']
    available_cols = [col for col in abarrotes_cols if col in df_filtrado.columns]
    
    if available_cols:
        for col in available_cols:
            df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors='coerce')
        
        df_filtrado['satisfaccion_abarrotes_promedio'] = df_filtrado[available_cols].mean(axis=1, skipna=True)
        df_filtrado = df_filtrado[df_filtrado['satisfaccion_abarrotes_promedio'] >= satisfaccion_minima]
    
    return df_filtrado, True

def render_metricas_generales(df):
    """Renderiza métricas generales de abarrotes"""
    st.header("📊 Métricas Generales de Abarrotes")
    
    abarrotes_cols = {
        '9fecha_vencimiento': 'Fecha de vencimiento',
        '10tipo_empaque': 'Tipo de empaque',
        '11productos_iguales_lista_mercado': 'Correspondencia con lista'
    }
    
    available_cols = [col for col in abarrotes_cols.keys() if col in df.columns]
    
    if not available_cols:
        st.warning("No se encontraron datos de satisfacción de abarrotes")
        return
    
    # Convertir a numérico
    for col in available_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Calcular métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_respuestas = df[available_cols].count().sum()
        st.metric("📝 Total Respuestas", total_respuestas)
    
    with col2:
        satisfaccion_general = df[available_cols].mean().mean()
        delta_general = satisfaccion_general - 3.0  # Delta respecto al punto neutral
        st.metric(
            "⭐ Satisfacción General", 
            f"{satisfaccion_general:.2f}/5",
            delta=f"{delta_general:+.2f}"
        )
    
    with col3:
        # Porcentaje de respuestas positivas (≥4)
        respuestas_positivas = (df[available_cols] >= 4).sum().sum()
        porcentaje_positivo = (respuestas_positivas / total_respuestas * 100) if total_respuestas > 0 else 0
        st.metric("👍 Respuestas Positivas", f"{porcentaje_positivo:.1f}%")
    
    with col4:
        # Respuestas críticas (≤2)
        respuestas_criticas = (df[available_cols] <= 2).sum().sum()
        porcentaje_critico = (respuestas_criticas / total_respuestas * 100) if total_respuestas > 0 else 0
        st.metric("🚨 Respuestas Críticas", f"{porcentaje_critico:.1f}%")

def render_analisis_satisfaccion(df):
    """Renderiza análisis detallado de satisfacción"""
    st.header("📈 Análisis Detallado de Satisfacción")
    
    abarrotes_cols_map = {
        '9fecha_vencimiento': 'Fecha de vencimiento de abarrotes',
        '10tipo_empaque': 'Tipo de empaque de abarrotes',
        '11productos_iguales_lista_mercado': 'Correspondencia con lista de mercado'
    }
    
    available_cols = [col for col in abarrotes_cols_map.keys() if col in df.columns]
    
    if not available_cols:
        st.warning("No se encontraron datos de satisfacción válidos para Abarrotes.")
        return
    
    # Crear tabs para diferentes vistas
    tab1, tab2, tab3 = st.tabs(["📊 Distribución Individual", "🔗 Análisis Comparativo", "📈 Tendencias"])
    
    with tab1:
        st.subheader("Distribución de Satisfacción por Aspecto")
        
        # Mostrar gráficos en grid (2 columnas)
        for i in range(0, len(available_cols), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                col_key = available_cols[i]
                description = abarrotes_cols_map[col_key]
                try:
                    fig = plot_question_satisfaction(df, col_key, description)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info(f"No hay datos suficientes para {description}")
                except Exception as e:
                    st.error(f"Error al graficar {description}: {str(e)}")
            
            # Segunda columna si existe
            if i + 1 < len(available_cols):
                with col2:
                    col_key = available_cols[i + 1]
                    description = abarrotes_cols_map[col_key]
                    try:
                        fig = plot_question_satisfaction(df, col_key, description)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info(f"No hay datos suficientes para {description}")
                    except Exception as e:
                        st.error(f"Error al graficar {description}: {str(e)}")
    
    with tab2:
        st.subheader("Comparación entre Aspectos de Abarrotes")
        
        # Gráfico de barras comparativo
        satisfaction_means = {}
        for col in available_cols:
            numeric_data = pd.to_numeric(df[col], errors='coerce')
            if numeric_data.notna().any():
                satisfaction_means[abarrotes_cols_map[col]] = numeric_data.mean()
        
        if satisfaction_means:
            comparison_df = pd.DataFrame(list(satisfaction_means.items()), 
                                       columns=['Aspecto', 'Satisfacción Promedio'])
            
            fig = px.bar(
                comparison_df,
                x='Aspecto',
                y='Satisfacción Promedio',
                title="Comparación de Satisfacción por Aspecto",
                color='Satisfacción Promedio',
                color_continuous_scale='RdYlGn',
                range_color=[1, 5],
                text='Satisfacción Promedio'
            )
            
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig.update_layout(
                xaxis_title="Aspectos de Abarrotes",
                yaxis_title="Satisfacción Promedio (1-5)",
                yaxis_range=[1, 5]
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Análisis de correlaciones
            st.subheader("🔗 Correlaciones entre Aspectos")
            
            if len(available_cols) >= 2:
                correlation_data = df[available_cols].apply(pd.to_numeric, errors='coerce').corr()
                
                # Crear heatmap de correlaciones
                fig_corr = px.imshow(
                    correlation_data,
                    text_auto=True,
                    aspect="auto",
                    title="Matriz de Correlación - Aspectos de Abarrotes",
                    color_continuous_scale='RdBu'
                )
                
                # Personalizar etiquetas
                fig_corr.update_xaxes(
                    ticktext=[abarrotes_cols_map[col] for col in correlation_data.columns],
                    tickvals=list(range(len(correlation_data.columns)))
                )
                fig_corr.update_yaxes(
                    ticktext=[abarrotes_cols_map[col] for col in correlation_data.index],
                    tickvals=list(range(len(correlation_data.index)))
                )
                
                st.plotly_chart(fig_corr, use_container_width=True)
                
                # Interpretación de correlaciones
                st.markdown("**Interpretación de Correlaciones:**")
                for i in range(len(available_cols)):
                    for j in range(i+1, len(available_cols)):
                        corr_value = correlation_data.iloc[i, j]
                        col1_name = abarrotes_cols_map[available_cols[i]]
                        col2_name = abarrotes_cols_map[available_cols[j]]
                        
                        if abs(corr_value) > 0.5:
                            direction = "positiva fuerte" if corr_value > 0 else "negativa fuerte"
                            st.write(f"- {col1_name} ↔ {col2_name}: Correlación {direction} ({corr_value:.3f})")
                        elif abs(corr_value) > 0.3:
                            direction = "positiva moderada" if corr_value > 0 else "negativa moderada"
                            st.write(f"- {col1_name} ↔ {col2_name}: Correlación {direction} ({corr_value:.3f})")
    
    with tab3:
        st.subheader("📈 Tendencias Temporales")
        
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            df_con_fecha = df.dropna(subset=['fecha'])
            
            if not df_con_fecha.empty:
                # Crear serie temporal por mes
                df_con_fecha['mes'] = df_con_fecha['fecha'].dt.to_period('M')
                
                # Calcular satisfacción promedio por mes para cada aspecto
                monthly_data = []
                for col in available_cols:
                    col_name = abarrotes_cols_map[col]
                    numeric_data = pd.to_numeric(df_con_fecha[col], errors='coerce')
                    monthly_avg = df_con_fecha.groupby('mes')[col].apply(
                        lambda x: pd.to_numeric(x, errors='coerce').mean()
                    ).reset_index()
                    monthly_avg['Aspecto'] = col_name
                    monthly_avg['mes_str'] = monthly_avg['mes'].astype(str)
                    monthly_data.append(monthly_avg)
                
                if monthly_data:
                    trends_df = pd.concat(monthly_data)
                    
                    fig_trend = px.line(
                        trends_df,
                        x='mes_str',
                        y=col,
                        color='Aspecto',
                        title="Evolución de Satisfacción en el Tiempo",
                        markers=True
                    )
                    
                    fig_trend.update_layout(
                        xaxis_title="Mes",
                        yaxis_title="Satisfacción Promedio",
                        yaxis_range=[1, 5]
                    )
                    
                    st.plotly_chart(fig_trend, use_container_width=True)
                else:
                    st.info("No hay suficientes datos temporales para mostrar tendencias")
            else:
                st.info("No hay datos con fechas válidas para análisis temporal")
        else:
            st.info("No hay columna de fecha disponible para análisis temporal")

def render_analisis_comedores_problematicos(df):
    """Renderiza análisis de comedores problemáticos mejorado"""
    st.header("⚠️ Análisis de Comedores con Insatisfacción")
    
    # Buscar columna de identificación del comedor
    id_comedor_candidates = ['nombre_comedor', 'comedor', 'id_comedor', 'nombre del comedor']
    id_comedor_col = next((col for col in id_comedor_candidates if col in df.columns), None)
    
    abarrotes_cols = ['9fecha_vencimiento', '10tipo_empaque', '11productos_iguales_lista_mercado']
    available_cols = [col for col in abarrotes_cols if col in df.columns]
    
    if not available_cols:
        st.warning("No hay columnas de satisfacción disponibles")
        return
    
    if not id_comedor_col:
        st.warning("No se encontró columna de identificación del comedor")
        return
    
    # Convertir a numérico
    for col in available_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Identificar comedores con problemas
    comedores_problematicos = {}
    
    for col in available_cols:
        # Identificar respuestas de insatisfacción (≤2)
        insatisfaccion_mask = df[col] <= 2
        
        if insatisfaccion_mask.any():
            insatisfacciones = df[insatisfaccion_mask].groupby(id_comedor_col).size()
            
            for comedor, count in insatisfacciones.items():
                if comedor not in comedores_problematicos:
                    comedores_problematicos[comedor] = {}
                
                col_name = COL_DESCRIPTIONS.get(col, col)
                comedores_problematicos[comedor][col_name] = count
    
    if not comedores_problematicos:
        st.success("✅ No se encontraron comedores con reportes de insatisfacción en abarrotes")
        return
    
    # Convertir a DataFrame
    resultado_df = pd.DataFrame.from_dict(comedores_problematicos, orient='index').fillna(0)
    resultado_df['Total Insatisfacciones'] = resultado_df.sum(axis=1)
    resultado_df = resultado_df.sort_values('Total Insatisfacciones', ascending=False)
    
    # Crear tabs para diferentes vistas
    tab1, tab2, tab3 = st.tabs(["📊 Ranking de Comedores", "🎯 Mapa de Calor", "📋 Plan de Acción"])
    
    with tab1:
        st.subheader("Comedores con Mayor Número de Reportes")
        
        # Mostrar tabla
        st.dataframe(resultado_df, use_container_width=True)
        
        # Gráfico de barras de top comedores problemáticos
        top_comedores = resultado_df.head(10)
        
        fig_comedores = px.bar(
            x=top_comedores['Total Insatisfacciones'],
            y=top_comedores.index,
            orientation='h',
            title="Top 10 Comedores con Más Reportes de Insatisfacción",
            labels={'x': 'Número de Reportes', 'y': 'Comedor'},
            color=top_comedores['Total Insatisfacciones'],
            color_continuous_scale='Reds'
        )
        
        fig_comedores.update_layout(height=400)
        st.plotly_chart(fig_comedores, use_container_width=True)
    
    with tab2:
        st.subheader("Mapa de Calor - Problemas por Comedor y Aspecto")
        
        # Preparar datos para heatmap (solo aspectos, sin total)
        heatmap_data = resultado_df.drop('Total Insatisfacciones', axis=1)
        
        if not heatmap_data.empty:
            fig_heatmap = px.imshow(
                heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                aspect="auto",
                title="Intensidad de Problemas por Comedor y Aspecto",
                color_continuous_scale='Reds',
                text_auto=True
            )
            
            fig_heatmap.update_layout(
                xaxis_title="Aspectos de Abarrotes",
                yaxis_title="Comedores"
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tab3:
        st.subheader("Plan de Acción Recomendado")
        
        # Análisis por nivel de criticidad
        criticos = resultado_df[resultado_df['Total Insatisfacciones'] >= 5]
        atencion = resultado_df[(resultado_df['Total Insatisfacciones'] >= 2) & 
                               (resultado_df['Total Insatisfacciones'] < 5)]
        seguimiento = resultado_df[resultado_df['Total Insatisfacciones'] == 1]
        
        if not criticos.empty:
            st.error("🔴 **COMEDORES CRÍTICOS** (≥5 reportes)")
            for comedor, row in criticos.head(5).iterrows():
                st.markdown(f"- **{comedor}**: {int(row['Total Insatisfacciones'])} reportes")
                
                # Aspectos más problemáticos
                aspectos_problematicos = [asp for asp, val in row.items() 
                                        if asp != 'Total Insatisfacciones' and val > 0]
                if aspectos_problematicos:
                    st.markdown(f"  - Aspectos críticos: {', '.join(aspectos_problematicos)}")
            
            st.markdown("""
            **Acciones inmediatas requeridas:**
            - Visita presencial para evaluación
            - Revisión completa del proceso de entrega
            - Capacitación específica al personal
            """)
        
        if not atencion.empty:
            st.warning("🟡 **COMEDORES REQUIEREN ATENCIÓN** (2-4 reportes)")
            st.markdown(f"Total: {len(atencion)} comedores")
            st.markdown("""
            **Acciones recomendadas:**
            - Seguimiento telefónico quincenal
            - Verificación de mejoras implementadas
            """)
        
        if not seguimiento.empty:
            st.info("🟢 **COMEDORES EN SEGUIMIENTO** (1 reporte)")
            st.markdown(f"Total: {len(seguimiento)} comedores")
            st.markdown("**Acción:** Monitoreo mensual preventivo")

def render_recomendaciones_especificas(df):
    """Renderiza recomendaciones específicas con visualizaciones"""
    st.header("🎯 Recomendaciones Estratégicas para Abarrotes")
    
    abarrotes_cols_map = {
        '9fecha_vencimiento': 'Fecha de vencimiento',
        '10tipo_empaque': 'Tipo de empaque',
        '11productos_iguales_lista_mercado': 'Correspondencia con lista'
    }
    
    available_cols = [col for col in abarrotes_cols_map.keys() if col in df.columns]
    
    if not available_cols:
        st.info("No hay datos suficientes para generar recomendaciones")
        return
    
    # Calcular scores por aspecto
    aspect_scores = {}
    for col in available_cols:
        numeric_data = pd.to_numeric(df[col], errors='coerce')
        if numeric_data.notna().any():
            aspect_scores[col] = numeric_data.mean()
    
    if not aspect_scores:
        st.info("No se pudieron calcular scores de satisfacción")
        return
    
    # Crear visualización de prioridades
    priority_data = []
    for col, score in aspect_scores.items():
        aspect_name = abarrotes_cols_map[col]
        
        if score <= 2.5:
            priority = "Crítico"
            color = "#FF4B4B"
        elif score <= 3.5:
            priority = "Atención"
            color = "#FFA500"
        else:
            priority = "Mantener"
            color = "#00CC66"
        
        priority_data.append({
            'Aspecto': aspect_name,
            'Satisfacción': score,
            'Prioridad': priority,
            'Color': color
        })
    
    priority_df = pd.DataFrame(priority_data)
    
    # Gráfico de prioridades
    fig_priority = px.scatter(
        priority_df,
        x='Aspecto',
        y='Satisfacción',
        color='Prioridad',
        size=[1]*len(priority_df),  # Tamaño uniforme
        title="Matriz de Prioridades - Abarrotes",
        color_discrete_map={'Crítico': '#FF4B4B', 'Atención': '#FFA500', 'Mantener': '#00CC66'}
    )
    
    # Agregar líneas de referencia
    fig_priority.add_hline(y=2.5, line_dash="dash", line_color="red", 
                          annotation_text="Línea Crítica (2.5)")
    fig_priority.add_hline(y=3.5, line_dash="dash", line_color="orange", 
                          annotation_text="Línea de Atención (3.5)")
    
    fig_priority.update_layout(
        yaxis_range=[1, 5],
        yaxis_title="Satisfacción Promedio",
        showlegend=True
    )
    
    st.plotly_chart(fig_priority, use_container_width=True)
    
    # Plan de acción detallado
    st.subheader("📋 Plan de Acción Detallado")
    
    # Organizar por prioridad
    criticos = priority_df[priority_df['Prioridad'] == 'Crítico']
    atencion = priority_df[priority_df['Prioridad'] == 'Atención']
    mantener = priority_df[priority_df['Prioridad'] == 'Mantener']
    
    # Recomendaciones específicas por aspecto
    recomendaciones = {
        'Fecha de vencimiento': {
            'critico': [
                "🔴 Auditoría inmediata de procesos de almacenamiento",
                "🔄 Implementar sistema FIFO (First In, First Out)",
                "📊 Monitoreo diario de fechas de vencimiento",
                "🤝 Renegociar términos con proveedores"
            ],
            'atencion': [
                "📈 Mejorar rotación de inventario",
                "📋 Capacitación en manejo de fechas",
                "⏰ Alertas automáticas de vencimiento"
            ],
            'mantener': [
                "✅ Documentar buenas prácticas actuales",
                "📚 Compartir metodología con otros productos"
            ]
        },
        'Tipo de empaque': {
            'critico': [
                "🔍 Evaluación completa de proveedores",
                "📝 Nuevas especificaciones de empaque",
                "🧪 Pruebas de calidad intensivas",
                "💼 Búsqueda de proveedores alternativos"
            ],
            'atencion': [
                "📊 Monitoreo de calidad de empaque",
                "🎯 Establecer estándares más claros",
                "🔧 Mejoras incrementales"
            ],
            'mantener': [
                "✅ Mantener estándares actuales",
                "📈 Monitoreo de satisfacción continuo"
            ]
        },
        'Correspondencia con lista': {
            'critico': [
                "🔄 Revisión completa del proceso de verificación",
                "👥 Capacitación intensiva al personal",
                "📱 Sistema de verificación digital",
                "🎯 Implementar doble verificación"
            ],
            'atencion': [
                "📋 Mejorar comunicación compras-distribución",
                "🔍 Verificación antes del envío",
                "📊 Seguimiento de errores"
            ],
            'mantener': [
                "📚 Documentar proceso como buena práctica",
                "🎓 Entrenamiento a nuevo personal"
            ]
        }
    }
    
    # Mostrar recomendaciones por prioridad
    if not criticos.empty:
        st.error("🔴 **ACCIÓN INMEDIATA REQUERIDA**")
        for _, row in criticos.iterrows():
            aspect = row['Aspecto']
            score = row['Satisfacción']
            
            with st.expander(f"🚨 {aspect} - Satisfacción: {score:.2f}/5"):
                for recom in recomendaciones.get(aspect, {}).get('critico', []):
                    st.markdown(f"- {recom}")
    
    if not atencion.empty:
        st.warning("🟡 **REQUIERE ATENCIÓN**")
        for _, row in atencion.iterrows():
            aspect = row['Aspecto']
            score = row['Satisfacción']
            
            with st.expander(f"⚠️ {aspect} - Satisfacción: {score:.2f}/5"):
                for recom in recomendaciones.get(aspect, {}).get('atencion', []):
                    st.markdown(f"- {recom}")
    
    if not mantener.empty:
        st.success("🟢 **MANTENER ESTÁNDARES**")
        for _, row in mantener.iterrows():
            aspect = row['Aspecto']
            score = row['Satisfacción']
            
            with st.expander(f"✅ {aspect} - Satisfacción: {score:.2f}/5"):
                for recom in recomendaciones.get(aspect, {}).get('mantener', []):
                    st.markdown(f"- {recom}")

def main():
    """Función principal de la página"""
    # Título y descripción
    st.title("📦 Análisis de Satisfacción - Abarrotes")
    st.markdown("""
    Esta sección presenta el análisis completo y detallado de la satisfacción con los abarrotes entregados,
    incluyendo fechas de vencimiento, tipo de empaque y correspondencia con la lista de mercado.
    """)
    
    # Cargar datos
    df = load_data()
    
    if df is None or df.empty:
        st.error("❌ No se pudieron cargar los datos iniciales desde load_data()")
        st.stop()
    
    # Aplicar filtros
    df_filtrado, filtros_aplicados = render_filtros_mejorados(df)
    
    if df_filtrado.empty:
        st.warning("⚠️ No se encontraron registros con los filtros seleccionados")
        st.info("💡 Intenta ajustar los filtros o desactivarlos para ver todos los datos")
        return
    
    # Mostrar información de filtrado
    if filtros_aplicados:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Datos Originales", len(df))
        with col2:
            st.metric("🔍 Datos Filtrados", len(df_filtrado))
        with col3:
            porcentaje = (len(df_filtrado) / len(df)) * 100 if len(df) > 0 else 0
            st.metric("📈 % Datos Mostrados", f"{porcentaje:.1f}%")
    else:
        st.info(f"📊 Mostrando todos los datos disponibles: {len(df_filtrado)} registros")
    
    # Separador
    st.markdown("---")
    
    # Renderizar secciones principales
    try:
        # 1. Métricas generales
        render_metricas_generales(df_filtrado)
        
        # 2. Análisis detallado de satisfacción
        render_analisis_satisfaccion(df_filtrado)
        
        # 3. Análisis de comedores problemáticos
        render_analisis_comedores_problematicos(df_filtrado)
        
        # 4. Recomendaciones específicas
        render_recomendaciones_especificas(df_filtrado)
        
    except Exception as e:
        st.error(f"❌ Error en el análisis: {str(e)}")
        st.info("🔧 Por favor, verifica la integridad de los datos o contacta al administrador")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 14px;'>
        <p>📊 Dashboard de Análisis de Satisfacción | Sección: Abarrotes</p>
        <p>🕐 Última actualización: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
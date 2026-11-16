import streamlit as st
import pandas as pd
import altair as alt

st.title("Explorar los datos")

# --- R1: Cargar los datos en la primera página ---
# Control 1: st.file_uploader
archivo_subido = st.file_uploader(
    "Selecciona bicicletas_listas.csv",
    type=["csv"]
)

# Control 2: st.button
if st.button("Cargar datos", type="primary"):
    if archivo_subido is not None:
        # Leer CSV con coma, UTF-8 con BOM y parseo de fecha
        df_cargado = pd.read_csv(
            archivo_subido,
            sep=",",
            encoding="utf-8-sig",
            parse_dates=["fecha"]
        )
        st.session_state.df = df_cargado
        st.success(f"{len(df_cargado):,} registros cargados.".replace(",", "."))
    else:
        st.warning("Por favor, selecciona primero el archivo bicicletas_listas.csv.")

# Verificar si hay datos cargados antes de calcular resultados (R1)
if st.session_state.df is None:
    st.info("👈 Sube el archivo **bicicletas_listas.csv** y pulsa **Cargar datos** para comenzar.")
    st.stop()

# Mostrar confirmación persistente si ya estaba cargado
st.caption(f"Base activa: {len(st.session_state.df):,} registros cargados.".replace(",", "."))

# --- Aplicar filtros compartidos (R3) ---
df_filtrado = st.session_state.df.copy()

# Filtro de tipo de día
if st.session_state.tipo_dia != "Todos":
    df_filtrado = df_filtrado[df_filtrado["tipo_dia"] == st.session_state.tipo_dia]

# Filtro de rango de horas (incluye ambos extremos)
hora_min, hora_max = st.session_state.rango_horas
df_filtrado = df_filtrado[
    (df_filtrado["hora"] >= hora_min) & (df_filtrado["hora"] <= hora_max)
]

# Selección de columna según tipo de usuario
mapa_columnas = {
    "Todos": "alquileres_total",
    "Ocasionales": "alquileres_ocasionales",
    "Registrados": "alquileres_registrados"
}
col_alquileres = mapa_columnas[st.session_state.tipo_usuario]
df_filtrado["alquileres"] = df_filtrado[col_alquileres]

# --- R4: Mostrar dos indicadores ---
total_alquileres = int(df_filtrado["alquileres"].sum())
promedio_hora = df_filtrado["alquileres"].mean() if len(df_filtrado) > 0 else 0.0

col1, col2 = st.columns(2)
with col1:
    st.metric(
        label="Total de alquileres",
        value=f"{total_alquileres:,}".replace(",", ".")
    )
with col2:
    st.metric(
        label="Promedio por hora observada",
        value=f"{promedio_hora:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

# --- R2: Dos pestañas en la primera página ---
tab_grafico, tab_datos = st.tabs(["Gráfico diario", "Datos"])

# --- R4: Pestaña Gráfico diario ---
with tab_grafico:
    if len(df_filtrado) > 0:
        df_diario = (
            df_filtrado.groupby("fecha", as_index=False)["alquileres"]
            .sum()
            .rename(columns={"alquileres": "Alquileres por día"})
        )
        
        grafico_linea = (
            alt.Chart(df_diario)
            .mark_line(color="#197A8D")
            .encode(
                x=alt.X("fecha:T", title="Fecha"),
                y=alt.Y("Alquileres por día:Q", title="Alquileres por día"),
                tooltip=[
                    alt.Tooltip("fecha:T", title="Fecha", format="%Y-%m-%d"),
                    alt.Tooltip("Alquileres por día:Q", title="Alquileres", format=",")
                ]
            )
            .properties(height=380)
        )
        st.altair_chart(grafico_linea, use_container_width=True)
    else:
        st.warning("No hay registros que coincidan con los filtros seleccionados.")

# --- R5: Pestaña Datos ---
with tab_datos:
    # Mostrar tabla interactiva (formateando fecha solo para vista limpia)
    df_vista = df_filtrado.copy()
    df_vista["fecha"] = df_vista["fecha"].dt.strftime("%Y-%m-%d")
    
    st.dataframe(df_vista, use_container_width=True)
    
    # Control 6: st.download_button
    csv_descarga = df_vista.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Descargar datos filtrados",
        data=csv_descarga,
        file_name="bicicletas_filtradas.csv",
        mime="text/csv"
    )
    
    st.markdown(
        "Fanaee-T, H. (2013). *Bike Sharing* [Conjunto de datos]. "
        "UCI Machine Learning Repository. https://doi.org/10.24432/C5W894. Licencia CC BY 4.0."
    )
    
    # Control 7: st.link_button
    st.link_button(
        label="Consultar la fuente en UCI",
        url="https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset"
    )
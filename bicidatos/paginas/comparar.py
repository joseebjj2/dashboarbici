import streamlit as st
import pandas as pd
import altair as alt

st.title("Comparar horarios")

# Verificar si los datos están cargados (R1 / R2)
if st.session_state.df is None:
    st.info("👈 Ve a la página **Explorar los datos**, sube el archivo CSV y pulsa **Cargar datos** para comenzar.")
    st.stop()

# --- Aplicar filtros compartidos (R3) ---
df_filtrado = st.session_state.df.copy()

if st.session_state.tipo_dia != "Todos":
    df_filtrado = df_filtrado[df_filtrado["tipo_dia"] == st.session_state.tipo_dia]

hora_min, hora_max = st.session_state.rango_horas
df_filtrado = df_filtrado[
    (df_filtrado["hora"] >= hora_min) & (df_filtrado["hora"] <= hora_max)
]

mapa_columnas = {
    "Todos": "alquileres_total",
    "Ocasionales": "alquileres_ocasionales",
    "Registrados": "alquileres_registrados"
}
col_alquileres = mapa_columnas[st.session_state.tipo_usuario]
df_filtrado["alquileres"] = df_filtrado[col_alquileres]

if len(df_filtrado) == 0:
    st.warning("No hay registros que coincidan con los filtros seleccionados.")
    st.stop()

# --- R6: Dibujar el promedio de alquileres de cada hora ---
# Control 8: st.color_picker
color_barras = st.color_picker("Color de las barras", value="#197A8D")

# Agrupar por hora y calcular promedio
df_horas = (
    df_filtrado.groupby("hora", as_index=False)["alquileres"]
    .mean()
    .rename(columns={"alquileres": "promedio"})
    .sort_values("hora")
)

grafico_barras = (
    alt.Chart(df_horas)
    .mark_bar(color=color_barras)
    .encode(
        x=alt.X("hora:O", title="Hora del día", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("promedio:Q", title="Alquileres por hora observada"),
        tooltip=[
            alt.Tooltip("hora:O", title="Hora"),
            alt.Tooltip("promedio:Q", title="Promedio", format=".1f")
        ]
    )
    .properties(height=360)
)
st.altair_chart(grafico_barras, use_container_width=True)

# Control 9: st.checkbox
mostrar_tabla = st.checkbox("Mostrar tabla de promedios")
if mostrar_tabla:
    df_tabla_promedios = df_horas.copy()
    df_tabla_promedios["Hora formateada"] = df_tabla_promedios["hora"].apply(lambda h: f"{int(h):02d}:00")
    df_tabla_promedios["Promedio"] = df_tabla_promedios["promedio"].round(2)
    st.dataframe(
        df_tabla_promedios[["Hora formateada", "Promedio"]],
        use_container_width=True,
        hide_index=True
    )

st.divider()

# --- R7: Identificar las horas cuyo promedio supera el límite ---
# Control 10: st.number_input
limite = st.number_input(
    "Límite de alquileres por hora",
    min_value=0,
    value=250,
    step=10
)

# Filtrar estrictamente mayor que el límite
horas_superan = df_horas[df_horas["promedio"] > limite]["hora"].tolist()
total_horas_con_datos = len(df_horas)

st.metric(
    label="Horarios con promedio mayor que el límite",
    value=f"{len(horas_superan)}/{total_horas_con_datos}"
)

if len(horas_superan) > 0:
    lista_formateada = ", ".join([f"{int(h):02d}:00" for h in horas_superan])
    st.write(f"**Horarios:** {lista_formateada}.")
else:
    st.write("**Horarios:** Ninguno.")
import streamlit as st

st.set_page_config(
    page_title="BiciDatos",
    page_icon="🚲",
    layout="wide"
)

# Inicializar variables de estado si no existen (R1 y R3)
if "df" not in st.session_state:
    st.session_state.df = None
if "tipo_usuario" not in st.session_state:
    st.session_state.tipo_usuario = "Todos"
if "tipo_dia" not in st.session_state:
    st.session_state.tipo_dia = "Todos"
if "rango_horas" not in st.session_state:
    st.session_state.rango_horas = (0, 23)

# Definir las dos páginas (R2)
pagina_explorar = st.Page(
    "paginas/explorar.py",
    title="Explorar los datos",
    default=True
)
pagina_comparar = st.Page(
    "paginas/comparar.py",
    title="Comparar horarios"
)

# Configurar la navegación multipágina (R2)
pg = st.navigation([pagina_explorar, pagina_comparar])

# Barra lateral compartida (R3)
with st.sidebar:
    st.title("BiciDatos")
    st.divider()
    
    # Control 3: st.selectbox
    st.session_state.tipo_usuario = st.selectbox(
        "Tipo de usuario",
        options=["Todos", "Ocasionales", "Registrados"],
        index=["Todos", "Ocasionales", "Registrados"].index(st.session_state.tipo_usuario)
    )
    
    # Control 4: st.radio
    st.session_state.tipo_dia = st.radio(
        "Tipo de día",
        options=["Todos", "Laborable", "No laborable"],
        index=["Todos", "Laborable", "No laborable"].index(st.session_state.tipo_dia)
    )
    
    # Control 5: st.slider
    st.session_state.rango_horas = st.slider(
        "Horas del día",
        min_value=0,
        max_value=23,
        value=st.session_state.rango_horas
    )

# Ejecutar la página seleccionada
pg.run()
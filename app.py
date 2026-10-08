import os
import time
import sqlite3
import base64
import pandas as pd
import streamlit as st
import plotly.express as px

# CONFIGURAÇÃO
st.set_page_config(
    page_title="RTS | Fleet Intelligence",
    page_icon="🚚",
    layout="wide"
)

LOGO_PATH = r"C:\Users\mateus_s_cavalheiro\Documents\GitHub\dashboard\assets\logo.svg"
BANNER_PATH = r"C:\Users\mateus_s_cavalheiro\Documents\GitHub\dashboard\assets\banner.png"

# ESTILO
st.markdown("""
<style>
.stApp {background:#F4F6FA}
[data-testid="stSidebar"] {background:#111C2E}
[data-testid="stSidebar"] * {color:#F1F5F9}
[data-testid="stSidebar"] [data-baseweb="select"] * {color:#111827}
.block-container {padding-top:1.5rem; max-width:1500px}
.header {
    background:linear-gradient(120deg,#14243A,#203D60);
    padding:24px 28px; border-radius:12px; color:white;
    margin-bottom:20px;
}
.header h1 {color:white; margin:0; font-size:28px}
.header p {color:#CBD5E1; margin:6px 0 0}
div[data-testid="stMetric"] {
    background:white; border:1px solid #E2E8F0;
    border-radius:10px; padding:12px
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background:white; border-radius:12px;
    border-color:#E2E8F0
}
</style>
""", unsafe_allow_html=True)


# EXIBIR LOGO SVG OU IMAGEM
def mostrar_imagem(caminho, largura=180):
    if not os.path.isfile(caminho):
        st.warning(f"Imagem não encontrada: {caminho}")
        return

    if caminho.lower().endswith(".svg"):
        with open(caminho, "rb") as arquivo:
            codigo = base64.b64encode(arquivo.read()).decode()

        st.markdown(
            f'<img src="data:image/svg+xml;base64,{codigo}" '
            f'width="{largura}">',
            unsafe_allow_html=True
        )
    else:
        st.image(caminho, width=largura)


# BANCO DE DADOS
@st.cache_data(ttl=1)
def carregar_telemetria(limite):
    try:
        with sqlite3.connect("telemetria.db", timeout=10) as conn:
            df = pd.read_sql_query("""
                SELECT timestamp, veiculo, velocidade,
                       combustivel, temperatura, bateria
                FROM telemetria_veiculos
                ORDER BY id DESC LIMIT ?
            """, conn, params=(limite,))

        if not df.empty:
            df["timestamp"] = pd.to_datetime(
                df["timestamp"], errors="coerce"
            )
            for c in ["velocidade", "combustivel", "temperatura", "bateria"]:
                df[c] = pd.to_numeric(df[c], errors="coerce")
            df = df.dropna(subset=["timestamp", "veiculo"])
            df = df.sort_values("timestamp")

        return df

    except (sqlite3.Error, pd.errors.DatabaseError):
        return pd.DataFrame()


def avaliar(row):
    problemas = []
    if pd.notna(row["temperatura"]) and row["temperatura"] >= 90:
        problemas.append("Temperatura elevada")
    if pd.notna(row["combustivel"]) and row["combustivel"] <= 20:
        problemas.append("Combustível baixo")
    if pd.notna(row["bateria"]) and row["bateria"] <= 20:
        problemas.append("Bateria baixa")
    return problemas


# BARRA LATERAL
with st.sidebar:
    mostrar_imagem(LOGO_PATH, 180)
    st.markdown("---")
    st.subheader("Controles")

    intervalo = st.slider("Atualização (segundos)", 1, 10, 2)
    limite = st.slider("Histórico de leituras", 30, 1000, 240, 30)

    df = carregar_telemetria(limite)

    st.markdown("---")
    st.subheader("Filtros")

    if not df.empty:
        veiculos = sorted(df["veiculo"].unique())
        selecionado = st.selectbox(
            "Veículo", ["Todos"] + veiculos
        )
        filtrado = (
            df[df["veiculo"] == selecionado].copy()
            if selecionado != "Todos" else df.copy()
        )
    else:
        filtrado = pd.DataFrame()
        st.info("Aguardando dados do simulador.")


# CABEÇALHO PRINCIPAL
st.markdown("""
<div class="header">
    <h1>Fleet Intelligence</h1>
    <p>MONITORAMENTO DE FROTAS | TELEMETRIA OPERACIONAL</p>
</div>
""", unsafe_allow_html=True)

# BANNER LARGO, ABAIXO DO CABEÇALHO
if os.path.isfile(BANNER_PATH):
    st.image(BANNER_PATH, use_container_width=True)

st.markdown("")

if filtrado.empty:
    st.info("Nenhuma telemetria disponível. Verifique o simulador.")

else:
    # ÚLTIMA LEITURA POR VEÍCULO
    ultimos = (
        filtrado.sort_values("timestamp")
        .groupby("veiculo").tail(1)
        .sort_values("veiculo")
        .reset_index(drop=True)
    )

    # INDICADORES
    st.subheader("Visão geral da operação")
    k = st.columns(4)

    k[0].metric("Veículos monitorados", len(ultimos))
    k[1].metric("Velocidade média",
        f"{ultimos['velocidade'].mean():.1f} km/h")
    k[2].metric("Combustível médio",
        f"{ultimos['combustivel'].mean():.1f}%")

    alertas = sum(bool(avaliar(r)) for _, r in ultimos.iterrows())
    k[3].metric("Veículos em atenção", alertas)

    st.markdown("---")
    st.subheader("Estado da frota")

    # CARTÕES
    colunas = st.columns(3)

    for i, (_, r) in enumerate(ultimos.iterrows()):
        with colunas[i % 3]:
            with st.container(border=True):
                st.markdown(f"**🚚 {r['veiculo']}**")
                problemas = avaliar(r)

                if problemas:
                    st.warning(" • ".join(problemas))
                else:
                    st.success("NORMAL")

                a, b = st.columns(2)
                a.metric("Velocidade",
                    f"{r['velocidade']:.1f} km/h")
                b.metric("Combustível",
                    f"{r['combustivel']:.1f}%")

                a, b = st.columns(2)
                a.metric("Temperatura",
                    f"{r['temperatura']:.1f} °C")
                b.metric("Bateria",
                    f"{r['bateria']:.1f}%")

                st.caption(r["timestamp"].strftime("%d/%m/%Y %H:%M:%S"))

    # GRÁFICOS
    st.markdown("---")
    st.subheader("Análise histórica")

    graficos = [
        ("velocidade", "Velocidade ao longo do tempo", "Velocidade (km/h)"),
        ("combustivel", "Nível de combustível", "Combustível (%)"),
        ("temperatura", "Temperatura do motor", "Temperatura (°C)"),
        ("bateria", "Nível de bateria", "Bateria (%)")
    ]

    for inicio in range(0, 4, 2):
        colunas_grafico = st.columns(2)

        for coluna, (campo, titulo, eixo) in zip(
            colunas_grafico, graficos[inicio:inicio + 2]
        ):
            fig = px.line(
                filtrado, x="timestamp", y=campo,
                color="veiculo", title=titulo,
                labels={
                    "timestamp": "Horário",
                    campo: eixo,
                    "veiculo": "Veículo"
                },
                color_discrete_sequence=px.colors.qualitative.Set2
            )

            fig.update_layout(
                template="plotly_white",
                height=330,
                margin=dict(l=10, r=10, t=55, b=10),
                legend=dict(orientation="h", y=1.02)
            )

            if campo in ["combustivel", "bateria"]:
                fig.update_yaxes(range=[0, 100], ticksuffix="%")

            coluna.plotly_chart(fig, use_container_width=True)

    # TABELA E EXPORTAÇÃO
    with st.expander("Histórico completo"):
        tabela = filtrado.sort_values("timestamp", ascending=False)
        st.dataframe(tabela, use_container_width=True, hide_index=True)

        st.download_button(
            "Exportar CSV",
            tabela.to_csv(index=False).encode("utf-8-sig"),
            "historico_telemetria.csv",
            "text/csv"
        )

    # ALERTAS DETALHADOS
    with st.expander("Detalhes dos alertas"):
        linhas = []
        for _, r in ultimos.iterrows():
            for problema in avaliar(r):
                linhas.append({
                    "Veículo": r["veiculo"],
                    "Alerta": problema,
                    "Horário": r["timestamp"].strftime("%d/%m/%Y %H:%M:%S")
                })

        if linhas:
            st.dataframe(pd.DataFrame(linhas), use_container_width=True, hide_index=True)
        else:
            st.success("Nenhum alerta detectado.")

st.markdown("---")
st.caption("RTS | Fleet Intelligence")

time.sleep(intervalo)
st.rerun()
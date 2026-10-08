import os
import time
import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.express as px


# =========================================================
# 1. CONFIGURAÇÕES GERAIS
# =========================================================

st.set_page_config(
    page_title="RTS | Fleet Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. PERSONALIZAÇÃO DE IMAGENS
# =========================================================
# Coloque os caminhos das suas imagens abaixo.
# Exemplo: "assets/logo.png"
# Se o arquivo não existir, o sistema continuará funcionando.

LOGO_PATH = r"C:\Users\mateus_s_cavalheiro\Downloads\Trabalho Telemetria\assets\logo.svg"
BANNER_PATH = r"C:\Users\mateus_s_cavalheiro\Downloads\Trabalho Telemetria\assets\banner.png"

# =========================================================
# 3. IDENTIDADE VISUAL
# =========================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #F4F6FA;
    }

    [data-testid="stSidebar"] {
        background-color: #111C2E;
    }

    [data-testid="stSidebar"] * {
        color: #F1F5F9;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #111827;
    }

    [data-testid="stSidebar"] input {
        color: #111827;
    }

    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2rem;
        max-width: 1600px;
    }

    .main-header {
        background: linear-gradient(120deg, #14243A, #203D60);
        padding: 26px 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        border: 1px solid #2D4665;
    }

    .main-header h1 {
        color: white;
        font-size: 29px;
        font-weight: 800;
        margin: 0;
        padding: 0;
    }

    .main-header p {
        color: #CBD5E1;
        font-size: 14px;
        margin-top: 8px;
        margin-bottom: 0;
    }

    .section-title {
        color: #18283D;
        font-size: 19px;
        font-weight: 700;
        margin-top: 12px;
        margin-bottom: 14px;
    }

    .section-caption {
        color: #64748B;
        font-size: 12px;
        margin-top: -10px;
        margin-bottom: 16px;
    }

    .vehicle-title {
        font-size: 16px;
        font-weight: 700;
        color: #1E293B;
    }

    .vehicle-status {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        padding: 5px 9px;
        border-radius: 20px;
        display: inline-block;
        margin: 8px 0 12px 0;
    }

    .status-normal {
        background: #DCFCE7;
        color: #166534;
    }

    .status-warning {
        background: #FEF3C7;
        color: #92400E;
    }

    .status-critical {
        background: #FEE2E2;
        color: #991B1B;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.025);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748B;
        font-size: 13px;
    }

    div[data-testid="stMetricValue"] {
        color: #172B45;
        font-weight: 700;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white;
        border-radius: 14px;
        border-color: #E2E8F0;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0;
        border-radius: 10px;
    }

    hr {
        border-color: #E2E8F0;
    }

    .footer {
        text-align: center;
        color: #94A3B8;
        font-size: 11px;
        padding-top: 24px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 4. ACESSO AO BANCO DE DADOS
# =========================================================

@st.cache_data(ttl=1)
def carregar_telemetria(limite=1000):
    conn = sqlite3.connect("telemetria.db", timeout=10)

    query = """
        SELECT timestamp, veiculo, velocidade,
               combustivel, temperatura, bateria
        FROM telemetria_veiculos
        ORDER BY id DESC
        LIMIT ?
    """

    try:
        df = pd.read_sql_query(query, conn, params=(int(limite),))
    except (sqlite3.Error, pd.errors.DatabaseError):
        df = pd.DataFrame()
    finally:
        conn.close()

    if not df.empty:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"], errors="coerce"
        )

        colunas_numericas = [
            "velocidade", "combustivel",
            "temperatura", "bateria"
        ]

        for coluna in colunas_numericas:
            df[coluna] = pd.to_numeric(
                df[coluna], errors="coerce"
            )

        df = df.dropna(subset=["timestamp", "veiculo"])
        df = df.sort_values("timestamp")

    return df


# =========================================================
# 5. CLASSIFICAÇÃO DOS VEÍCULOS
# =========================================================
# Limites iniciais para demonstração.
# Ajuste conforme as especificações reais dos veículos.

def avaliar_veiculo(row):
    problemas = []

    if pd.notna(row["temperatura"]) and row["temperatura"] >= 90:
        problemas.append("Temperatura elevada")

    if pd.notna(row["combustivel"]) and row["combustivel"] <= 20:
        problemas.append("Combustível baixo")

    if pd.notna(row["bateria"]) and row["bateria"] <= 20:
        problemas.append("Bateria baixa")

    if any(
        pd.notna(row[coluna]) and row[coluna] < 0
        for coluna in ["velocidade", "combustivel", "bateria"]
    ):
        problemas.append("Leitura fora da faixa")

    if problemas:
        return "ATENÇÃO", problemas

    return "NORMAL", []


# =========================================================
# 6. BARRA LATERAL
# =========================================================

with st.sidebar:
    if os.path.isfile(LOGO_PATH):
        st.image(LOGO_PATH, width=180)
    else:
        st.markdown("## RTS")
        st.caption("FLEET INTELLIGENCE")

    st.markdown("---")
    st.markdown("### CONTROLES")

    intervalo_atualizacao = st.slider(
        "Atualização automática",
        min_value=1,
        max_value=10,
        value=2,
        help="Intervalo em segundos entre atualizações."
    )

    quantidade_registros = st.slider(
        "Quantidade de leituras",
        min_value=30,
        max_value=1000,
        value=240,
        step=30
    )

    st.markdown("---")
    st.markdown("### FILTROS")

    df = carregar_telemetria(quantidade_registros)

    if not df.empty:
        veiculos_disponiveis = sorted(
            df["veiculo"].unique().tolist()
        )

        veiculo_selecionado = st.selectbox(
            "Veículo monitorado",
            ["Todos os veículos"] + veiculos_disponiveis
        )

        if veiculo_selecionado != "Todos os veículos":
            df_filtrado = df[
                df["veiculo"] == veiculo_selecionado
            ].copy()
        else:
            df_filtrado = df.copy()

        st.markdown("---")
        st.caption("RTS • Sistema de telemetria")
        st.caption(
            f"Última atualização: {datetime.now().strftime('%H:%M:%S')}"
        )

    else:
        veiculo_selecionado = "Todos os veículos"
        df_filtrado = pd.DataFrame()
        st.info("Aguardando dados do simulador.")


# =========================================================
# 7. CABEÇALHO PRINCIPAL
# =========================================================

col_logo, col_titulo = st.columns([1, 5])

with col_logo:
    if os.path.isfile(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, width=180)

st.title("🚚 Telemetria de Frota")

if os.path.isfile(BANNER_PATH):
    st.image(BANNER_PATH, use_container_width=True)

with col_titulo:
    st.markdown(
        """
        <div class="main-header">
            <h1>Fleet Intelligence</h1>
            <p>
                CENTRAL DE MONITORAMENTO DE FROTAS |
                TELEMETRIA E DESEMPENHO OPERACIONAL
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if os.path.isfile(BANNER_PATH):
    with st.expander("Imagem institucional da operação", expanded=False):
        st.image(BANNER_PATH, use_container_width=True)


# =========================================================
# 8. PAINEL DE MONITORAMENTO
# =========================================================

if df_filtrado.empty:

    st.warning(
        "Nenhuma telemetria disponível. "
        "Verifique se o simulador está em execução "
        "e se o arquivo telemetria.db está acessível."
    )

else:
    # Última leitura de cada veículo
    ultimos = (
        df_filtrado
        .sort_values("timestamp")
        .groupby("veiculo")
        .tail(1)
        .sort_values("veiculo")
        .reset_index(drop=True)
    )

    total_veiculos = len(ultimos)

    velocidades_validas = ultimos["velocidade"].dropna()
    combustiveis_validos = ultimos["combustivel"].dropna()

    velocidade_media = (
        velocidades_validas.mean()
        if not velocidades_validas.empty else None
    )

    combustivel_medio = (
        combustiveis_validos.mean()
        if not combustiveis_validos.empty else None
    )

    avaliacoes = [
        avaliar_veiculo(row)
        for _, row in ultimos.iterrows()
    ]

    veiculos_atencao = sum(
        status == "ATENÇÃO"
        for status, _ in avaliacoes
    )

    st.markdown(
        '<div class="section-title">Visão geral da operação</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-caption">'
        'Resumo baseado na última leitura disponível de cada veículo.'
        '</div>',
        unsafe_allow_html=True
    )

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric(
        "Veículos monitorados",
        total_veiculos,
        help="Quantidade de veículos com leituras disponíveis."
    )

    kpi2.metric(
        "Velocidade média",
        f"{velocidade_media:.1f} km/h"
        if velocidade_media is not None else "—"
    )

    kpi3.metric(
        "Combustível médio",
        f"{combustivel_medio:.1f}%"
        if combustivel_medio is not None else "—"
    )

    kpi4.metric(
        "Veículos em atenção",
        veiculos_atencao,
        delta=(
            "Verificar" if veiculos_atencao > 0
            else "Sem alertas detectados"
        ),
        delta_color="inverse"
    )

    st.markdown("---")


    # =====================================================
    # 9. CARTÕES INDIVIDUAIS DOS VEÍCULOS
    # =====================================================

    st.markdown(
        '<div class="section-title">Estado da frota</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-caption">'
        'Indicadores individuais e condições que merecem atenção.'
        '</div>',
        unsafe_allow_html=True
    )

    colunas_cartoes = st.columns(3)

    for idx, (_, row) in enumerate(ultimos.iterrows()):
        status, problemas = avaliar_veiculo(row)

        with colunas_cartoes[idx % 3]:
            with st.container(border=True):
                st.markdown(
                    f'<div class="vehicle-title">'
                    f'🚚 {row["veiculo"]}</div>',
                    unsafe_allow_html=True
                )

                classe_status = (
                    "status-warning"
                    if status == "ATENÇÃO"
                    else "status-normal"
                )

                st.markdown(
                    f'<span class="vehicle-status {classe_status}">'
                    f'{status}</span>',
                    unsafe_allow_html=True
                )

                c1, c2 = st.columns(2)

                c1.metric(
                    "Velocidade",
                    f'{row["velocidade"]:.1f} km/h'
                    if pd.notna(row["velocidade"]) else "—"
                )

                c2.metric(
                    "Combustível",
                    f'{row["combustivel"]:.1f}%'
                    if pd.notna(row["combustivel"]) else "—"
                )

                c3, c4 = st.columns(2)

                c3.metric(
                    "Temperatura",
                    f'{row["temperatura"]:.1f} °C'
                    if pd.notna(row["temperatura"]) else "—"
                )

                c4.metric(
                    "Bateria",
                    f'{row["bateria"]:.1f}%'
                    if pd.notna(row["bateria"]) else "—"
                )

                if problemas:
                    st.caption(" • ".join(problemas))
                else:
                    st.caption("Sem alertas pelos limites configurados.")

                st.caption(
                    "Última leitura: "
                    + row["timestamp"].strftime("%d/%m/%Y %H:%M:%S")
                )

    st.markdown("---")


    # =====================================================
    # 10. GRÁFICOS HISTÓRICOS
    # =====================================================

    st.markdown(
        '<div class="section-title">Análise de telemetria</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-caption">'
        'Evolução das métricas no período selecionado.'
        '</div>',
        unsafe_allow_html=True
    )

    cores = px.colors.qualitative.Set2

    layout_grafico = dict(
        template="plotly_white",
        height=340,
        margin=dict(l=15, r=15, t=55, b=15),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        font=dict(
            family="Inter, sans-serif",
            color="#334155",
            size=11
        ),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        fig_velo = px.line(
            df_filtrado,
            x="timestamp",
            y="velocidade",
            color="veiculo",
            color_discrete_sequence=cores,
            title="Velocidade ao longo do tempo",
            labels={
                "timestamp": "Horário",
                "velocidade": "Velocidade (km/h)",
                "veiculo": "Veículo"
            }
        )

        fig_velo.update_layout(**layout_grafico)
        fig_velo.update_traces(line=dict(width=2.5))
        fig_velo.update_yaxes(rangemode="tozero")

        st.plotly_chart(fig_velo, use_container_width=True)

    with col_g2:
        fig_combu = px.line(
            df_filtrado,
            x="timestamp",
            y="combustivel",
            color="veiculo",
            color_discrete_sequence=cores,
            title="Nível de combustível",
            labels={
                "timestamp": "Horário",
                "combustivel": "Combustível (%)",
                "veiculo": "Veículo"
            }
        )

        fig_combu.update_layout(**layout_grafico)
        fig_combu.update_traces(line=dict(width=2.5))
        fig_combu.update_yaxes(range=[0, 100], ticksuffix="%")

        st.plotly_chart(fig_combu, use_container_width=True)

    col_g3, col_g4 = st.columns(2)

    with col_g3:
        fig_temp = px.line(
            df_filtrado,
            x="timestamp",
            y="temperatura",
            color="veiculo",
            color_discrete_sequence=cores,
            title="Temperatura do motor",
            labels={
                "timestamp": "Horário",
                "temperatura": "Temperatura (°C)",
                "veiculo": "Veículo"
            }
        )

        fig_temp.update_layout(**layout_grafico)
        fig_temp.update_traces(line=dict(width=2.5))

        # Referência visual de temperatura elevada
        fig_temp.add_hline(
            y=90,
            line_dash="dash",
            line_color="#DC2626",
            annotation_text="Limite configurado: 90 °C",
            annotation_position="top left"
        )

        st.plotly_chart(fig_temp, use_container_width=True)

    with col_g4:
        fig_bat = px.line(
            df_filtrado,
            x="timestamp",
            y="bateria",
            color="veiculo",
            color_discrete_sequence=cores,
            title="Nível de bateria",
            labels={
                "timestamp": "Horário",
                "bateria": "Bateria (%)",
                "veiculo": "Veículo"
            }
        )

        fig_bat.update_layout(**layout_grafico)
        fig_bat.update_traces(line=dict(width=2.5))
        fig_bat.update_yaxes(range=[0, 100], ticksuffix="%")

        st.plotly_chart(fig_bat, use_container_width=True)


    # =====================================================
    # 11. ALERTAS OPERACIONAIS
    # =====================================================

    st.markdown("---")

    st.markdown(
        '<div class="section-title">Alertas operacionais</div>',
        unsafe_allow_html=True
    )

    lista_alertas = []

    for _, row in ultimos.iterrows():
        status, problemas = avaliar_veiculo(row)

        for problema in problemas:
            lista_alertas.append({
                "Veículo": row["veiculo"],
                "Ocorrência": problema,
                "Valor atual": {
                    "Temperatura elevada": (
                        f'{row["temperatura"]:.1f} °C'
                    ),
                    "Combustível baixo": (
                        f'{row["combustivel"]:.1f}%'
                    ),
                    "Bateria baixa": (
                        f'{row["bateria"]:.1f}%'
                    )
                }.get(problema, "Verificar leitura"),
                "Horário": row["timestamp"].strftime(
                    "%d/%m/%Y %H:%M:%S"
                )
            })

    if lista_alertas:
        df_alertas = pd.DataFrame(lista_alertas)
        st.dataframe(
            df_alertas,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success(
            "Nenhum alerta detectado com os limites atuais."
        )


    # =====================================================
    # 12. HISTÓRICO COMPLETO
    # =====================================================

    with st.expander("Consultar histórico completo de telemetria"):
        df_exibicao = df_filtrado.sort_values(
            "timestamp", ascending=False
        ).copy()

        df_exibicao["timestamp"] = (
            df_exibicao["timestamp"].dt.strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        )

        df_exibicao = df_exibicao.rename(columns={
            "timestamp": "Data e hora",
            "veiculo": "Veículo",
            "velocidade": "Velocidade (km/h)",
            "combustivel": "Combustível (%)",
            "temperatura": "Temperatura (°C)",
            "bateria": "Bateria (%)"
        })

        st.dataframe(
            df_exibicao,
            use_container_width=True,
            hide_index=True
        )

        csv = df_exibicao.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "Exportar histórico em CSV",
            data=csv,
            file_name="historico_telemetria.csv",
            mime="text/csv"
        )


# =========================================================
# 13. RODAPÉ E ATUALIZAÇÃO
# =========================================================

st.markdown(
    """
    <div class="footer">
        RTS FLEET INTELLIGENCE · MONITORAMENTO DE TELEMETRIA
        <br>
        Painel demonstrativo para acompanhamento operacional da frota
    </div>
    """,
    unsafe_allow_html=True
)

time.sleep(intervalo_atualizacao)
st.rerun()
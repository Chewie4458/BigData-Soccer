from math import trunc
from stat import filemode

import numpy as np
import streamlit as st
import pandas as pd
import altair as alt
import api

from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Configura se vai utilizar o merge nas bases
CONFIG_MERGE = True

st.set_page_config(page_title="Big Data Soccer", layout="wide")

# ---------------------------------------------------
# Recupera o dia
ontem = (datetime.now(ZoneInfo("UTC")).date() - timedelta(days=1)).isoformat()

# Recupera o nome do arquivo esperado
filename = Path(f"partidas{ontem}.xlsx")

# Verifica se a base já foi gerada
if not filename.exists():
    # Só gera se não existir
    api.geraBasePartidas(ontem)

# Carrega a base de dados
if CONFIG_MERGE:
    api.mergeBases()
    filename = Path(f"partidas_merged.xlsx")

df = pd.read_excel(filename)

# Cria coluna de identificação da partida
df["Partida"] = df["Casa"] + " x " + df["Visitante"]

# ---------------------------------------------------
# Gerenciar estado (para alternar entre visão geral e detalhes)
if "partida_selecionada" not in st.session_state:
    st.session_state.partida_selecionada = None

# ---------------------------------------------------
# Função: visão geral (estatísticas + cards)
def mostrar_painel_geral():
    st.title("⚽ Big Data Soccer Dashboard")
    st.markdown("### Trabalho de Big Data — Alexandre Filho, Marcela Viana e Pedro Chies")

    # ==========================
    # 🔹 Estatísticas gerais
    # ==========================
    st.subheader("📊 Estatísticas Gerais")

    # Converter datas sem quebrar
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

    # Criar string bonita para exibir
    df["Data_Str"] = df["Data"].dt.strftime("%d/%m/%Y — %H:%M")
    df["Data_Str"] = df["Data_Str"].fillna("Data não disponível")

    df["Acertou_Vencedor"] = df["Prediction_Vencedor"] == df["Vencedor"]

    df["Acertou"] = np.where(
        df["Acertou_Vencedor"],
        "sim",
        "não"
    )

    total_partidas = len(df)
    taxa_acerto = df["Acertou_Vencedor"].mean() * 100
    media_prev_gols_casa = df["Prediction_Gols_Casa"].mean()
    media_prev_gols_visit = df["Prediction_Gols_Visitante"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Partidas", total_partidas)
    col2.metric("Taxa de Acertos (Vencedor)", f"{taxa_acerto:.1f}%")
    col3.metric("Média de Gols Prev. (Casa)", f"{media_prev_gols_casa:.2f}")
    col4.metric("Média de Gols Prev. (Visitante)", f"{media_prev_gols_visit:.2f}")

    # ==========================
    # 🔹 Gráfico de acertos por vencedor previsto
    # ==========================
    st.subheader("🏆 Distribuição de Acertos por Vencedor Previsto")

    chart_resultado = alt.Chart(df).mark_bar().encode(
        x=alt.X("Prediction_Vencedor", title="Vencedor Previsto"),
        y=alt.Y("count()", title="Número de Partidas"),
        color=alt.Color("Acertou:N", title="Acertou?"),
        tooltip=["Prediction_Vencedor", "Vencedor", "Acertou"]
    ).properties(height=400)

    st.altair_chart(chart_resultado, use_container_width=True)

    # ==========================
    # 🔹 Cards interativos
    # ==========================
    st.subheader("🧩 Partidas Disponíveis")

    cols = st.columns(3)
    for i, (_, row) in enumerate(df.iterrows()):
        with cols[i % 3]:
            st.markdown(f"""
            ### {row['Casa']} x {row['Visitante']}
            <small>📅 {row['Data_Str']}</small>
            """, unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if pd.notna(row.get("Logo Casa")):
                    st.image(row["Logo Casa"], width=80)
            with col_b:
                if pd.notna(row.get("Logo Visitante")):
                    st.image(row["Logo Visitante"], width=80)

            st.markdown(f"""
            **Previsão:** {row['Prediction_Gols_Casa']} - {row['Prediction_Gols_Visitante']}  
            **Resultado:** {row['Gols_Casa']} - {row['Gols_Visitante']}
            """)

            if st.button("🔍 Ver detalhes", key=row["Partida"]):
                st.session_state.partida_selecionada = row["Partida"]
                st.rerun()


# ---------------------------------------------------
# Função: tela detalhada da partida
def mostrar_detalhes(partida_nome):
    partida = df[df["Partida"] == partida_nome].iloc[0]

    st.markdown(f"## 🏟️ {partida['Partida']}")
    col1, col2, col3 = st.columns([1,2,1])

    with col1:
        if "Img_Casa" in df.columns and pd.notna(partida["Img_Casa"]):
            st.image(partida["Img_Casa"], width=120)
        st.markdown(f"### {partida['Casa']}")
        st.metric("Previsão de Gols", f"até {trunc(partida["Prediction_Gols_Casa"])}")
        st.metric("Gols Reais", partida["Gols_Casa"])

    with col3:
        if "Img_Visitante" in df.columns and pd.notna(partida["Img_Visitante"]):
            st.image(partida["Img_Visitante"], width=120)
        st.markdown(f"### {partida['Visitante']}")
        st.metric("Previsão de Gols", f"até {trunc(partida["Prediction_Gols_Visitante"])}")
        st.metric("Gols Reais", partida["Gols_Visitante"])

    with col2:
        st.markdown("### Resultado Previsto vs Real")
        st.metric("Previsão de Vencedor", partida["Prediction_Vencedor"])
        st.metric("Vencedor Real", partida["Vencedor"])

        if partida["Prediction_Vencedor"] == partida["Vencedor"]:
            st.success("✅ A previsão de vencedor foi **correta!**")
        else:
            st.error("❌ A previsão de vencedor foi **incorreta.**")

    # --- preparar dataframe ---
    df_gols = pd.DataFrame({
        "Tipo": ["Previsão", "Real"],
        "Mandante": [partida["Prediction_Gols_Casa"], partida["Gols_Casa"]],
        "Visitante": [partida["Prediction_Gols_Visitante"], partida["Gols_Visitante"]],
    }).melt(id_vars="Tipo", var_name="Time", value_name="Gols")

    # garantir que o eixo y comece em 0 e com folga superior para rótulos
    y_max = int(df_gols["Gols"].max() + 2)

    # --- gráfico de barras lado-a-lado (dodged) ---
    bars = alt.Chart(df_gols).mark_bar(size=40).encode(
        x=alt.X("Time:N", title="", axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("Gols:Q", title="Quantidade de Gols", scale=alt.Scale(domain=[0, y_max])),
        color=alt.Color("Tipo:N", title="Tipo"),
        tooltip=[alt.Tooltip("Time:N"), alt.Tooltip("Tipo:N"), alt.Tooltip("Gols:Q")],
        # canal para "deslocar" as barras por categoria (dodged)
        xOffset="Tipo:N"
    ).properties(
        height=400,
        title="Comparação de Gols: Previsão vs Real"
    )

    # rótulos sobre as barras
    labels = alt.Chart(df_gols).mark_text(dy=-10, fontSize=12).encode(
        x=alt.X("Time:N"),
        y=alt.Y("Gols:Q"),
        text=alt.Text("Gols:Q"),
        xOffset="Tipo:N"
    )

    # --- opcional: calcular diferença e mostrar como texto acima do grupo ---
    df_diff = df_gols.pivot(index="Time", columns="Tipo", values="Gols").reset_index()
    df_diff["Diff"] = df_diff["Previsão"] - df_diff["Real"]

    diff_text = alt.Chart(df_diff).mark_text(dy=-40, fontSize=12, fontWeight="bold").encode(
        x=alt.X("Time:N"),
        # posicionar sempre no topo do gráfico (valor fixo)
        y=alt.value(y_max - 0.2),
        text=alt.Text("Diff:Q", format="+d"),  # ex: +2 ou -1
        tooltip=[alt.Tooltip("Time:N"), alt.Tooltip("Diff:Q", title="Previsão − Real")]
    )

    # montar camada final
    chart = (bars + labels + diff_text).configure_title(fontSize=16).configure_legend(
        orient="right"
    )

    st.altair_chart(chart, use_container_width=True)

    # Botão para voltar
    if st.button("⬅️ Voltar para o painel"):
        st.session_state.partida_selecionada = None
        st.rerun()

# ---------------------------------------------------
# Alterna entre as telas
if st.session_state.partida_selecionada:
    mostrar_detalhes(st.session_state.partida_selecionada)
else:
    mostrar_painel_geral()

import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

pd.set_option('display.max_columns', 200)
st.set_page_config(layout='wide')

def run():
    df = pd.read_csv('E0.csv')
    df = df[['Div', 'Date', 'Time', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HTHG', 'HTAG', 'HTR', 'HS', 'AS', 'HST', 'AST', 'HF', 'AF', 'HC', 'AC', 'B365H', 'B365D', 'B365A']]
    # st.table(df)

    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')


    mandante = st.selectbox('Selecione o time mandante', sorted(df['HomeTeam'].unique()))
    visitante = st.selectbox('Selecione o time visitante', sorted(df['AwayTeam'].unique()))

    def pontos(x):
        if x == 'A':
            return 0, 3
        elif x == 'H':
            return 3, 0
        else:
            return 1, 1
        
    def intensidade(row):
        somaMandante = row['FTHG'] + row['HS'] + row['HST'] + row['HC']
        intensidadeMandante = round(somaMandante / 90, 2)
        somaVisitante = row['FTAG'] + row['AS'] + row['AST'] + row['AC']
        intensidadeVisitante = round(somaVisitante / 90, 2)
        return intensidadeMandante, intensidadeVisitante

    df['PontosCasa'], df['PontosVisitante'] = zip(*df['FTR'].apply(pontos))
    df['IntensidadeMandante'], df['IntensidadeVisitante'] = zip(*df.apply(intensidade, axis=1))
    df

    df['PontosCasaAcumulados'] = df.groupby('HomeTeam')['PontosCasa'].cumsum()
    df['FTHGAcumuladoCasa'] = df.groupby('HomeTeam')['FTHG'].cumsum()
    df['FTAGAcumuladoCasa'] = df.groupby('HomeTeam')['FTAG'].cumsum()
    df['FTHGAcumuladoVisitante'] = df.groupby('AwayTeam')['FTHG'].cumsum()
    df['FTAGAcumuladoVisitante'] = df.groupby('AwayTeam')['FTAG'].cumsum()
    df['HSTAcumuladoCasa'] = df.groupby('HomeTeam')['HST'].cumsum()
    df['ASTAcumuladoCasa'] = df.groupby('HomeTeam')['AST'].cumsum()
    df['HSTAcumuladoVisitante'] = df.groupby('AwayTeam')['HST'].cumsum()
    df['ASTAcumuladoVisitante'] = df.groupby('AwayTeam')['AST'].cumsum()
    df['HCAcumuladoCasa'] = df.groupby('HomeTeam')['HC'].cumsum()
    df['ACAcumuladoCasa'] = df.groupby('HomeTeam')['AC'].cumsum()
    df['HCAcumuladoVisitante'] = df.groupby('AwayTeam')['HC'].cumsum()
    df['ACAcumuladoVisitante'] = df.groupby('AwayTeam')['AC'].cumsum()
    df['HSAcumuladoCasa'] = df.groupby('HomeTeam')['HS'].cumsum()
    df['ASAcumuladoCasa'] = df.groupby('HomeTeam')['AS'].cumsum()
    df['HSAcumuladoVisitante'] = df.groupby('AwayTeam')['HS'].cumsum()
    df['ASAcumuladoVisitante'] = df.groupby('AwayTeam')['AS'].cumsum()
    df['IntensidadeMandanteAcumulada'] = df.groupby('HomeTeam')['IntensidadeMandante'].cumsum()
    df['IntensidadeVisitanteAcumulada'] = df.groupby('AwayTeam')['IntensidadeVisitante'].cumsum()
    df['PontosVisitanteAcumulados'] = df.groupby('AwayTeam')['PontosVisitante'].cumsum()
    col1, col2 = st.columns((2))
    pontos_m = df.groupby('HomeTeam')['PontosCasa'].get_group(mandante).sum() + df.groupby('AwayTeam')['PontosVisitante'].get_group(visitante).sum()
    col1.subheader(f'O {mandante} tem {pontos_m} pontos')

    pontos_v = df.groupby('HomeTeam')['PontosCasa'].get_group(visitante).sum() + df.groupby('AwayTeam')['PontosVisitante'].get_group(mandante).sum()
    col2.subheader(f'O {visitante} tem {pontos_v} pontos')
    fig = px.line(df, x='Date', y='PontosCasaAcumulados', color='HomeTeam', title='Pontos Acumulados em Casa')
    fig.update_layout(xaxis_title='Data', yaxis_title='Pontos Acumulados')
    col1.plotly_chart(fig, use_container_width=True,)

    fig = px.line(df, x='Date', y='PontosVisitanteAcumulados', color='AwayTeam', title='Pontos Acumulados como Visitante')
    fig.update_layout(xaxis_title='Data', yaxis_title='Pontos Acumulados')
    col2.plotly_chart(fig, use_container_width=True,)

    def calcular_odds(row):
        if row['FTR'] == 'H':
            return row['B365H'] - 1, -1, -1, -1
        elif row['FTR'] == 'A':
            return -1, -1, row['B365A'] - 1, -1
        else:
            return -1, row['B365D'] - 1, -1, row['B365D'] - 1


    # Supondo que 'df' seja o seu DataFrame
    df['BackCasa'], df['BackCasaEmpate'], df['BackVisitante'], df['BackVisitanteEmpate'] = zip(*df.apply(calcular_odds, axis=1))

    df_m = df[df['HomeTeam'] == mandante]
    df_m_qv = df[df['AwayTeam'] == mandante]
    df_v = df[df['AwayTeam'] == visitante]
    df_v_qm = df[df['HomeTeam'] == visitante]

    fig = px.line(df_m, x='Date', y='PontosCasaAcumulados', title=f'Pontos Acumulados em Casa do {mandante}')
    fig.update_layout(xaxis_title='Data', yaxis_title='Pontos Acumulados')
    col1.plotly_chart(fig, use_container_width=True,)

    fig = px.line(df_m_qv, x='Date', y='PontosVisitanteAcumulados', title=f'Pontos Acumulados como Visitante do {mandante}')
    fig.update_layout(xaxis_title='Data', yaxis_title='Pontos Acumulados')
    col1.plotly_chart(fig, use_container_width=True,)

    fig = px.line(df_v, x='Date', y='PontosVisitanteAcumulados', title=f'Pontos Acumulados como Visitante do {visitante}')
    fig.update_layout(xaxis_title='Data', yaxis_title='Pontos Acumulados')
    col2.plotly_chart(fig, use_container_width=True,)

    fig = px.line(df_v_qm, x='Date', y='PontosCasaAcumulados', title=f'Pontos Acumulados em Casa do {visitante}')
    fig.update_layout(xaxis_title='Data', yaxis_title='Pontos Acumulados')
    col2.plotly_chart(fig, use_container_width=True,)

    fig = px.line(df_m, x='Date', y=['FTHGAcumuladoCasa', 'FTAGAcumuladoCasa'], title=f'Gols Acumulados em Casa do {mandante}')
    fig.update_layout(xaxis_title='Data', yaxis_title='Gols Acumulados')
    col1.plotly_chart(fig, use_container_width=True,)

    fig = px.line(df_v, x='Date', y=['FTHGAcumuladoVisitante','FTAGAcumuladoVisitante'], title=f'Gols Acumulados como Visitante do {visitante}')
    fig.update_layout(xaxis_title='Data', yaxis_title='Gols Acumulados')
    col2.plotly_chart(fig, use_container_width=True,)

    a, b = st.columns(2)
    fig = px.line(df_m, x='Date', y=['HSTAcumuladoCasa', 'ASTAcumuladoCasa'], title=f'Chutes a gol Acumulados em Casa do {mandante}')
    fig.update_layout(xaxis_title='Data', yaxis_title='Chutes a gol Acumulados')
    a.plotly_chart(fig, use_container_width=True,)

    fig = px.line(df_v, x='Date', y=['HSTAcumuladoVisitante','ASTAcumuladoVisitante'], title=f'Chutes a gol Acumulados como Visitante do {visitante}')
    fig.update_layout(xaxis_title='Data', yaxis_title='Chutes a gol Acumulados')
    b.plotly_chart(fig, use_container_width=True,)


    fig = px.line(df_m, x='Date', y=['HCAcumuladoCasa', 'ACAcumuladoCasa'], title=f'Escanteios Acumulados em Casa do {mandante}')
    fig.update_layout(xaxis_title='Data', yaxis_title='Escanteios Acumulados')
    a.plotly_chart(fig, use_container_width=True,)

    fig = px.line(df_v, x='Date', y=['HCAcumuladoVisitante','ACAcumuladoVisitante'], title=f'Escanteios Acumulados como Visitante do {visitante}')
    fig.update_layout(xaxis_title='Data', yaxis_title='Escanteios Acumulados')
    b.plotly_chart(fig, use_container_width=True,)

    fig = px.line(df_m, x='Date', y=['HSAcumuladoCasa', 'ASAcumuladoCasa'], title=f'Finalizações Acumuladas em Casa do {mandante}')
    fig.update_layout(xaxis_title='Data', yaxis_title='Finalizações Acumuladas')
    a.plotly_chart(fig, use_container_width=True,)

    fig = px.line(df_v, x='Date', y=['HSAcumuladoVisitante','ASAcumuladoVisitante'], title=f'Finalizações Acumuladas como Visitante do {visitante}')
    fig.update_layout(xaxis_title='Data', yaxis_title='Finalizações Acumuladas')
    b.plotly_chart(fig, use_container_width=True,)

    fig = px.line(df_m, x='Date', y=['IntensidadeMandanteAcumulada'], title=f'Intensidade Acumulada em Casa do {mandante}')
    fig.update_layout(xaxis_title='Data', yaxis_title='Intensidade Acumulada')
    a.plotly_chart(fig, use_container_width=True,)

    fig = px.line(df_v, x='Date', y=['IntensidadeVisitanteAcumulada'], title=f'Intensidade Acumulada como Visitante do {visitante}')
    fig.update_layout(xaxis_title='Data', yaxis_title='Intensidade Acumulada')
    b.plotly_chart(fig, use_container_width=True,)

    st.divider()
    a, b = st.columns(2)
    # Escrevendo a média de gols feitos pelo time da casa
    a.subheader(f'A média de gols feitos pelo {mandante} em casa é de {round(df_m["FTHG"].mean(), 2)}')
    # Escrevendo a média de gols sofridos pelo time da casa
    a.subheader(f'A média de gols sofridos pelo {mandante} em casa é de {round(df_m["FTAG"].mean(), 2)}')

    # Escrevendo a média de gols feitos pelo time visitante
    b.subheader(f'A média de gols feitos pelo {visitante} como visitante é de {round(df_v["FTAG"].mean(), 2)}')
    # Escrevendo a média de gols sofridos pelo time visitante
    b.subheader(f'A média de gols sofridos pelo {visitante} como visitante é de {round(df_v["FTHG"].mean(), 2)}')

    # Escrevendo o desvio padrão de gols feitos pelo time da casa
    a.subheader(f'O desvio padrão de gols feitos pelo {mandante} em casa é de {round(df_m["FTHG"].std(), 2)}')

    # Escrevendo o desvio padrão de gols feitos pelo time visitante
    b.subheader(f'O desvio padrão de gols feitos pelo {visitante} como visitante é de {round(df_v["FTAG"].std(), 2)}')

    # Escrevendo o desvio padrão de gols sofridos pelo time da casa
    a.subheader(f'O desvio padrão de gols sofridos pelo {mandante} em casa é de {round(df_m["FTAG"].std(), 2)}')

    # Escrevendo o desvio padrão de gols sofridos pelo time visitante
    b.subheader(f'O desvio padrão de gols sofridos pelo {visitante} como visitante é de {round(df_v["FTHG"].std(), 2)}')

    # Escrevendo a variância de gols feitos pelo time da casa
    a.subheader(f'A variância de gols feitos pelo {mandante} em casa é de {round(df_m["FTHG"].var(), 2)}')

    # Escrevendo a variância de gols feitos pelo time visitante
    b.subheader(f'A variância de gols feitos pelo {visitante} como visitante é de {round(df_v["FTAG"].var(), 2)}')

    # Escrevendo a variância de gols sofridos pelo time da casa
    a.subheader(f'A variância de gols sofridos pelo {mandante} em casa é de {round(df_m["FTAG"].var(), 2)}')

    # Escrevendo a variância de gols sofridos pelo time visitante
    b.subheader(f'A variância de gols sofridos pelo {visitante} como visitante é de {round(df_v["FTHG"].var(), 2)}')

    st.divider()
    # Vamos criar 4 colunas no df, BackCasa, BackCasaEmpate, BackVisitante, BackVisitanteEmpate
    a, b = st.columns(2)
    # Escrevendo o ROI do time da casa com BackCasa
    a.subheader(f'O ROI do {mandante} com BackCasa é de {round(df_m["BackCasa"].mean() * 100, 2)}%')

    # Escrevendo o ROI do time da casa com BackCasaEmpate
    a.subheader(f'O ROI do {mandante} com BackCasaEmpate é de {round(df_m["BackCasaEmpate"].mean() * 100, 2)}%')

    # Escrevendo o ROI do time da casa com BackVisitante
    a.subheader(f'O ROI do {mandante} com BackVisitante é de {round(df_m["BackVisitante"].mean() * 100, 2)}%')

    # Escrevendo o ROI do time visitante com BackVisitante
    b.subheader(f'O ROI do {visitante} com BackVisitante é de {round(df_v["BackVisitante"].mean() * 100, 2)}%')

    # Escrevendo o ROI do time visitante com BackVisitanteEmpate
    b.subheader(f'O ROI do {visitante} com BackVisitanteEmpate é de {round(df_v["BackVisitanteEmpate"].mean() * 100, 2)}%')

    # Escrevendo o ROI do time visitante com BackCasa
    b.subheader(f'O ROI do {visitante} com BackCasa é de {round(df_v["BackCasa"].mean() * 100, 2)}%')


with open('config.yaml') as f:
    config = yaml.load(f, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login()

if st.session_state['authentication_status']:
    st.write(f'You are logged in, Sr *{st.session_state["name"]}*')
    st.title('Análise de Dados da Premier League')
    run()
    # if authenticator.logout():
    #     st.rerun()
elif st.session_state['authentication_status'] == False:
    st.write('Senha ou Usuário incorretos. Tente novamente.')
elif st.session_state['authentication_status'] is None:
    st.write('Informe suas credenciais para acessar o sistema.')





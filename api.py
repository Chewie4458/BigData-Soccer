import http.client
import requests
import json
import glob
from pandas import DataFrame
import pandas as pd

# salvar nome do arquivo com data ex partida04112025
# no front vai verificar se o da data que precisa já existe - se não existe faz a requisição
# fazer uma chamada só
    # pega as partidas
    # faz um for e pega as predictions de cada partida
    # joga tudo para uma única base (excel)

headers = {
    'x-apisports-key': "0083b88b9e9da5f8c1dcaabe3dfa4275"
    }

# Função que recupera todas as partidas de um dia específico (AAAA-MM-DD)
def getPartidas(date):
    # Define o URL do endpoint (predictions)
    url = "https://v3.football.api-sports.io/fixtures?date=" + str(date)

    # Realiza o request
    responsePartidas = requests.request("GET", url, headers=headers)

    # Converte a resposta para JSON
    dadosPartidas = json.loads(responsePartidas.text)

    return dadosPartidas

# Função para recuperar previsão de uma partida
def getPredictions(fixture):
    # Define o URL do endpoint (predictions)
    url = "https://v3.football.api-sports.io/predictions?fixture=" + str(fixture)

    # Realiza o request
    responsePredictions = requests.request("GET", url, headers=headers)

    # Converte a resposta para JSON
    dadosPredictions = json.loads(responsePredictions.text)

    return dadosPredictions

# Função para recupera dados de uma partida específica
def getFixture(id):
    # Define o URL do endpoint (fixtures)
    url = "https://v3.football.api-sports.io/fixtures?id=" + str(id)

    # Realiza o request
    responseFixtures = requests.request("GET", url, headers=headers)

    # Converte a resposta para JSON
    dadosFixtures = json.loads(responseFixtures.text)

    return dadosFixtures

# Função que gera a base de partidas em excel
def geraBasePartidas(date):
    # Recupera as partidas da data
    dadosPartidas = getPartidas(date)

    # Inicia o contador para limitar o número de partidas
    qtdPartidas = 0

    # Inicializa os array para armazenar os dados
    data = []
    liga = []
    timeCasa = []
    logoTimeCasa = []
    timeVisitante = []
    logoTimeVisitante = []
    predictionVencedor = []
    vencedor = []
    predictionGolsCasa = []
    golsCasa = []
    predictionGolsVisitante = []
    golsVisitante = []

    for fixture in dadosPartidas["response"]:
        # Finaliza o loop se atingiu o limite
        if (qtdPartidas == 4):
            break

        # Recupera o id
        idPartida = fixture["fixture"]["id"]

        # Atualiza a qauntidade recuperada
        qtdPartidas += 1

        # Recupera os dados da partida
        dadosPredictions = getPredictions(idPartida)
        dadosFixtures = getFixture(idPartida)

        try:
            # Recupera os dados necessários
            data.append(date) # Arrumar para pegar data e hora do retorno
            liga.append(dadosPredictions["response"][0]["league"]["name"])
            timeCasaStr = dadosPredictions["response"][0]["teams"]["home"]["name"] # Armazena em variável para utilizar no vencedor
            timeCasa.append(timeCasaStr)
            logoTimeCasa.append(dadosPredictions["response"][0]["teams"]["home"]["logo"])
            timeVisitanteStr = dadosPredictions["response"][0]["teams"]["away"]["name"] # Armazena em variável para utilizar no vencedor
            timeVisitante.append(timeVisitanteStr)
            logoTimeVisitante.append(dadosPredictions["response"][0]["teams"]["away"]["logo"])
            winOrDraw = dadosPredictions["response"][0]["predictions"]["win_or_draw"]
            predictionVencedor.append(dadosPredictions["response"][0]["predictions"]["winner"]["name"] if winOrDraw else "Empate")
            casaVencedor = dadosFixtures["response"][0]["teams"]["home"]["winner"]
            visitanteVencedor = dadosFixtures["response"][0]["teams"]["away"]["winner"]
            vencedor.append(timeCasaStr if casaVencedor and (not visitanteVencedor) else (timeVisitanteStr if visitanteVencedor and (not casaVencedor) else "Empate"))
            predictionGolsCasa.append(abs(float(dadosPredictions["response"][0]["predictions"]["goals"]["home"])))
            golsCasaAux = dadosFixtures["response"][0]["goals"]["home"]
            golsCasa.append(golsCasaAux if golsCasaAux != None else 0)
            predictionGolsVisitante.append(abs(float(dadosPredictions["response"][0]["predictions"]["goals"]["away"])))
            golsVisitanteAux = dadosFixtures["response"][0]["goals"]["away"]
            golsVisitante.append(golsVisitanteAux if golsVisitanteAux != None else 0)

        except Exception as e:
            print(f"Erro na partida {idPartida}: {e}")

            # Remove os últimos elementos adicionados antes do erro
            liga.pop()
            timeCasa.pop()
            logoTimeCasa.pop()
            timeVisitante.pop()
            logoTimeVisitante.pop()
            predictionVencedor.pop()

            break

    # Transforma os dados em dataframe
    df = DataFrame({'Data': data,
                    'Liga': liga,
                    'Casa': timeCasa,
                    'Logo Casa': logoTimeCasa,
                    'Visitante': timeVisitante,
                    'Logo Visitante': logoTimeVisitante,
                    'Prediction_Vencedor': predictionVencedor,
                    'Vencedor': vencedor,
                    'Prediction_Gols_Casa': predictionGolsCasa,
                    'Gols_Casa': golsCasa,
                    'Prediction_Gols_Visitante': predictionGolsVisitante,
                    'Gols_Visitante': golsVisitante
                    })

    # Exporta o dataframe para excel
    df.to_excel(f"partidas{date}.xlsx", sheet_name='sheet1', index=False)

    return 'OK'

# Função que recupera previsõs e resultados de uma partida
# O resultado é exportado como excel
def geraBasePartidaUnica(idPartida):
    dadosPredictions = getPredictions(idPartida)
    dadosFixtures = getFixture(idPartida)

    # Recupera os dados necessários
    liga = dadosPredictions["response"][0]["league"]["name"]
    timeCasa = dadosPredictions["response"][0]["teams"]["home"]["name"]
    logoTimeCasa = dadosPredictions["response"][0]["teams"]["home"]["logo"]
    timeVisitante = dadosPredictions["response"][0]["teams"]["away"]["name"]
    logoTimeVisitante = dadosPredictions["response"][0]["teams"]["away"]["logo"]
    winOrDraw = dadosPredictions["response"][0]["predictions"]["win_or_draw"]
    predictionVencedor = dadosPredictions["response"][0]["predictions"]["winner"]["name"] if winOrDraw else "Empate"
    casaVencedor = dadosFixtures["response"][0]["teams"]["home"]["winner"]
    visitanteVencedor = dadosFixtures["response"][0]["teams"]["away"]["winner"]
    vencedor = timeCasa if casaVencedor and (not visitanteVencedor) else (timeVisitante if visitanteVencedor and (not casaVencedor) else "Empate")
    predictionGolsCasa = abs(int(dadosPredictions["response"][0]["predictions"]["goals"]["home"]))
    golsCasa = dadosFixtures["response"][0]["goals"]["home"]
    predictionGolsVisitante = abs(int(dadosPredictions["response"][0]["predictions"]["goals"]["away"]))
    golsVisitante = dadosFixtures["response"][0]["goals"]["away"]

    # Transforma os dados em dataframe
    df = DataFrame({'Liga': [liga],
                    'Casa': [timeCasa],
                    'Logo Casa': [logoTimeCasa],
                    'Visitante': [timeVisitante],
                    'Logo Visitante': [logoTimeVisitante],
                    'Prediction_Vencedor': [predictionVencedor],
                    'Vencedor': [vencedor],
                    'Prediction_Gols_Casa': [predictionGolsCasa],
                    'Gols_Casa': [golsCasa],
                    'Prediction_Gols_Visitante': [predictionGolsVisitante],
                    'Gols_Visitante': [golsVisitante]
                    })

    # Exporta o dataframe para excel
    df.to_excel(f'partida{idPartida}.xlsx', sheet_name='sheet1', index=False)

    return 'OK'

# Função para mergear todas as bases geradas
def mergeBases():
    # Encontra todos os arquivos que começam com "partidas" e terminam com .xlsx
    arquivos = glob.glob("partidas*.xlsx")

    dfs = []  # lista para armazenar todos os DataFrames

    for arquivo in arquivos:
        df = pd.read_excel(arquivo)
        dfs.append(df)

    # Concatena tudo em um DataFrame só
    df_final = pd.concat(dfs, ignore_index=True)

    # Remove duplicatas (caso existam registros repetidos)
    df_final = df_final.drop_duplicates()

    # Salva em um novo arquivo
    df_final.to_excel("partidas_merged.xlsx", index=False)


# Testes (Ex. partida: 1477941
# print(json.dumps(dados, indent=4, ensure_ascii=False))
#getBasePartidaUnica(1477941)
#print(geraBasePartidas('2025-11-15'))
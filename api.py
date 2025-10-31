import http.client
import requests
import json
from pandas import DataFrame

headers = {
    'x-apisports-key': "2ca4f33e422f272a2021955472321911"
    }

''' INICIO PREDICTIONS '''
# Define o URL do endpoint (predictions)
url = "https://v3.football.api-sports.io/predictions?fixture=1477941"

# Realiza o request
responsePredictions = requests.request("GET", url, headers=headers)

# Converte a resposta para JSON
dadosPredictions = json.loads(responsePredictions.text)
''' FIM PREDICTIONS '''

''' INICIO FIXTURES '''
# Define o URL do endpoint (fixtures)
url = "https://v3.football.api-sports.io/fixtures?id=1477941"

# Realiza o request
responseFixtures = requests.request("GET", url, headers=headers)

# Converte a resposta para JSON
dadosFixtures = json.loads(responseFixtures.text)
''' FIM FIXTURES '''

# Teste de resposta
print(responsePredictions.text)
print(responseFixtures.text)
# print(json.dumps(dados, indent=4, ensure_ascii=False))
print(dadosPredictions["response"][0]["predictions"]["winner"]["name"])

# Recupera os dados necessários
liga = dadosPredictions["response"][0]["league"]["name"]
timeCasa = dadosPredictions["response"][0]["teams"]["home"]["name"]
timeVisitante = dadosPredictions["response"][0]["teams"]["away"]["name"]
winOrDraw = dadosPredictions["response"][0]["predictions"]["win_or_draw"]
predictionVencedor = dadosPredictions["response"][0]["predictions"]["winner"]["name"] if winOrDraw else "Empate"
casaVencedor = dadosFixtures["response"][0]["teams"]["home"]["winner"]
visitanteVencedor = dadosFixtures["response"][0]["teams"]["away"]["winner"]
vencedor = timeCasa if casaVencedor and (not visitanteVencedor) else (timeVisitante if visitanteVencedor and (not casaVencedor) else "Empate")
predictionGolsCasa = dadosPredictions["response"][0]["predictions"]["goals"]["home"]
golsCasa = dadosFixtures["response"][0]["goals"]["home"]
predictionGolsVisitante = dadosPredictions["response"][0]["predictions"]["goals"]["away"]
golsVisitante = dadosFixtures["response"][0]["goals"]["away"]

# Transforma os dados em dataframe
df = DataFrame({'Liga': [liga],
                'Casa': [timeCasa],
                'Visitante': [timeVisitante],
                'Prediction_Vencedor': [predictionVencedor],
                'Vencedor': [vencedor],
                'Prediction_Gols_Casa': [predictionGolsCasa],
                'Gols_Casa': [golsCasa],
                'Prediction_Gols_Visitante': [predictionGolsVisitante],
                'Gols_Visitante': [golsVisitante]
                })

# Exporta o dataframe para excel
df.to_excel('partidas.xlsx', sheet_name='sheet1', index=False)

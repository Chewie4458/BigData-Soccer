import http.client
import requests
import json
from pandas import DataFrame

conn = http.client.HTTPSConnection("v3.football.api-sports.io")

headers = {
    'x-apisports-key': "2ca4f33e422f272a2021955472321911"
    }

conn.request("GET", "/leagues", headers=headers)

res = conn.getresponse()
data = res.read()

#print(data.decode("utf-8"))

# Define o URL do endpoint
url = "https://v3.football.api-sports.io/predictions?fixture=1477941"

# Inicia o array de retorno
payload={}

# Realiza o request
response = requests.request("GET", url, headers=headers, data=payload)

dados = json.loads(response.text)

# Teste de resposta
print(response.text)
# print(json.dumps(dados, indent=4, ensure_ascii=False))
print(dados["response"][0]["predictions"]["winner"]["name"])

# Recupera os dados necessários
timeCasa = dados["response"][0]["teams"]["home"]["name"]
timeVisitante = dados["response"][0]["teams"]["away"]["name"]

# Transforma os dados em dataframe
df = DataFrame({'Casa': [timeCasa], 'Visitante': [timeVisitante]})

# Exporta o dataframe para excel
df.to_excel('test.xlsx', sheet_name='sheet1', index=False)

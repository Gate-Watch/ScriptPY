import psutil
import time
from datetime import datetime
import mysql.connector as sql
import re

import requests
import json
from dotenv import load_dotenv
import os

load_dotenv('C:\\Users\\Samsung\\OneDrive\\Documentos\\ScriptPY\\configuracoes.env')

email_jira = os.getenv('JIRA_EMAIL')
chave_jira = os.getenv('CHAVE_DO_JIRA')


limiteCPU = 0.1
limiteMEM = 85.0
limiteDSK = 85.0


def abrir_chamado_jira(categoria, tipo, limite_atual):
    url = "https://gate-watch.atlassian.net/rest/api/2/issue"
    auth = (email_jira, chave_jira)
    headers = {"Content-Type": "application/json"}
    descricao = f"O uso de {categoria} ultrapassou o limite de {tipo}. Utilização atual: {limite_atual:.2f}%."

    dados_chamado = {
        "fields": {
            "project": {"key": "GW"},
            "summary": f"Limite de {categoria} excedido - Uso de {limite_atual:.2f}%",
            "description": descricao,
            "issuetype": {"name": "Task"}
        }
    }

    response = requests.post(url, auth=auth, headers=headers, data=json.dumps(dados_chamado))
    
    if response.status_code == 201:
        print(f"Chamado criado com sucesso no Jira para {categoria}!")
    else:
        print(f"Falha ao criar chamado para {categoria}. Status: {response.status_code}, Erro: {response.text}")

def idUnicoMaquina():
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                mac = addr.address
                if mac:
                    mac = re.sub(r'[:.-]', '', mac)
                    mac_int = int(mac, 16) & 0xFFFFFFFF
                    return mac_int
    return None


def leitura():
    countCPU = 0
    countMEM = 0
    countDSK = 0
    
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq().current

        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent
        memory_total = round(memory_info.total / 1024.0 / 1024.0 / 1024.0, 1)

        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        disk_total = round(disk.total / 1024.0 / 1024.0 / 1024.0, 1)

        idMaquina = idUnicoMaquina()
        if idMaquina is None:
            print("Erro ao obter o endereço MAC.")
            return

        # Exibe os dados da máquina capturados
        print(f"\nDados capturados: ")
        print(f"CPU: {cpu_usage:.2f}% | Freq: {cpu_freq:.2f} MHz")
        print(f"Memória: {memory_usage:.2f}% de {memory_total} GB")
        print(f"Disco: {disk_usage:.2f}% de {disk_total} GB")
        
        # Verifica limites e alerta
        if cpu_usage > limiteCPU:
            countCPU += 1
            print(f"⚠️ ALERTA: CPU acima do limite ({cpu_usage:.2f}%)")
            if countCPU >= 5:
                abrir_chamado_jira("CPU", "limite", cpu_usage)
                countCPU = 0
        else:
            countCPU = 0

        if memory_usage > limiteMEM:
            countMEM += 1
            print(f"⚠️ ALERTA: Memória acima do limite ({memory_usage:.2f}%)")
            if countMEM >= 5:
                abrir_chamado_jira("Memória", "limite", memory_usage)
                countMEM = 0
        else:
            countMEM = 0

        if disk_usage > limiteDSK:
            countDSK += 1
            print(f"⚠️ ALERTA: Disco acima do limite ({disk_usage:.2f}%)")
            if countDSK >= 5:
                abrir_chamado_jira("Disco", "limite", disk_usage)
                countDSK = 0
        else:
            countDSK = 0
    

        time.sleep(5)  # Atraso entre as capturas de dados

# Iniciar a leitura
leitura()

import psutil
import time
from datetime import datetime
import mysql.connector as sql
import re

import requests
import json
from dotenv import load_dotenv
import os

load_dotenv('configuracoes.env')

email_jira = os.getenv('JIRA_EMAIL')
chave_jira = os.getenv('CHAVE_DO_JIRA')

limiteCPU = 10.0
limiteMEM = 85.0
limiteDSK = 85.0


def abrir_chamado_jira(categoria, tipo, limite_atual):
    url = "https://marketsafee.atlassian.net/rest/api/2/issue"
    auth = (email_jira, chave_jira)
    headers = {"Content-Type": "application/json"}
    descricao = f"O uso de {categoria} ultrapassou o limite de {tipo}. Utilização atual: {limite_atual:.2f}%."

    dados_chamado = {
        "fields": {
            "project": {"key": "GW"},
            "summary": f"Limite de {categoria} excedido - Uso de {limite_atual:.2f}%",
            "description": descricao,
            "issuetype": {"name": "Investigar um problema"}
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
                    # Remove os ':' do endereço MAC
                    mac = re.sub(r'[:.-]', '', mac)
                    # Converte o MAC para inteiro e pega os últimos 8 dígitos
                    mac_int = int(mac, 16) & 0xFFFFFFFF
                    return mac_int
    return None


def leitura():
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

    inserirDados(idMaquina, cpu_usage, cpu_freq, memory_usage, memory_total, disk_usage, disk_total)


def conectarDb():
    return sql.connect(
        host='localhost',
        port="3306",
        user='root',
        password='###',
        database="GateWatch"
    )


def inserirDados(idMaquina, cpu_usage, cpu_freq, memory_usage, memory_total, disk_usage, disk_total):
    momento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    banco = conectarDb()
    cursor = banco.cursor()
    query = """
        INSERT INTO dados 
            (idMaquina, momento, cpu_usage, cpu_freq, memory_usage, memory_total, disk_usage, disk_total) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    val = (idMaquina, momento, cpu_usage, cpu_freq, memory_usage, memory_total, disk_usage, disk_total)
    cursor.execute(query, val)
    banco.commit()

    countCPU = 0
    countMEM = 0
    countDSK = 0
    if cpu_usage > limiteCPU:
        countCPU += 1
        if(countCPU >= 5):
            countCPU = 0
            abrir_chamado_jira("CPU", cpu_usage, limiteCPU)

    
    if memory_usage > limiteMEM:
        countMEM += 1
        if(countMEM >= 5):
            countMEM = 0
            abrir_chamado_jira("Memória", memory_usage, limiteMEM)
    
    if disk_usage > limiteDSK:
        countDSK += 1
        if(countDSK >= 5):
            countDSK = 0
            abrir_chamado_jira("Disco", disk_usage, limiteDSK)


def listarMaquinas():
    banco = conectarDb()
    cursor = banco.cursor()

    cursor.execute("SELECT DISTINCT idMaquina FROM dados")
    maquinas = cursor.fetchall()

    return maquinas


def buscarDados(idMaquina, component):
    banco = conectarDb()
    cursor = banco.cursor()

    cursor.execute(f"SELECT {component} FROM dados WHERE idMaquina = %s ORDER BY momento DESC LIMIT 1", (idMaquina,))
    resultado = cursor.fetchone()

    return resultado


def listarMemoria(idMaquina):
    banco = conectarDb()
    cursor = banco.cursor()

    cursor.execute("SELECT memory_total FROM dados WHERE idMaquina = %s ORDER BY momento DESC LIMIT 1", (idMaquina,))
    resultado = cursor.fetchone()

    return resultado


def listarDisco(idMaquina):
    banco = conectarDb()
    cursor = banco.cursor()

    cursor.execute("SELECT disk_total FROM dados WHERE idMaquina = %s ORDER BY momento DESC LIMIT 1", (idMaquina,))
    resultado = cursor.fetchone()

    return resultado


def menu_interacao():
    while True:
        maquinas = listarMaquinas()

        print("1- Escolha a máquina que você quer monitorar:")
        for maquina in maquinas:
            print(f"- Máquina ID: {maquina[0]}")

        idMaquina = int(input("Digite o ID da máquina que você quer monitorar: "))

        print("2- Qual componente você deseja monitorar:")
        print("1 - CPU")
        print("2 - RAM")
        print("3 - Disco")
        print("4 - Sair")
        componente_opcao = int(input("Digite o número do componente que você deseja monitorar: "))

        if componente_opcao == 4:
            print("Saindo do menu de interação...")
            break

        if componente_opcao == 1:
            print("Escolha a métrica:")
            print("1 - Percentual")
            print("2 - Frequência")
            metrica_opcao = int(input("Digite o número da métrica que você deseja monitorar: "))
            if metrica_opcao == 1:
                componente = 'cpu_usage'
            elif metrica_opcao == 2:
                componente = 'cpu_freq'
            else:
                print("Opção inválida")
                continue

        elif componente_opcao == 2:
            print("Escolha a métrica:")
            print("1 - Percentual")
            print("2 - Espaço em bytes")
            metrica_opcao = int(input("Digite o número da métrica que você deseja monitorar: "))
            if metrica_opcao == 1:
                componente = 'memory_usage'
            elif metrica_opcao == 2:
                componente = 'memory_total'
            else:
                print("Opção inválida")
                continue

        elif componente_opcao == 3:
            print("Escolha a métrica:")
            print("1 - Percentual")
            print("2 - Espaço em bytes")
            metrica_opcao = int(input("Digite o número da métrica que você deseja monitorar: "))
            if metrica_opcao == 1:
                componente = 'disk_usage'
            elif metrica_opcao == 2:
                componente = 'disk_total'
            else:
                print("Opção inválida")
                continue
        else:
            print("Opção inválida")
            continue

        while True:
            if componente == 'cpu_freq':
                resultado = buscarDados(idMaquina, 'cpu_freq')
                if resultado:
                    print(f"Frequência atual do CPU da máquina {idMaquina}: {resultado[0]} MHz")
                else:
                    print(f"Nenhum dado encontrado para a máquina {idMaquina}.")
            elif componente == 'memory_total':
                resultado = listarMemoria(idMaquina)
                if resultado:
                    print(f"Espaço total da RAM da máquina {idMaquina}: {resultado[0]} GB")
                else:
                    print(f"Nenhum dado encontrado para a máquina {idMaquina}.")
            elif componente == 'disk_total':
                resultado = listarDisco(idMaquina)
                if resultado:
                    print(f"Espaço total do Disco da máquina {idMaquina}: {resultado[0]} GB")
                else:
                    print(f"Nenhum dado encontrado para a máquina {idMaquina}.")
            else:
                resultado = buscarDados(idMaquina, componente)
                if resultado:
                    if componente == 'cpu_usage':
                        print(f"Percentual atual do CPU da máquina {idMaquina}: {resultado[0]}%")
                    elif componente == 'memory_usage':
                        print(f"Percentual atual da RAM da máquina {idMaquina}: {resultado[0]}%")
                    elif componente == 'disk_usage':
                        print(f"Percentual atual do Disco da máquina {idMaquina}: {resultado[0]}%")
                else:
                    print(f"Nenhum dado encontrado para a máquina {idMaquina}.")
            time.sleep(5)


while True:
    leitura()
    menu_interacao()
    continuar = input("Deseja continuar no menu de interação? (s/n): ").strip().lower()
    if continuar != 's':
        print("Saindo da aplicação...")
        break

import psutil
import time
from datetime import datetime
import mysql.connector as sql

def leitura():
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_freq = psutil.cpu_freq().current

    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    memory_total = round(memory_info.total / 1024.0 / 1024.0 / 1024.0, 1)

    disk = psutil.disk_usage('/')
    disk_usage = disk.percent
    disk_total = round(disk.total / 1024.0 / 1024.0 / 1024.0, 1)

    idMaquina = 3

    inserirDados(idMaquina, cpu_usage, cpu_freq, memory_usage, memory_total, disk_usage, disk_total)

def conectarDb():
    return sql.connect(
        host='localhost',
        port="3306",
        user='root',
        password='7895',
        database="cco1"
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
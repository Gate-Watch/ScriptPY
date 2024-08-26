import psutil
import time
from datetime import datetime
import mysql.connector as sql

def leitura():
    cpu_usage = psutil.cpu_percent(interval=1)

    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent

    disk = psutil.disk_usage('/')
    disk_usage = disk.percent

    performance_media = round((cpu_usage + memory_usage + disk_usage) / 3, 1)

    print(f"Utilização da CPU: {cpu_usage}%")
    print(f"Utilização da Memória: {memory_usage}%")
    print(f"Utilização do Disco: {disk_usage}%")
    print(f"Performance Média: {performance_media}%")

    bancodedados(cpu_usage, memory_usage, disk_usage, performance_media)

    time.sleep(5)

def bancodedados(cpu_usage, memory_usage, disk_usage, performance_media):
    idMaquina = 1
    momento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    banco = sql.connect(
        host='10.18.33.48',
        port="3307",
        user='aluno',
        password='Sptech#2024',
        database="cco1"
    )

    cursor = banco.cursor()

    query = "INSERT INTO dados (idMaquina, momento, cpu_usage, memory_usage, disk_usage, performance_media) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (idMaquina, momento, cpu_usage, memory_usage, disk_usage, performance_media)

    cursor.execute(query, val)
    banco.commit()
    cursor.close()
    banco.close()

while True:
    leitura()
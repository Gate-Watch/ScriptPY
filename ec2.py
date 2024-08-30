import psutil
import time

def leitura():
    while True:

        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq().current

        memory_info = psutil.virtual_memory()
        memory_usage = memory_info.percent
        memory_free = round(memory_info.available / 1024.0 / 1024.0 / 1024.0, 1)
        memory_total = round(memory_info.total / 1024.0 / 1024.0 / 1024.0, 1)

        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        disk_free = round(disk.free / 1024.0 / 1024.0 / 1024.0, 1)
        disk_total = round(disk.total / 1024.0 / 1024.0 / 1024.0, 1)

        performance_media = round((cpu_usage + memory_usage + disk_usage) / 3, 1)

        idMaquina = 3

        time.sleep(5)
        print(f"""
        ID da Máquina: {idMaquina}
        Uso da CPU: {cpu_usage}%
        Frequência da CPU: {cpu_freq} MHz
        Uso de Memória: {memory_usage}%
        Memória Livre: {memory_free} GB
        Memória Total: {memory_total} GB
        Uso de Disco: {disk_usage}%
        Disco Livre: {disk_free} GB
        Disco Total: {disk_total} GB
        Média de Performance: {performance_media}%
        """)

while True:
    leitura()
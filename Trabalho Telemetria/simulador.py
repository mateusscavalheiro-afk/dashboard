import sqlite3
import time
import random
from datetime import datetime

# CRIAÇÃO DO BANCO DE DADOS, PASSANDO OS SEUS PARÂMETROS DE VARIÁVEIS
def init_db():
    conn = sqlite3.connect("telemetria.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetria_veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            veiculo TEXT,
            velocidade REAL,
            combustivel REAL,
            temperatura REAL,
            bateria REAL
        )
    ''')
    conn.commit()
    conn.close()

# FUNÇÃO DE INJEÇÃO DE VALORES DENTRO DO BANCO DE DADOS, SEGUINDO OS PARÂMETROS JÁ DECLARADOS
def simular_sensores():
    init_db()
    print("Telemetria de veículos chegando..")

    veiculos = {
        'Empilhadeira A-001': {'velo': 25.6, 'combu': 78, 'temp': 24.0, 'bat': 55},
        'Empilhadeira B-002': {'velo': 35, 'combu': 66, 'temp': 31, 'bat': 40},
        'Empilhadeira D-011': {'velo': 28.9, 'combu': 98, 'temp': 37.8, 'bat': 30},
        'Empilhadeira E-031': {'velo': 22.6, 'combu': 19, 'temp': 68.2, 'bat': 33},
        'Empilhadeira C-007': {'velo': 12.1, 'combu': 32, 'temp': 43.3, 'bat': 78},
        'Empilhadeira C-081': {'velo': 61.8, 'combu': 48, 'temp': 73.1, 'bat': 81},
        'Empilhadeira D-045': {'velo': 43.2, 'combu': 55, 'temp': 46.2, 'bat': 77},
        'Empilhadeira B-033': {'velo': 21.3, 'combu': 86, 'temp': 25.9, 'bat': 44},
    }

    while True:
        try:
            conn = sqlite3.connect('telemetria.db', timeout=10)
            cursor = conn.cursor()

            for veiculo, dados in veiculos.items():
                velo = round(max(0, min(100, dados['velo'] + random.uniform(-0.8, 0.8))), 2)
                combu = round(max(0, min(100, dados['combu'] + random.uniform(-0.8, 0.8))), 2)
                temp = round(dados['temp'] + random.uniform(-0.4, 0.4), 2)
                bat = round(max(0, min(100, dados['bat'] + random.uniform(-0.8, 0.8))), 2)

                dados['velo'] = velo
                dados['combu'] = combu
                dados['temp'] = temp
                dados['bat'] = bat

                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                cursor.execute('''
                    INSERT INTO telemetria_veiculos (timestamp, veiculo, velocidade, combustivel, temperatura, bateria)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (timestamp, veiculo, velo, combu, temp, bat))

            conn.commit()
            conn.close()

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Telemetria coletada.")
            time.sleep(2)

        except sqlite3.OperationalError as e:
            print(f"Aviso de concorrência: {e}")
            time.sleep(1)

        except KeyboardInterrupt:
            print("\nTelemetria finalizada.")
            break

if __name__ == "__main__":
    simular_sensores()
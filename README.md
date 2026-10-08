# 🚚 RTS | Fleet Intelligence

### Sistema de Telemetria e Monitoramento de Frota

Sistema desenvolvido para monitorar e acompanhar os principais indicadores operacionais de veículos utilizados em ambientes logísticos e industriais, por meio de um dashboard interativo.

O **RTS Fleet Intelligence** permite visualizar dados de telemetria, acompanhar o comportamento dos veículos e identificar condições que exigem atenção, facilitando a análise operacional da frota.

---

## 📊 Visão geral

O sistema utiliza um simulador para gerar leituras de telemetria, armazena essas informações em um banco de dados SQLite e apresenta os dados em um dashboard desenvolvido com Streamlit.

### Principais indicadores monitorados

| Indicador       | Descrição                       | Unidade |
| --------------- | ------------------------------- | ------- |
| 🚀 Velocidade   | Velocidade atual do veículo     | km/h    |
| ⛽ Combustível   | Nível de combustível disponível | %       |
| 🌡️ Temperatura | Temperatura do motor            | °C      |
| 🔋 Bateria      | Nível de bateria                | %       |

## ✨ Funcionalidades

* **Monitoramento em tempo real:** atualização periódica das leituras recebidas pelo sistema.
* **Dashboard interativo:** visualização organizada dos principais indicadores da frota.
* **Monitoramento individual:** acompanhamento das métricas de cada veículo.
* **Filtros por veículo:** seleção de veículos específicos para analisar seus dados.
* **Gráficos históricos:** análise da evolução da velocidade, do combustível, da temperatura e da bateria.
* **Alertas operacionais:** identificação de valores que ultrapassam os limites configurados.
* **Histórico de telemetria:** consulta às leituras armazenadas no banco de dados.
* **Exportação de dados:** possibilidade de exportar o histórico em formato CSV.
* **Simulação de sensores:** geração contínua de dados para testar o funcionamento do sistema.

## 🛠️ Tecnologias utilizadas

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge\&logo=streamlit\&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge\&logo=pandas\&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge\&logo=plotly\&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge\&logo=sqlite\&logoColor=white)

* **Python:** linguagem utilizada no desenvolvimento do sistema.
* **Streamlit:** construção da interface e do dashboard.
* **Pandas:** tratamento e organização dos dados.
* **Plotly:** criação dos gráficos interativos.
* **SQLite:** armazenamento local das leituras de telemetria.

## 📁 Estrutura do projeto

```text
RTS-Fleet-Intelligence/
│
├── app.py
├── simulador.py
├── requirements.txt
├── telemetria.db
│
└── assets/
    ├── logo.svg
    └── banner.png
```

| Arquivo            | Descrição                                            |
| ------------------ | ---------------------------------------------------- |
| `app.py`           | Dashboard e visualização dos dados.                  |
| `simulador.py`     | Simulação e geração de telemetria.                   |
| `requirements.txt` | Dependências do projeto.                             |
| `telemetria.db`    | Banco de dados SQLite, gerado localmente.            |
| `assets/`          | Diretório opcional para imagens e identidade visual. |

## ⚙️ Como executar o projeto

### 1. Pré-requisitos

Instale o [Python](https://www.python.org/downloads/). O Git é opcional, caso prefira clonar o repositório.

No Windows, marque a opção **Add Python to PATH** durante a instalação do Python.

### 2. Obter o projeto

Clone o repositório:

```bash
git clone URL_DO_SEU_REPOSITORIO
```

Entre na pasta:

```bash
cd RTS-Fleet-Intelligence
```

Se já tiver os arquivos no computador, abra o terminal diretamente na pasta do projeto.

### 3. Criar um ambiente virtual

```bash
python -m venv venv
```

Ative o ambiente no Windows:

```bash
venv\Scripts\activate
```

### 4. Instalar as dependências

Execute:

```bash
pip install -r requirements.txt
```

O arquivo `requirements.txt` deve conter:

```text
streamlit
pandas
plotly
```

O SQLite já faz parte da biblioteca padrão do Python e não precisa ser instalado separadamente.

### 5. Iniciar o simulador

Em um terminal, execute:

```bash
python simulador.py
```

O simulador começará a gerar leituras para os veículos e armazená-las no banco `telemetria.db`.

Mantenha esse terminal aberto enquanto utilizar o sistema.

### 6. Iniciar o dashboard

Abra um **segundo terminal** na mesma pasta do projeto.

Se estiver usando um ambiente virtual, ative-o novamente:

```bash
venv\Scripts\activate
```

Inicie o Streamlit:

```bash
streamlit run app.py
```

O terminal exibirá o endereço local do dashboard. Normalmente, você poderá acessá-lo em:

http://localhost:8501

Pronto! Com o simulador e o dashboard em execução, será possível acompanhar as leituras e visualizar os gráficos atualizados.

## 🔄 Fluxo de funcionamento

```text
Simulador de sensores
        |
        v
Geração das leituras
        |
        v
Banco de dados SQLite
        |
        v
Leitura e organização com Pandas
        |
        v
Dashboard Streamlit
        |
        v
Indicadores, gráficos e alertas
```

## 🚨 Observações importantes

* Os dados utilizados são gerados por um simulador e não representam necessariamente medições de veículos reais.
* O simulador e o dashboard precisam acessar o mesmo arquivo `telemetria.db`.
* Os limites de alerta são parâmetros configuráveis e devem ser ajustados conforme as características dos veículos monitorados.
* A atualização automática do dashboard não substitui a aquisição real de dados por sensores ou equipamentos de telemetria.
* Os caminhos das imagens definidos em `app.py` devem corresponder aos arquivos existentes no ambiente em que o projeto será executado.

## 🚀 Possibilidades de evolução

O projeto pode ser ampliado futuramente com recursos como:

* Integração com dispositivos reais de telemetria.
* Localização geográfica dos veículos por GPS.
* Visualização de rotas e posições em um mapa.
* Histórico de trajetos e análise de desempenho.
* Sistema de alertas com notificações.
* Relatórios operacionais e indicadores de eficiência.

## 👨‍💻 Sobre o projeto

O **RTS Fleet Intelligence** é um projeto de monitoramento de telemetria com foco na visualização e análise de indicadores operacionais de veículos logísticos e industriais.

Seu objetivo é demonstrar como a integração entre simulação de dados, armazenamento estruturado e visualização interativa pode contribuir para o acompanhamento e a análise de uma frota.

---

**RTS Fleet Intelligence** · Telemetria, monitoramento e análise operacional.

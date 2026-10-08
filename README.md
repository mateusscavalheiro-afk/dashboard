Tema:
Opcao B - Telemetria de Frota de Veiculos Logisticos: Acompanhar caminhoes de entrega em tempo real (Metricas: Velocidade em km/h, Nivel de Combustivel %, Bateria em Volts e Temperatura do Motor)

Passo 1:
Criar pasta com nome do projeto, bem como os arquivos simulador.py e app.py.

Passo 2:
Abra o terminal e instale as bibliotecas necessárias para o funcionamento do código.

*Use o comando pip install 'nome_extensão'

Extensões usadas:
    - pandas
    - streamlit
    - plotly.express
    - numpy

Para a visualização do banco de dados, utilize as extensões disponíveis na aba 'Extensions' no VSCode:
    - SQLite
    - SQLite Viewer
    - SQLTools
    - SQLTools SQLite

*Nem todas as extensões são necessárias, porém caso queira interagir com o banco de dados por meio das querys, se faz necessário a instalação das mesmas

Passo 3:
Para a criação do dashboard funcional, se faz necessário dividir a aplicação em duas etapas. A primeira será responsável pelo gerenciamento dos dados, utilizando do sistema CRUD (Create, Read, Update and Delete) para manipulação do banco de dados. O segundo ficará responsável pelo leavantamento do site utilizando a plataforma Streamlit.

Para a simulação:

Baixe o arquivo;
Instale as extensões;
Rode o 'simulador.py'
Abra o app.py em um terminal usando o comando 'python -m streamlit run app.py'


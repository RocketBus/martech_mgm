Member Get Member
O Member Get Member é uma campanha criada pela equipe de Growth e desenvolvida em parceria com o time de Martech. O objetivo é incentivar a indicação da ClickBus por meio de cupons de desconto exclusivos.

⚙️ Como funciona
Indicação: Cada usuário recebe um link exclusivo para indicar a ClickBus a outras pessoas.
Compra via link: Quando alguém usa o link de indicação para realizar uma compra, essa pessoa recebe um cupom de desconto.
Recompensa para o indicador: Assim que a pessoa indicada finaliza sua viagem, o proprietário do link também recebe um cupom de desconto como recompensa.
🎯 Benefícios
✅ Todos ganham: Tanto quem indica quanto quem é indicado recebem descontos.
✅ Incentivo à lealdade: A campanha promove fidelização e aumenta as chances de novas compras por meio de indicações orgânicas.

🚀 Tecnologias Utilizadas
🔹 FastAPI
FastAPI é um framework web moderno e de alta performance para construção de APIs com Python. Ele é baseado no ASGI (Asynchronous Server Gateway Interface), permitindo a criação de aplicações assíncronas de forma eficiente e intuitiva.

🔹 Apache Airflow
O Apache Airflow é uma plataforma open-source para orquestração de workflows e pipelines de dados. Ele permite criar, agendar e monitorar fluxos de trabalho complexos, como ETLs e integrações entre sistemas, tudo programaticamente em Python.

🔹 Processos automatizados via Airflow:

DAG - Criação de Promoters: mgm_set_promoters
DAG - Criação de Voucher para Promoter: mgm_create_promoter_voucher
🔗 Documentação: Airflow
🔗 GitHub do Airflow: airflow-dags-k8s-developer
📌 Caso não tenha acesso, solicitar ao time de Engenharia.

🔹 Banco de Dados MySQL
Utilizamos o MySQL como sistema de gerenciamento de banco de dados relacional (RDBMS) para armazenar e organizar as informações do projeto. Ele é confiável, amplamente utilizado no mercado e se integra muito bem com aplicações em Python.

Documentação oficial: https://dev.mysql.com/doc/
🔧 Ambientes
Existem dois ambientes distintos, cada um com sua própria base de dados:

dev – Banco utilizado localmente para testes e desenvolvimento.
live – Banco utilizado em produção, com dados reais.
Essa separação garante segurança, controle de qualidade e evita impactos não intencionais no ambiente de produção.

▶️ Como rodar o projeto localmente
Para executar o projeto em ambiente local com MySQL, siga os passos abaixo:

Instale e inicie o MySQL localmente

Você pode instalar o MySQL usando o MySQL Installer ou rodar via Docker.
Certifique-se de que o serviço do MySQL esteja ativo e acessível (por padrão na porta 3306).
Crie o banco de dados local

Crie um banco de dados com o nome esperado pelo projeto, como por exemplo martech_db, ou conforme definido nas variáveis de ambiente.
Configure as variáveis de ambiente no .env

No ambiente de desenvolvimento, utilizamos a engine mysql+aiomysql, que permite integração assíncrona com o MySQL.
mysql → especifica o tipo de banco.
aiomysql → é o driver que habilita a comunicação assíncrona.
Exemplo de configuração da DATABASE_URL no arquivo .env:

DATABASE_URL_LOCAL=mysql+aiomysql://usuario:senha@localhost:3306/nome_do_banco
Execute a aplicação
Com tudo configurado, você pode rodar a aplicação localmente utilizando o gerenciador padrão do projeto (por exemplo uvicorn, docker-compose, etc.).

🛠️ Sessões assíncronas com SQLAlchemy
Para manter todas as APIs compatíveis com a abordagem async, utilizamos sessões assíncronas via AsyncSession do SQLAlchemy:

from sqlmodel.ext.asyncio.session import AsyncSession
Essa estratégia melhora:

✅ A performance em ambientes com múltiplas requisições concorrentes.
✅ O consumo eficiente de recursos (threads/processos).
✅ A escalabilidade da API, especialmente quando usada em produção com workers assíncronos como o Uvicorn.
🛠 Como configurar as variáveis no código
Para facilitar o gerenciamento de variáveis de ambiente, utilizamos uma função que retorna um dicionário (dict) onde:

A chave (key) é o nome da variável.
O valor é o conteúdo da variável.
A obtenção desses valores pode ocorrer de duas formas:

Ambiente local: As variáveis são carregadas a partir de um arquivo .env.
Produção: As variáveis devem ser previamente configuradas no AWS Secrets Manager.
No arquivo app/config/settings.py, há uma variável do tipo List[str] chamada SECRET_KEYS, que contém os nomes das variáveis esperadas, tanto no .env quanto no AWS Secrets Manager. É importante que o nome das variáveis seja o mesmo em ambos os ambientes para garantir a compatibilidade.

A função fetch_secrets deve receber como parâmetro o tipo de ambiente em que está sendo executada, como dev ou prod. Dessa forma, ela pode coletar corretamente as variáveis de cada ambiente sem complicações. Abaixo está a função responsável por buscar os valores das variáveis conforme o ambiente:

from typing import List
import os
from secret_manager import SecretManager  # Classe para gerenciar secrets da AWS

# Lista de variáveis de ambiente que queremos carregar
SECRET_KEYS = [
    "VARIAVEL1",
    "VARIAVEL2"
]

def fetch_secrets(environments: str) -> dict:
    """
    Carrega as variáveis de ambiente de acordo com o ambiente especificado.

    Parâmetros:
    - environments (str): Ambiente atual do sistema ('dev' ou 'prod')

    Retorno:
    - dict contendo os secrets carregados
    """

    # Ambiente de desenvolvimento local
    if environments == 'dev':
        # Recupera os secrets diretamente do sistema operacional (local `.env` ou exportadas)
        response = {key: os.environ.get(key) for key in SECRET_KEYS}
        
        # Banco de dados local específico para ambiente de desenvolvimento
        response['DATABASE_URL'] = os.environ.get("DATABASE_URL_LOCAL")
        return response

    # Ambiente de produção
    elif environments == 'prod':
        # Inicializa o gerenciador de secrets da AWS
        secret_manager = SecretManager()
        
        # ARN do secret armazenado no AWS Secrets Manager
        aws_arn = "arn:aws:secretsmanager:us-east-1:596612927501:secret:Secrets_MartechHub-sqcs3E"
        
        # Recupera a variável ENVIRONMENT do ambiente Kubernetes (ex: development, production)
        k8s_env = os.environ.get("ENVIRONMENT")

        # Recupera as variáveis definidas em SECRET_KEYS usando o Secrets Manager da AWS
        response = {
            key: secret_manager.get_secret_by_secret_key(arn=aws_arn, secret_key=key)
            for key in SECRET_KEYS
        }

        # Define qual string de conexão com o banco usar de acordo com o ambiente no Kubernetes
        if k8s_env == "development":
            response['DATABASE_URL'] = secret_manager.get_secret_by_secret_key(
                arn=aws_arn,
                secret_key="DATABASE_URL_DEV"
            )
        elif k8s_env == "production":
            response['DATABASE_URL'] = secret_manager.get_secret_by_secret_key(
                arn=aws_arn,
                secret_key="DATABASE_URL_LIVE"
            )

        return response

    # Caso o ambiente informado não seja válido
    return {}

# =============================
# EXEMPLO DE USO DO CÓDIGO
# =============================

# Define o ambiente atual como 'prod'
environment_secrets = fetch_secrets("prod")
secrets.append(environment_secrets)
Esse código permite que, dependendo do ambiente, as variáveis sejam obtidas corretamente, garantindo flexibilidade e segurança no gerenciamento de credenciais. 🚀

import os
from app.src.aws.secrete_manager import SecretManager


ENVIRONMENT_LOCAL = 'dev' # alterar p/ prod quado fizer commit

SECRET_KEYS = [
    "JWT_SECRET",
    "JWT_ALGORITHM",
    "ACCESS_TOKEN",
    "MGM_DISCOUNT_ID_INVITED",
    "MGM_DISCOUNT_ID_PROMOTER",
    "MGM_VOUCHER_CAMPAIGN_INDICADO",
    "MGM_VOUCHER_CAMPAIGN_PROMOTOR",
    "SALT_GENERATOR",
    "ALPHABET",
    "SLACK_OAUTH_TOKEN",
    "MARTECH_ALERT_CHANNEL_ID",
    "ROOTUSERNAME",
    "ROOTPASSWORD",
    "SALES_FORCE_SFTP_HOST",
    "SALES_FORCE_SFTP_USERNAME",
    "SALES_FORCE_SFTP_PASSWORD",
]

secrets = []
environment_secrets = {}

def fetch_secrets(environment):
    
    if environment == 'dev':
        response = {key: os.environ.get(key) for key in SECRET_KEYS}
        response['DATABASE_URL'] = os.environ.get("DATABASE_URL_LOCAL")
        return response
  
    elif environment == 'prod':
        secret_manager = SecretManager()
        aws_arn = "arn:aws:secretsmanager:us-east-1:596612927501:secret:Secrets_MartechHub-sqcs3E"
        k8s_env = os.environ.get("ENVIRONMENT")
        response = {key: secret_manager.get_secret_by_secret_key(arn=aws_arn, secret_key=key) for key in SECRET_KEYS}
    
        if k8s_env == "development":
            response['DATABASE_URL'] = secret_manager.get_secret_by_secret_key(
                arn=aws_arn,
                secret_key="DATABASE_URL_DEV"
            )
    
        if k8s_env == "production":
            response['DATABASE_URL'] = secret_manager.get_secret_by_secret_key(
                arn=aws_arn,
                secret_key="DATABASE_URL_LIVE"
            )
        return response
    return {}

environment_secrets = fetch_secrets(ENVIRONMENT_LOCAL)
secrets.append(environment_secrets)

VOUCHER_MOCK = {
    "voucher_id": "e5ddcb30-a215-4100-824f-a7814c2469c4",
    "code": "mgm_mock_app",
    "end_at": "2025-12-31T23:59:59"
}

VERSION = "1.0.0"

VERSION = "1.0.0"

title = "API Martech - Member Get Member"
summary = "API para gerenciar o programa de indicação Member Get Member (MGM) da ClickBus, oferecendo descontos e recompensas para quem indica e para quem é indicado."
description = """
    A API Martech - Member Get Member facilita as indicações de clientes através de cupons de desconto.
    Ela permite a criação e gerenciamento de links de indicação, rastreia compras feitas através desses links
    e distribui cupons de desconto tanto para o indicador quanto para o cliente indicado após a conclusão da viagem.

    Funcionalidades Principais:

    - Geração e gerenciamento de links de indicação
    - Distribuição de cupons de desconto para indicadores e indicados
    - Rastreamento de compras via links de indicação
    - Distribuição de recompensas após a conclusão da viagem
    - Integração com plataformas de CRM e marketing
    - Análise de desempenho da campanha

    Esta API otimiza o processo de indicação, incentiva a fidelidade do cliente e impulsiona o crescimento orgânico através de indicações incentivadas.
    """

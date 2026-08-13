from dotenv import load_dotenv
import os
import datetime
from app import App

## CONFIGURACOES DO SERVIDOR
load_dotenv()

# AUTENTICACAO
EMPRESA= os.getenv('EMPRESA')
USUARIO= os.getenv('USUARIO')
SENHA= os.getenv('SENHA')


#CONFIGURACOES DE REQUISICAO
BASE_URL= os.getenv('BASE_URL')
URL_FINAL = os.getenv('URL_FINAL')
URL_PEDIDOS = os.getenv('URL_PEDIDOS')

# BANCO DE DADOS
URL_HOST = os.getenv('URL_HOST')
DB_KEY = os.getenv('DB_KEY')


# CONFIGURACAO DO SERVICO DE EMAIL
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
EMAIL = os.getenv('EMAIL')
EMAIL_PASS = os.getenv('EMAIL_PASS')

  
## GERENCIAMENTO DE EXECUCOES
TIME_EXEC_GCOMLINKS = os.getenv('TIME_EXEC_GCOMLINKS')
TIME_EXEC_PEDIDOS = os.getenv('TIME_EXEC_PEDIDOS')
tempo_tratado_gcomlinks = int(TIME_EXEC_GCOMLINKS)
tempo_tratado_pedidos = int(TIME_EXEC_PEDIDOS) 

server = App(
                BASE_URL,
                SENHA,
                EMPRESA,
                USUARIO,
                URL_FINAL,
                EMAIL,
                EMAIL_PASS,
                SMTP_SERVER,
                SMTP_PORT,
                tempo_tratado_gcomlinks,
                tempo_tratado_pedidos,
                URL_HOST,
                DB_KEY,
                URL_PEDIDOS
            )

server.call_agent_myorder(20, "GCOM_LINKS")
server.call_agent_myorder(20, "PEDIDOS")


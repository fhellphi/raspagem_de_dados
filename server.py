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

# BANCO DE DADOS
URL_HOST = os.getenv('URL_HOST')
DB_KEY = os.getenv('DB_KEY')


# CONFIGURACAO DO SERVICO DE EMAIL
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
EMAIL = os.getenv('EMAIL')
EMAIL_PASS = os.getenv('EMAIL_PASS')

print(URL_HOST, DB_KEY)
  
## GERENCIAMENTO DE EXECUCOES
TIME_EXEC = os.getenv('TIME_EXEC')
tempo_tratado = int(TIME_EXEC)

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
                tempo_tratado
            )
server.start_app()

# tz5Nf9JIKj9q9cQb - server do supabase particular



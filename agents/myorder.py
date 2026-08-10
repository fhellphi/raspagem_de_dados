from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Ec
from datetime import datetime
from services.email import enviar_email
from io import BytesIO
from services.database import Supabase
import pandas as pd


class AgentMyorder:
    
    def __init__(
                    self,
                    url_auth,
                    pass_url,
                    empresa_url,
                    user_url,
                    url_info,
                    email_login,
                    email_pass,
                    smtp_server,
                    smtp_port,
                    ip_db=0,
                    pass_db=0,
                ):
        
        self.url_auth = url_auth
        self.pass_url = pass_url
        self.empresa_url = empresa_url
        self.user_url = user_url
        self.url_info = url_info
        self.ip_db = ip_db
        self.pass_bd = pass_db
        self.listagem_lojas = []
        self.email_login = email_login
        self.email_pass = email_pass
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.lojas_offline = []
        self.html_lojas_offline = ''
        self.lojas_online = []
        self.lojas_versao = []
        self.html_lojas_versao = ''
        self.maior_versao_disponivel = ''

    def get_info(self, time):
        
        navegador = webdriver.Chrome()
        wait = WebDriverWait(navegador,time)
        
        try:
            navegador.get(self.url_auth)
            empresa = wait.until(
                Ec.presence_of_element_located((By.ID, 'SG_EMP'))
            )
            usuario = wait.until(
                Ec.presence_of_element_located((By.ID, 'NM_LOG_USU'))
            )
            senha = wait.until(
                Ec.presence_of_element_located((By.ID, 'DC_PASSWORD'))
            )
            botao = navegador.find_element(By.ID, 'btnLogin')
            
            empresa.send_keys(self.empresa_url)
            usuario.send_keys(self.user_url)
            senha.send_keys(self.pass_url)
            botao.click()
            
            wait.until(Ec.url_contains('MyOrders'))
            
            navegador.get(self.url_info)
            
            wait.until(Ec.url_contains('StatusUnidade'))
            
            while True:
                element = navegador.find_elements(By.CSS_SELECTOR, '#myDataTable tbody tr')
                
                for i in element:
                    colunas = i.find_elements(By.TAG_NAME, "td")

                    # print(f"Quantidade de colunas: {len(colunas)}")
                    # print([c.text for c in colunas])            

                    if len(colunas) != 6:
                            continue
                        
                    loja = {
                            "empresa": colunas[0].text,
                            "uf": colunas[1].text,
                            "loja": colunas[2].text,
                            "status": colunas[3].text,
                            "ultima_atualizacao": colunas[4].text,
                            "versao": colunas[5].text
                    }
                    
                    self.listagem_lojas.append(loja)
                                   
                final = navegador.find_element(By.ID, 'myDataTable_next')
                
                if 'disabled' in final.get_attribute("class"):
                    break
                
                primeira_linha = element[0]
                
                proximo = wait.until(
                    Ec.element_to_be_clickable((By.LINK_TEXT, 'Próximo'))
                )
                
                proximo.click()
                wait.until(Ec.staleness_of(primeira_linha))
                
                if not element:
                    break
                            
        except Exception as err:
            print('erro ao resgatar informacao')
            print(f'ERRO: {err}')
            with open ('log_myorder.txt', 'a', encoding='utf-8') as log:
                log.write(f'\n DATRA/HORA = {datetime.now()}. ERRO NA EXECUCAO DO METODO get_info. ERRO: {err}')
         
    def dispara_email(self):
        
        df = pd.DataFrame(self.listagem_lojas)
        maior_versao = df['versao'].max()
        
        df_offiline = df.loc [
            df['status'] == 'OFFLINE',
            ['empresa', 'uf', 'status', 'ultima_atualizacao', 'versao']
        ]
        df_versao = df.loc[
            df['versao'] < maior_versao,
            ['loja', 'uf', 'status', 'ultima_atualizacao', 'versao']
        ]
        
        arquivo_offline = BytesIO()
        with pd.ExcelWriter( arquivo_offline, engine='openpyxl') as writer:
            df_offiline.to_excel(
                writer,
                index=False,
                sheet_name='Lojas Offiline'
            )
        excel_offline = arquivo_offline.getvalue()
        
        arquivo_versao = BytesIO()
        with pd.ExcelWriter(arquivo_versao, engine='openpyxl') as writer:
            df_versao.to_excel(
                writer,
                index=False,
                sheet_name='Lojas Desatualizadas'
            )
        excel_versao = arquivo_versao.getvalue()
        
        
        mensagem = f"""
        <html>

        <head>

        <style>

        body {{
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12px;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 10px;
        }}

        th {{
            background-color:#d32f2f;
            color:white;
            padding:2px;
            border:1px solid #ccc;
        }}

        td {{
            border:1px solid #ccc;
            padding:2px;
            text-align:center;
        }}

        tr:nth-child(even){{
            background:#f7941f;
        }}

        </style>

        </head>

        <body>

            <h2>Monitoramento MyOrders</h2>

            <p>Olá,</p>

            <p>Foram encontradas <b>{len(self.lojas_offline)}</b> lojas offline.</p>

            {self.html_lojas_offline}

            <br>
            <p>Foram encontradas <b>{len(self.lojas_versao)}</b> lojas sem a ultima atuaização. Ultima atuaização encontrada <b>{self.maior_versao_disponivel}</b></p>
                {self.html_lojas_versao}
            <br>
            <p><b>Data/Hora da execução:</b> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>

            <hr>

            <small>E-mail enviado automaticamente pelo serviço de monitoramento.</small>

        </body>

        </html>
        """
        
        anexos = [

                {
                    "dados": excel_offline,
                    "maintype": "application",
                    "subtype": "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "filename": "relatorio_lojas_offline.xlsx"
                },

                {
                    "dados": excel_versao,
                    "maintype": "application",
                    "subtype": "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "filename": "relatorio_versoes_desatualizadas.xlsx"
                }

            ]         
        enviar_email(
                        'Monitoramento Plataforma MyOrder',
                        mensagem,
                        'tecnologia@giraffas.com',
                        self.email_login, 
                        self.email_pass,
                        self.smtp_server,
                        self.smtp_port,
                        anexos=anexos
                    )
        
    def tratar_dados(self):
        
        df = pd.DataFrame(self.listagem_lojas)
        
        offiline = df.loc[
            df['status'] == 'OFFLINE',
            ['loja', 'uf', 'status', 'ultima_atualizacao', 'versao']
        ]
        

               
        self.lojas_offline = offiline
        
        self.html_lojas_offline = offiline.to_html(
                index=False,
                border=0,
                justify="center",
                classes="tabela"
        )
        
        df['versao'] = df['versao'].astype(float)

        maior_versao = df['versao'].max()
        self.maior_versao_disponivel = maior_versao
        
        maior_versao_tratado = df.loc[
            df['versao'] < maior_versao,
            ['loja', 'uf', 'status', 'ultima_atualizacao', 'versao']
        ]
        
        self.lojas_versao = maior_versao_tratado
        self.html_lojas_versao = maior_versao_tratado.to_html(
            index=False,
            border=0,
            justify="center",
            classes="tabela"
        )
        
        # print(self.lojas_offline)
                
    def insert_db(self):
        try:
            supabase_client = Supabase(self.ip_db, self.pass_bd)
            supabase_client.insert("GIRAFFAS_HOMOLOG","MONITORAMENTO_GLINKS", self.listagem_lojas)
            print('Insert no banco realizado com sucesso')
            
        except Exception as err:
            print('Erro ao executar o metodo inser_db do agent myorder')
            print(err)
            
    def select_db(self):
        supabase_client = Supabase(self.ip_db, self.pass_bd)
        supabase_client.select('GIRAFFAS_HOMOLOG','MONITORAMENTO_GLINKS')
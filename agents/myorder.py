from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from services.email import enviar_email
from io import BytesIO
from services.database import Supabase
from pathlib import Path
import pandas as pd
import time
import re
import unicodedata
import platform


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
        url_pedidos="",
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
        self.html_lojas_offline = ""
        self.lojas_online = []
        self.lojas_versao = []
        self.html_lojas_versao = ""
        self.maior_versao_disponivel = ""
        self.url_pedidos = url_pedidos
        self.lista_pedidos = []
        self.lista_pedidos_erro = []
        self.lisa_pedidos_aguardando = []
        self.lista_pedidos_supa = []
        self.html_pedidos_erro = ''
        self.html_pedidos_aguardando = ''
        sistema = platform.system()
        self.options = Options()

        if sistema == "Linux":
            self.options.binary_location = "/usr/bin/chromium"
            self.options.add_argument("--headless")
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-dev-shm-usage")
            self.options.add_argument("--disable-gpu")
            self.options.add_argument("--window-size=1920,1080")
        elif sistema =="Windows":
            self.options.add_argument("--headless=new")
            self.options.add_argument("--disable-gpu")
            self.options.add_argument("--window-size=1920,1080")
        else:
            raise RuntimeError(f"Sistema operacional não suportado: {sistema}")


    def get_info(self, time_selenium):

        navegador = webdriver.Chrome(options=self.options)
        
        wait = WebDriverWait(navegador, time_selenium)

        try:
            navegador.get(self.url_auth)
            empresa = wait.until(Ec.presence_of_element_located((By.ID, "SG_EMP")))
            usuario = wait.until(Ec.presence_of_element_located((By.ID, "NM_LOG_USU")))
            senha = wait.until(Ec.presence_of_element_located((By.ID, "DC_PASSWORD")))
            botao = navegador.find_element(By.ID, "btnLogin")

            empresa.send_keys(self.empresa_url)
            usuario.send_keys(self.user_url)
            senha.send_keys(self.pass_url)
            botao.click()

            wait.until(Ec.url_contains("MyOrders"))

            navegador.get(self.url_info)

            wait.until(Ec.url_contains("StatusUnidade"))

            while True:
                element = navegador.find_elements(
                    By.CSS_SELECTOR, "#myDataTable tbody tr"
                )

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
                        "versao": colunas[5].text,
                    }

                    self.listagem_lojas.append(loja)

                final = navegador.find_element(By.ID, "myDataTable_next")

                if "disabled" in final.get_attribute("class"):
                    break

                primeira_linha = element[0]

                proximo = wait.until(
                    Ec.element_to_be_clickable((By.LINK_TEXT, "Próximo"))
                )

                proximo.click()
                wait.until(Ec.staleness_of(primeira_linha))

                if not element:
                    break

        except Exception as err:
            print("erro ao resgatar informacao")
            print(f"ERRO: {err}")
            with open("log_myorder.txt", "a", encoding="utf-8") as log:
                log.write(
                    f"\n DATRA/HORA = {datetime.now()}. ERRO NA EXECUCAO DO METODO get_info. ERRO: {err}"
                )

        finally:
            navegador.quit()
            print("Processo de verificacao de links concluido")

    def get_pedidos(self, time_selenium):

        BASE_DIR = Path(__file__).resolve().parent
        prefs = {
            "download.default_directory": str(BASE_DIR),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        self.options.add_experimental_option("prefs", prefs)

        arqui_base = BASE_DIR / "Gestão de Pedidos - Painel.xlsx"

        # navegacao

        navegador = webdriver.Chrome(options=self.options)
        wait = WebDriverWait(navegador, time_selenium)

        try:
            data_final = datetime.now()
            data_final_formatada = data_final.strftime("%d/%m/%Y")
            print(f"Data final: {data_final_formatada}")

            data_inicial = data_final - timedelta(days=7)
            data_inicial_formatada = data_inicial.strftime("%d/%m/%Y")
            print(f"Data inicial: {data_inicial_formatada}")

            if self.url_pedidos == "":
                print(f"Informe a url para monitoramento dos pedidos")
                with open("log_myorder.txt", "a", encoding="utf-8") as log:
                    log.write(
                        "ERRO: metodo get_pedidos sem url para realizar monitaramento dos pedidos "
                    )
                return

            navegador.get(self.url_auth)
            empresa = wait.until(Ec.presence_of_element_located((By.ID, "SG_EMP")))
            usuario = wait.until(Ec.presence_of_element_located((By.ID, "NM_LOG_USU")))
            senha = wait.until(Ec.presence_of_element_located((By.ID, "DC_PASSWORD")))
            botao = navegador.find_element(By.ID, "btnLogin")

            empresa.send_keys(self.empresa_url)
            usuario.send_keys(self.user_url)
            senha.send_keys(self.pass_url)
            botao.click()

            navegador.get(self.url_pedidos)

            filtro = wait.until(
                Ec.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        'div.spin-icon.bg-myorders[onclick="setaTamanhoFiltro()"]',
                    )
                )
            )

            navegador.execute_script("arguments[0].click();", filtro)

            input_init = wait.until(
                Ec.visibility_of_element_located((By.ID, "txtPeriodStart"))
            )
            input_final = wait.until(
                Ec.visibility_of_element_located((By.ID, "txtPeriodFinish"))
            )

            # Data inicial
            navegador.execute_script(
                """
                arguments[0].value = arguments[1];
                arguments[0].setAttribute('value', arguments[1]);

                arguments[0].dispatchEvent(
                    new Event('input', { bubbles: true })
                );

                arguments[0].dispatchEvent(
                    new Event('change', { bubbles: true })
                );
            """,
                input_init,
                data_inicial_formatada,
            )

            # Data final
            navegador.execute_script(
                """
                arguments[0].value = arguments[1];
                arguments[0].setAttribute('value', arguments[1]);

                arguments[0].dispatchEvent(
                    new Event('input', { bubbles: true })
                );

                arguments[0].dispatchEvent(
                    new Event('change', { bubbles: true })
                );
            """,
                input_final,
                data_final_formatada,
            )

            btn_filter = wait.until(Ec.element_to_be_clickable((By.ID, "btnPesquisar")))

            btn_filter.click()

            wait.until(
                Ec.url_contains(
                    f"https://www.myorders.com.br/MyOrders/PedidoWeb/Painel?period={data_final_formatada}&periodStart={data_inicial_formatada}&periodFinish={data_final_formatada}&origin=&status=N&etb=&mrc=&correction=N&captureByMyOrders=S&program=&sIntegradoRetentativa=N"
                )
            )

            ##PROCESSO DE RASPAGEM DE DADOS

            export_excel = wait.until(
                Ec.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'a[aria-controls="myDataTable"]')
                )
            )

            navegador.execute_script("arguments[0].click()", export_excel)

            timeout = 60
            inicio = time.time()

            while time.time() - inicio < timeout:
                if arqui_base.exists():
                    temp = BASE_DIR / "Gestão de Pedidos - Painel.xlsx.crdownload"
                    if not temp.exists():
                        tamanho_1 = arqui_base.stat().st_size
                        time.sleep(1)
                        tamanho_2 = arqui_base.stat().st_size
                        if tamanho_1 == tamanho_2:
                            print("download concluido")
                            break
                    time.sleep(1)
            else:
                raise TimeoutError(
                    "O download do Excel não foi concluído dentro do tempo esperado."
                )

            if arqui_base.exists():
                print("Verificando arquivo...")
                df = pd.read_excel(arqui_base, engine="calamine")

                df.columns = [self.normalizar_dados(coluna) for coluna in df.columns]

                df["recepcao"] = pd.to_datetime(
                    df["recepcao"], errors="coerce", dayfirst=True
                ).dt.strftime("%d/%m/%Y")
                
                df = df.astype(object).where(pd.notna(df), None)

                self.lista_pedidos.extend(df.to_dict(orient="records"))
                
                self.lista_pedidos_erro.extend(
                    df[df["descricao_do_erro"].notna()].to_dict(orient="records")
                )
                
                self.lisa_pedidos_aguardando.extend(
                    df[df["descricao_do_erro"].isnull()].to_dict(orient="records")
                )
                
                df['recepcao'] = pd.to_datetime(
                    df['recepcao'],
                    format='%d/%m/%Y %H:%M:%S',
                    errors='coerce'
                )
                df['recepcao'] = df['recepcao'].dt.strftime(
                    '%Y-%m-%d %H:%M:%S'
                )
                df = df.astype(object).where(pd.notna(df), None)
                self.lista_pedidos_supa.extend(df.to_dict(orient='records'))
                
                print(self.lista_pedidos_erro)
                arqui_base.unlink()
                print("arquivo base removido")

        except Exception as err:
            # <dt style="height: 26px;">Empresa</dt>
            print("Erro no metodo get_pedidos do agent myorder")
            print(f"ERRO: {err}")
            with open("log_myorder.txt", "a", encoding="utf-8") as log:
                log.write(
                    f"\n DATRA/HORA = {datetime.now()}. ERRO NA EXECUCAO DO METODO get_pedidos. ERRO: {err}"
                )

        finally:
            navegador.quit()
            print("Processo de verificacao de pedidos concluido")

    def dispara_email(self, relatorio=''):

        if relatorio == "GCOM_LINKS":
            
            ##Geracao de anexo para os GCOM_LINKS
            df = pd.DataFrame(self.listagem_lojas)
            maior_versao = df["versao"].max()

            df_offiline = df.loc[
                df["status"] == "OFFLINE",
                ["loja", "uf", "status", "ultima_atualizacao", "versao"],
            ]
            df_versao = df.loc[
                df["versao"] < maior_versao,
                ["loja", "uf", "status", "ultima_atualizacao", "versao"],
            ]
            df_versao_atualizada = df.loc[
                df["versao"] == maior_versao,
                ["loja", "uf", "status", "ultima_atualizacao", "versao"],
            ]

            arquivo_offline = BytesIO()
            with pd.ExcelWriter(arquivo_offline, engine="openpyxl") as writer:
                df_offiline.to_excel(writer, index=False, sheet_name="Lojas Offiline")
            excel_offline = arquivo_offline.getvalue()

            arquivo_versao = BytesIO()
            with pd.ExcelWriter(arquivo_versao, engine="openpyxl") as writer:
                df_versao.to_excel(writer, index=False, sheet_name="Lojas Desatualizadas")
            excel_versao = arquivo_versao.getvalue()

            arquivo_versao_atualizada = BytesIO()
            with pd.ExcelWriter(arquivo_versao_atualizada, engine="openpyxl") as writer:
                df_versao_atualizada.to_excel(
                    writer, index=False, sheet_name="Lojas Atualizadas"
                )
            excel_versao_atualizada = arquivo_versao_atualizada.getvalue()

            mensagem_gcomlinks = f"""
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

            anexos_gcom_links = [
                {
                    "dados": excel_offline,
                    "maintype": "application",
                    "subtype": "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "filename": "relatorio_lojas_offline.xlsx",
                },
                {
                    "dados": excel_versao,
                    "maintype": "application",
                    "subtype": "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "filename": "relatorio_versoes_desatualizadas.xlsx",
                },
                {
                    "dados": excel_versao_atualizada,
                    "maintype": "application",
                    "subtype": "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "filename": "relatorio_versoes_desatualizadas.xlsx",
                },
            ]

            
            enviar_email(
                "Monitoramento Plataforma MyOrder",
                mensagem_gcomlinks,
                "tecnologia@giraffas.com",
                self.email_login,
                self.email_pass,
                self.smtp_server,
                self.smtp_port,
                anexos=anexos_gcom_links,
            )
        
        elif relatorio == "PEDIDOS":
            ##GERACAO DE ANEXOS PARA OS PEDIDOS
            df_pedidos = pd.DataFrame(self.lista_pedidos)
            df_erros = pd.DataFrame(self.lista_pedidos_erro)
            df_aguardando = pd.DataFrame(self.lisa_pedidos_aguardando)
            
            arquivo_pedidos = BytesIO()
            with pd.ExcelWriter(arquivo_pedidos, engine='openpyxl') as writer:
                df_pedidos.to_excel(
                    writer,
                    index=False,
                    sheet_name='Compilado dos pedidos'
                )
            excel_pedidos = arquivo_pedidos.getvalue()
            
            
            arquivo_erros = BytesIO()
            with pd.ExcelWriter(arquivo_erros, engine='openpyxl') as writer:
                df_erros.to_excel(
                    writer,
                    index=False,
                    sheet_name='Pedidos com erro de integracao'
                )
            excel_erros = arquivo_erros.getvalue()
            
            
            arquivo_aguardando = BytesIO()
            with pd.ExcelWriter(arquivo_aguardando, engine='openpyxl') as writer:
                df_aguardando.to_excel(
                    writer,
                    index=False,
                    sheet_name='Pedidos aguardando aceite'
                )
            excel_aguardando = arquivo_aguardando.getvalue()
            
            self.html_pedidos_erro = df_erros.to_html(
                index=False, border=0, justify="center", classes="tabela"

            )
            self.html_pedidos_aguardando = df_aguardando.to_html(
                index=False, border=0, justify="center", classes="tabela"
            )
            mensagem_pedidos = f"""
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
            
                        <h2>Monitoramento de pedidos com ERRO/AGUARDANDO ACEITE</h2>
            
                        <p>Olá,</p>
            
                        <p>Foram encontrados <b>{len(self.lista_pedidos_erro)}</b> pedidos com erro .</p>
            
                        {self.html_pedidos_erro}
            
                        <br>
                        <p>Foram encontrados <b>{len(self.lisa_pedidos_aguardando)}</b>pedidos aguardando aceite </p>
                            {self.html_pedidos_aguardando}
                        <br>
                        
                        <p><b>Data/Hora da execução:</b> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</p>
            
                        <hr>
            
                        <small>E-mail enviado automaticamente pelo serviço de monitoramento.</small>
            
                    </body>
            
                    </html>
                    """
            anexos_pedidos = [
                            {
                    "dados": excel_pedidos,
                    "maintype": "application",
                    "subtype": "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "filename": "compilado_pedidos.xlsx",
                },
                {
                    "dados": excel_erros,
                    "maintype": "application",
                    "subtype": "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "filename": "pedidos_com_erro.xlsx",
                },
                {
                    "dados": excel_aguardando,
                    "maintype": "application",
                    "subtype": "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "filename": "pedidos_aguardando_aceite.xlsx",
                },
            ]


            enviar_email(
                "Monitoramento de pedidos",
                mensagem_pedidos,
                "tecnologia@giraffas.com",
                self.email_login,
                self.email_pass,
                self.smtp_server,
                self.smtp_port,
                anexos=anexos_pedidos,
            )
        else:
            print("selecione entre o relatorio, GCOM_LINK ou PEDIDOS para executar o metodo")


    def normalizar_dados(self, coluna):

        coluna = unicodedata.normalize("NFKD", coluna)
        coluna = coluna.encode("ASCII", "ignore").decode("ASCII")

        coluna = coluna.lower()

        coluna = re.sub(r"\s+", "_", coluna)

        coluna = re.sub(r"[^a-zA-Z0-9_]", "", coluna)

        coluna = re.sub(r"_+", "_", coluna)

        coluna = coluna.strip("_")

        return coluna

    def tratar_dados(self):

        df = pd.DataFrame(self.listagem_lojas)

        offiline = df.loc[
            df["status"] == "OFFLINE",
            ["loja", "uf", "status", "ultima_atualizacao", "versao"],
        ]

        self.lojas_offline = offiline

        self.html_lojas_offline = offiline.to_html(
            index=False, border=0, justify="center", classes="tabela"
        )

        df["versao"] = df["versao"].astype(float)

        maior_versao = df["versao"].max()
        self.maior_versao_disponivel = maior_versao

        maior_versao_tratado = df.loc[
            df["versao"] < maior_versao,
            ["loja", "uf", "status", "ultima_atualizacao", "versao"],
        ]

        self.lojas_versao = maior_versao_tratado
        self.html_lojas_versao = maior_versao_tratado.to_html(
            index=False, border=0, justify="center", classes="tabela"
        )

        # print(self.lojas_offline)

    def insert_db(self, base):
        
        try:
            supabase_client = Supabase(self.ip_db, self.pass_bd)
        except Exception as err:
            print('Erro ao se conectar no banco de dados')
            print(f'Erro: {err}')
        finally:
            print('Conexao realziada')
            
        if base == 'GCOM_LINKS': 
            try:
                ##MONITORAMENTO DE LINKS
                supabase_client.insert("MONITORAMENTO", "GCOM_LINKS", self.listagem_lojas)
            except Exception as err:
                print("Erro ao executar o metodo inser_db do agent myorder")
                print(err)
            finally:
                print("INSERT MONITORAMENTO DE LINKS REALIZADO COM SUCESSO")
                
        elif base == 'PEDIDOS':
            try:
                supabase_client.insert(
                    "GIRAFFAS_HOMOLOG", "GCOM_PEDIDOS", self.lista_pedidos_supa
                )
            except Exception as err:
                print('Erro ao executar o insert dos pedidos')
                print(err)
            finally:
                print('INSERT NA TABELA GCOM_PEDIDOS REALIZADOS COM SUCESSO')         
        else:
            print('selecione entre as bases GCOM_LINKS ou PEDIDOS, para execucao do metodo de insert')      

    def select_db(self):
        supabase_client = Supabase(self.ip_db, self.pass_bd)
        supabase_client.select("MONITORAMENTO", "GCOM_LINKS")

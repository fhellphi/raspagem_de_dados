from agents.myorder import AgentMyorder
from datetime import datetime
import time


class App:
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
        tempo_exec_gcom_links=1800,
        tempo_exec_pedidos = 14400,
        ip_db=0,
        pass_db=0,
        url_pedidos=''
    ):
        self.url_auth = url_auth
        self.pass_url = pass_url
        self.empresa_url = empresa_url
        self.user_url = user_url
        self.url_info = url_info
        self.ip_db = ip_db
        self.pass_bd = pass_db
        self.email_login = email_login
        self.email_pass = email_pass
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
     
        self.url_pedidos = url_pedidos

    def call_agent_myorder(self, time, metodo):

        try:

            myorder = AgentMyorder(
                self.url_auth,
                self.pass_url,
                self.empresa_url,
                self.user_url,
                self.url_info,
                self.email_login,
                self.email_pass,
                self.smtp_server,
                self.smtp_port,
                self.ip_db,
                self.pass_bd,
                self.url_pedidos
            )

            if metodo == "PEDIDOS":

                print("Executando método PEDIDOS")

                myorder.get_pedidos(time)

                print("get_pedidos concluído")

                myorder.insert_db('PEDIDOS')

                print("insert_db PEDIDOS concluído")

                myorder.dispara_email('PEDIDOS')

                print("dispara_email PEDIDOS concluído")

                print("Método PEDIDOS executado com sucesso")


            elif metodo == "GCOM_LINKS":

                print("Executando método GCOM_LINKS")

                myorder.get_info(time)

                print("get_info concluído")

                myorder.tratar_dados()

                print("tratar_dados concluído")

                myorder.insert_db('GCOM_LINKS')

                print("insert_db GCOM_LINKS concluído")

                myorder.dispara_email("GCOM_LINKS")

                print("dispara_email GCOM_LINKS concluído")

                print("Método GCOM_LINKS executado com sucesso")
                
            else:
             print(f"Método inválido: {metodo}")

        except Exception as err:
            print("erro na execucao do agent")
            print(f'Erro" {err}')
            with open("log_app.txt", "a", encoding="utf-8") as log:
                log.write(
                    f"DATA/HORA: {datetime}. ERRO NA EXECUCAO DO METODO call_agent. ERRO: {err}"
                )
            raise
                
        finally:
            print('Excecucao dos agents concluida')
        

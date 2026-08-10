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
                    tempo_exec=1800,
                    ip_db=0,
                    pass_db=0
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
        self.tempo_exec = tempo_exec

        
    def call_agent(self, time):
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
                                    self.pass_bd
                                )    
            myorder.get_info(time)
            myorder.tratar_dados()
            myorder.insert_db()
            myorder.dispara_email()
            
        except Exception as err:
            print('erro na execucao do agent')
            print(f'Erro" {err}')
            with open('log_app.txt', 'a', encoding='utf-8') as log:
                log.write(f'DATA/HORA: {datetime}. ERRO NA EXECUCAO DO METODO call_agent. ERRO: {err}')
                
    def start_app(self):
        
            print( f"[{datetime.now()}] " f"Aplicação iniciada." )
            print( f"Intervalo configurado: " f"{self.tempo_exec} segundos." )
             
            while True: 
                try:
                    hora_execucao = datetime.now().timestamp()
                    self.call_agent(hora_execucao)
                except Exception as err:
                        print( f"[{datetime.now()}] " f"Erro no loop principal: {err}" ) 
                        
                        with open( "log_app.txt", "a", encoding="utf-8" ) as log:
                            log.write( f"\n" f"DATA/HORA: {datetime.now()}\n" f"MÉTODO: start_app\n" f"ERRO: {err}\n" f"{'-' * 80}\n" )
                        print( f"[{datetime.now()}] " f"Aguardando {self.tempo_exec} segundos " f"para a próxima execução..." ) 
                        
                time.sleep(self.tempo_exec)
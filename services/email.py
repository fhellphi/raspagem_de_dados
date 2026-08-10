import smtplib
from email.message import EmailMessage
from datetime import datetime


def enviar_email(assunto, msg, destinatario, email_login,email_pass, smtp_server, smtp_port, anexos=None):
    
    
    email = EmailMessage()
    email["From"] = email_login
    email["To"] = destinatario
    email["Subject"] = assunto
    email.set_content("Seu cliente de e-mail não suporta HTML.")
    email.add_alternative(msg, subtype="html")
    
    if anexos:
        for anexo in anexos:
            email.add_attachment(
                anexo['dados'],
            maintype=anexo["maintype"],
            subtype=anexo["subtype"],
            filename=anexo["filename"]
        )
             
    try:
        
        with smtplib.SMTP(smtp_server, smtp_port ) as smtp:
            smtp.starttls()
            smtp.login(email_login, email_pass)
            smtp.send_message(email)
            
        with open('log_email.txt','a', encoding='utf-8') as log:
            log.write(f'\n DATRA/HORA = {datetime.now()}. SUCESSO NA EXECUCAO DO DO SERVICO DE EMAIL.')
            
        print('servico executado')
            
    except  Exception as err:
        
        print('Erro na execucao do servico de email')
        print(f'Erro email: {err}')
        
        with open('log_email.txt', 'a', encoding='utf-8') as log:
            log.write(f'\n DATRA/HORA = {datetime.now()}. ERRO NA EXECUCAO DO DO SERVICO DE EMAIL. ERRO: {err}')

# tecnologia@giraffas.com.br
# SALVAR OS DADOS A  PARTIR DAS 10H00 E DISPARAR O ALERTA AS 11H00 
# REMOVER 
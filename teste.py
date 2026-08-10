from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as Ec

#Repositorio

lojas = []

# Executar navegacao 
navegador = webdriver.Chrome()
wait = WebDriverWait(navegador,20)

#realizar login
navegador.get('https://www.myorders.com.br/myorders')

empresa = wait.until(
    Ec.presence_of_element_located((By.ID,'SG_EMP'))
)
usuario = wait.until(
    Ec.presence_of_element_located((By.ID, 'NM_LOG_USU'))
)
senha = wait.until(
    Ec.presence_of_element_located((By.ID, 'DC_PASSWORD'))
)
botao = navegador.find_element(By.ID, 'btnLogin')


empresa.send_keys("giraffas")
usuario.send_keys("felipe.barbosa")
senha.send_keys("Fefo@2026")
botao.click()

wait.until(Ec.url_contains('MyOrders'))

navegador.get('https://www.myorders.com.br/MyOrders/PedidoWeb/StatusUnidade?status=ONLINE,OFFLINE&etb=&mrc=&program=')

#coletar informacao
    #unir as informacoes em formato de dinicionario -> marca, UF, unidade, statdos, ultimo acesso, versao do GCOMLINK
element = navegador.find_elements(By.CSS_SELECTOR, 'tr')

for i in element:
    colunas = i.find_elements(By.TAG_NAME, 'td')
    for coluna in colunas:
        print(coluna.text)
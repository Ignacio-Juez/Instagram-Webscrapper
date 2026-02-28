from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import time
import pandas as pd
from datetime import datetime

# Cargado de variables de entorno desde el archivo .env
load_dotenv()

# Obtención de credenciales desde las variables de entorno
username= os.getenv('INSTAGRAM_USERNAME')
password = os.getenv('INSTAGRAM_PASSWORD')

def login_to_instagram():
    print("Iniciando proceso de login...")

    if not username or not password:
        raise ValueError("Faltan las credenciales de Instagram en el archivo .env")

    chrome_options = Options()

    # Opciones para evitar detección
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Truco extra para evitar detección
    driver.execute_cdp_cmd(
        'Page.addScriptToEvaluateOnNewDocument',
        {'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''}
    )

    print("Abriendo Instagram...")
    driver.get("https://instagram.com")
    print("Esperando elementos de login")
    print("Ingresando credenciales")
    username_input = WebDriverWait(driver, timeout=10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email']"))
    )
    username_input.send_keys(username)

    password_input = driver.find_element(By.CSS_SELECTOR, "input[name='pass']")
    password_input.send_keys(password)

    login_button = driver.find_element(By.CSS_SELECTOR,"div[role='button'][aria-label='Iniciar sesión']")
    login_button.click()

    time.sleep(5)
    return driver

def get_followers(driver, username):
    print(f"Obteniendo seguidores de {username}...")
    # Navegar al perfil
    driver.get(f"https://www.instagram.com/{username}")
    print("Esperando a que cargue el perfil...")
    time.sleep(3)

    # Click en el enlace de seguidores
    print("Buscando enlace de seguidores...")
    followers_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href$='/followers/']"))
    )
    followers_count = followers_link.text
    lista_seguidores_texto = followers_link.text.split()
    if lista_seguidores_texto[1] =="mil":
        followers_count = int(lista_seguidores_texto[0]+"000")
    else: 
        followers_count = int(lista_seguidores_texto[0])
    print(followers_count)
    followers_link.click()
    time.sleep(5)

    # Detectar la pantalla de seguidores
    followers_xpath ='/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]'
    cuentas ='_ap3a._aaco._aacw._aacx._aad7._aade'

    followers = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, followers_xpath)))

    # SCROLL
    hora = datetime.now()
    diferencia = datetime.now() -hora
    segundos= diferencia.total_seconds()
    print(hora)
    fol_find = 0
    while followers_count > fol_find and segundos < 60:
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight;', followers)
        fol_find = len(driver.find_elements(By.CLASS_NAME, cuentas))
        print(fol_find)
        time.sleep(1)
        diferencia = datetime.now() - hora
        segundos = diferencia.total_seconds()

    # Obtener nombres de las cuentas
    mis_seguidores = driver.find_elements(By.CLASS_NAME, cuentas)

    seguidores = []
    for seguidor in mis_seguidores:
        print(seguidor.text)
        fol = seguidor.text
        seguidores.append(fol)
    
    return seguidores

def get_following(driver, username):
    print(f"Obteniendo seguidos de {username}...")

    # Navegar al perfil
    driver.get(f"https://www.instagram.com/{username}")
    print("Esperando a que cargue el perfil...")
    time.sleep(3)

    # Click en el enlace de seguidos
    print("Buscando enlace de seguidos...")
    following_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href$='/following/']"))
    )

    # Procesar número de seguidos igual que seguidores
    following_text = following_link.text.split()
    if len(following_text) > 1 and following_text[1] == "mil":
        following_count = int(following_text[0] + "000")
    else:
        following_count = int(following_text[0])

    print(f"Seguidos: {following_count}")

    following_link.click()
    time.sleep(5)

    # === ⭐ POSIBLE XPATH DIFERENTE AL DE FOLLOWERS ⭐ ===
    # ESTE XPATH ES EL MISMO QUE USAS EN FOLLOWERS.
    # SI NO FUNCIONA, NECESITO QUE ME PASES EL XPATH REAL DEL MODAL DE SEGUIDOS.
    following_xpath = '/html/body/div[4]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]'

    # === ⭐ POSIBLE CLASE DIFERENTE QUE FOLLOWERS ⭐ ===
    # ESTA ES LA MISMA QUE USAS EN FOLLOWERS
    cuentas = '_ap3a._aaco._aacw._aacx._aad7._aade'

    # Detecta el contenedor scrollable
    try:
        following_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, following_xpath))
        )
    except:
        print("❌ ERROR: el XPATH para SEGUIDOS NO funciona.")
        print("➡️ Necesito que abras el modal de SEGUIDOS, toques F12 y me pases el XPATH del div scrollable.")
        return []

    # SCROLL
    hora = datetime.now()
    fol_find = 0
    segundos = 0

    print("Scrolleando...")

    while following_count > fol_find and segundos < 60:
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight;', following_box)
        fol_find = len(driver.find_elements(By.CLASS_NAME, cuentas))
        print(f"{fol_find} cuentas cargadas...")
        time.sleep(1)

        segundos = (datetime.now() - hora).total_seconds()

    # Obtener nombres
    mis_seguidos = driver.find_elements(By.CLASS_NAME, cuentas)

    lista = []
    for seguido in mis_seguidos:
        texto = seguido.text.strip()
        if texto:
            print(texto)
            lista.append(texto)

    return lista



def save_to_excel(lista, columna, followers=None):
    df = pd.DataFrame(lista, columns=[columna])

    # Si estamos guardando seguidos, agregar columna extra
    if columna == "seguidos" and followers is not None:
        df['Me sigue'] = df['seguidos'].apply(lambda x: 'Si' if x in followers else 'No')

    filename = f'{columna}.xlsx'
    

    df.to_excel(filename, index=False)
    print(f"\nDatos guardados en: {filename}")
    
    return filename

if __name__ == "__main__":
    driver = login_to_instagram()
    followers = get_followers(driver, username)
    excel_file = save_to_excel(followers, "seguidores")
    followings = get_following(driver, username)
    excel_file = save_to_excel(followings, "seguidos", followers)
    input("Presiona Enter para cerrar el navegador...")
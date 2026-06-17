
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import pandas as pd
import traceback
import time
from datetime import datetime

ARQUIVO_EXCEL = "Atlas_Migracao_Teste.xlsx"

MESES = {
    "janeiro": 1,
    "fevereiro": 2,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}

def converter_horarios(texto):
    texto = str(texto).strip().lower()

    if " e " in texto:
        partes = texto.split(" e ")
        resultado = []

        for p in partes:
            p = p.strip().replace("h", ":")

            if p.endswith(":"):
                p += "00"

            if ":" not in p:
                p += ":00"

            resultado.append(p)

        return resultado

    texto = texto.replace("h30", ":30")
    texto = texto.replace("h", ":00")

    return [texto]


def abrir_nova_visita(wait):
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(.,'Nova Visita')]")
        )
    ).click()

    time.sleep(2)


def selecionar_categoria(driver, wait, categoria_texto):

    categoria = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[contains(.,'Selecionar categoria')]"
            )
        )
    )

    categoria.click()

    busca = wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "input[placeholder='Buscar categoria...']"
            )
        )
    )

    busca.clear()
    busca.send_keys(str(categoria_texto))
    time.sleep(1)
    busca.send_keys(Keys.ENTER)


def selecionar_data(driver, wait, data_str):

    data_obj = datetime.strptime(str(data_str), "%d/%m/%Y")

    alvo_mes = data_obj.month
    alvo_ano = data_obj.year
    alvo_dia = data_obj.day

    wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[contains(.,'Selecionar')]"
            )
        )
    ).click()

    time.sleep(1)

    while True:

        cabecalho = driver.find_element(
            By.XPATH,
            "//div[contains(@class,'font-medium') and contains(text(),'202')]"
        ).text.lower()

        partes = cabecalho.split()

        mes_atual = MESES[partes[0]]
        ano_atual = int(partes[1])

        atual = ano_atual * 12 + mes_atual
        alvo = alvo_ano * 12 + alvo_mes

        if atual == alvo:
            break

        if atual > alvo:
            driver.find_element(
                By.XPATH,
                "//button[@name='previous-month']"
            ).click()
        else:
            driver.find_element(
                By.XPATH,
                "//button[@name='next-month']"
            ).click()

        time.sleep(0.3)

    driver.find_element(
        By.XPATH,
        f"//button[@name='day' and text()='{alvo_dia}']"
    ).click()


try:

    df = pd.read_excel(ARQUIVO_EXCEL)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    driver.maximize_window()

    driver.get("https://fmloa.atlasconcierge.com.br/educativo")

    wait = WebDriverWait(driver, 30)

    email = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='email']")
        )
    )

    email.clear()
    email.send_keys("educativo@fundacaooscaramericano.org.br")

    senha = driver.find_element(
        By.CSS_SELECTOR,
        "input[type='password']"
    )

    senha.clear()
    senha.send_keys("pWV2jPKCj7CAZR!9")

    driver.find_element(
        By.XPATH,
        "//button[contains(., 'Entrar no portal')]"
    ).click()

    print("LOGIN OK")

    time.sleep(5)

    total_visitas = 0

    for _, linha in df.iterrows():

        horarios = converter_horarios(
            linha["Horário"]
        )

        for horario_atual in horarios:

            print(
                f"Cadastrando: "
                f"{linha['Nome do Grupo/Turma']} "
                f"- {horario_atual}"
            )

            abrir_nova_visita(wait)

            selecionar_data(
                driver,
                wait,
                linha["Data Atlas"]
            )

            campo_hora = driver.find_element(
                By.CSS_SELECTOR,
                "input[type='time']"
            )

            campo_hora.clear()
            campo_hora.send_keys(horario_atual)

            selecionar_categoria(
                driver,
                wait,
                linha["Categoria"]
            )

            grupo = driver.find_element(
                By.XPATH,
                "//input[contains(@placeholder,'Turma')]"
            )

            grupo.clear()
            grupo.send_keys(
                str(linha["Nome do Grupo/Turma"])
            )

            educador = driver.find_element(
                By.XPATH,
                "//input[contains(@placeholder,'educador')]"
            )

            educador.clear()
            educador.send_keys(
                str(linha["Educador"])
            )

            participantes = driver.find_element(
                By.XPATH,
                "//input[@type='number']"
            )

            participantes.clear()
            participantes.send_keys(
                str(int(linha["Qtd. Participantes"]))
            )

            observacoes = driver.find_element(
                By.TAG_NAME,
                "textarea"
            )

            observacoes.clear()
            observacoes.send_keys(
                str(linha["Observações"])
            )

            salvar = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//button[contains(.,'Salvar')]"
                    )
                )
            )

            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                salvar
            )

            time.sleep(1)

            driver.execute_script(
                "arguments[0].click();",
                salvar
            )

            total_visitas += 1

            print(f"Salvo ({total_visitas})")

            time.sleep(3)

    print()
    print("FINALIZADO")
    print(f"Total de visitas: {total_visitas}")

    input("ENTER para encerrar")
except Exception:
    traceback.print_exc()
    input("Pressione ENTER para sair...")

"""
Configuración global de pytest para la suite de regresión AMV Travel.

Fixtures disponibles:
  - driver             : navegador Chrome headless limpio.
  - logged_in_driver   : driver con login en el Frontend ya resuelto.

Además:
  - Captura automática de screenshot ante cualquier fallo.
  - Genera el environment.properties de Allure con el entorno real.
"""
import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# -------------------------------------------------------------------
# Driver base
# -------------------------------------------------------------------
@pytest.fixture(scope="function")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()


# -------------------------------------------------------------------
# Login silencioso al Frontend (usado por los flujos de web/)
# -------------------------------------------------------------------
@pytest.fixture(scope="function")
def logged_in_driver(driver):
    wait = WebDriverWait(driver, 15)

    usuario = os.environ.get("AMV_USER")
    password = os.environ.get("AMV_PASS")
    if not usuario or not password:
        pytest.fail("Faltan las credenciales (AMV_USER / AMV_PASS) en el entorno.")

    driver.get("https://preprod.amv.travel/")
    wait.until(EC.element_to_be_clickable((By.ID, "lnkLogin"))).click()

    input_user = wait.until(EC.presence_of_element_located((By.ID, "txtUser")))
    input_user.clear()
    input_user.send_keys(usuario)

    input_pass = driver.find_element(By.ID, "txtPassword")
    input_pass.clear()
    input_pass.send_keys(password)

    btn = wait.until(EC.presence_of_element_located((By.ID, "btnLogin")))
    driver.execute_script("arguments[0].click();", btn)

    time.sleep(3)  # carga inicial del sistema
    yield driver


# -------------------------------------------------------------------
# Captura automática de screenshot ante cualquier fallo de test
# -------------------------------------------------------------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        drv = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
        if drv is not None:
            try:
                import allure
                allure.attach(
                    drv.get_screenshot_as_png(),
                    name=f"FALLO_{item.name}",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass


# -------------------------------------------------------------------
# Allure environment
# -------------------------------------------------------------------
def pytest_sessionfinish(session, exitstatus):
    allure_dir = "allure-results"
    if not os.path.exists(allure_dir):
        os.makedirs(allure_dir)

    env_file = os.path.join(allure_dir, "environment.properties")
    with open(env_file, "w", encoding="utf-8") as f:
        f.write("Entorno=Preprod\n")
        f.write("Navegador=Chrome (Headless)\n")
        f.write("URL_Frontend=https://preprod.amv.travel/\n")
        f.write("URL_BackOffice=https://preprod.bo.amv.travel/\n")
        f.write("Framework=Pytest+Selenium\n")

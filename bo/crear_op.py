import pytest
import allure
import os
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementNotInteractableException


# =========================
# HELPERS ROBUSTOS
# =========================

def safe_click(wait, locator):
    for _ in range(5):
        try:
            elem = wait.until(EC.element_to_be_clickable(locator))
            elem.click()
            return
        except StaleElementReferenceException:
            time.sleep(2)
    raise Exception(f"No se pudo hacer click: {locator}")


def safe_send_keys(wait, locator, value):
    for _ in range(5):
        try:
            elem = wait.until(EC.visibility_of_element_located(locator))

            # Scroll al elemento
            wait._driver.execute_script("arguments[0].scrollIntoView(true);", elem)
            time.sleep(1)

            elem.clear()
            elem.send_keys(value)
            return

        except (StaleElementReferenceException, ElementNotInteractableException):
            try:
                # Fallback JS nativo si se bloquea
                elem = wait.until(EC.presence_of_element_located(locator))
                wait._driver.execute_script("arguments[0].value = arguments[1];", elem, value)
                return
            except:
                time.sleep(2)

    raise Exception(f"No se pudo escribir en: {locator}")


# =========================
# TEST
# =========================

@allure.epic("BO")
@allure.feature("Crear Orden de Pago / Cobro")
@allure.story("Crear Orden de Pago")
@allure.severity(allure.severity_level.CRITICAL)
def test_crear_orden_pago(driver):

    # Timeout holgado de 45 segundos para servidores lentos de preprod
    wait = WebDriverWait(driver, 45)

    # ==========================================
    # 1. LOGIN (Igual a crear_oc.py)
    # ==========================================
    with allure.step("1. Login"):
        driver.get("https://preprod.bo.amv.travel/login")

        user = os.environ.get("AMV_USER")
        password = os.environ.get("BO_PASS")

        if not user or not password:
            pytest.fail("Faltan variables de entorno")

        safe_send_keys(wait, (By.ID, "txtUser"), user)
        safe_send_keys(wait, (By.ID, "txtPassword"), password)
        safe_click(wait, (By.ID, "btnLogin"))

        wait.until(EC.url_contains("/main"))
        allure.attach(driver.get_screenshot_as_png(), "1_Login", allure.attachment_type.PNG)

    # ==========================================
    # 2. NAVEGACIÓN Y APERTURA DEL FORMULARIO
    # ==========================================
    with allure.step("2. Click en Administración (Menú Lateral)"):
        # Clickeamos el menú principal para desplegar las opciones
        safe_click(wait, (By.XPATH, "//span[contains(text(), 'Administración')]"))
        allure.attach(driver.get_screenshot_as_png(), "2_Menu_Administracion_Desplegado", allure.attachment_type.PNG)

    with allure.step("2.1 Ir a sección PayOrders"):
        # Click en el submenú de Órdenes de Pago
        safe_click(wait, (By.XPATH, "//a[contains(@href, '/administration/payorders')]"))
        allure.attach(driver.get_screenshot_as_png(), "2_1_Listado_PayOrders", allure.attachment_type.PNG)

    with allure.step("2.2 Click en Crear Orden de Pago (Nuevo Registro)"):
        # Buscamos y clickeamos el botón específico usando la clase provista
        safe_click(wait, (By.CSS_SELECTOR, "a.btn.btn-sm.btn-info.btn-icon.m-t4.usepreload"))
        time.sleep(4)
        allure.attach(driver.get_screenshot_as_png(), "2_2_Nuevo_Formulario", allure.attachment_type.PNG)

    # ==========================================
    # 3. SELECCIONAR PROVEEDOR MAX BAIRES
    # ==========================================
    with allure.step("3. Buscar y Seleccionar Proveedor MAX BAIRES"):
        safe_click(wait, (By.ID, "btnSupplier"))
        search = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='search']")))
        search.clear()
        search.send_keys("MAX BAIRES")

        fila_proveedor = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "sorting_1")))
        driver.execute_script("arguments[0].click();", fila_proveedor)
        time.sleep(5)  # Espera prudencial para que cargue la info heredada por el PostBack del proveedor
        allure.attach(driver.get_screenshot_as_png(), "3_Proveedor_Seleccionado", allure.attachment_type.PNG)

    # ==========================================
    # 4. REFERENCIA DE PAGO (Value='40')
    # ==========================================
    with allure.step("4. Seleccionar Referencia de Pago (Value='40')"):
        Select(wait.until(EC.element_to_be_clickable((By.NAME, "ctl00$cphMain$ddPaymentRefs"))))\
            .select_by_value("40")
        allure.attach(driver.get_screenshot_as_png(), "4_PaymentRef", allure.attachment_type.PNG)

    # ==========================================
    # 5. DETALLE
    # ==========================================
    with allure.step("5. Ingresar Detalle"):
        safe_send_keys(wait, (By.NAME, "ctl00$cphMain$txtDetail"), "Test Automático")
        allure.attach(driver.get_screenshot_as_png(), "5_Detalle", allure.attachment_type.PNG)

    # ==========================================
    # 6. MONEDA (Value='10') + 5s Sleep
    # ==========================================
    with allure.step("6. Seleccionar Moneda (Value='10')"):
        Select(wait.until(EC.element_to_be_clickable((By.NAME, "ctl00$cphMain$ddCurrency"))))\
            .select_by_value("10")
        time.sleep(5)  # Espera de 5 segundos solicitada por carga
        allure.attach(driver.get_screenshot_as_png(), "6_Currency", allure.attachment_type.PNG)

    # ==========================================
    # 7. CAJA (Value='8') + 5s Sleep
    # ==========================================
    with allure.step("7. Seleccionar Caja (Value='8')"):
        Select(wait.until(EC.element_to_be_clickable((By.NAME, "ctl00$cphMain$ddCashFlow1"))))\
            .select_by_value("8")
        time.sleep(5)  # Espera de 5 segundos solicitada por carga
        allure.attach(driver.get_screenshot_as_png(), "7_CashFlow", allure.attachment_type.PNG)

    # ==========================================
    # 8. MONTO
    # ==========================================
    with allure.step("8. Ingresar Monto"):
        safe_send_keys(wait, (By.NAME, "ctl00$cphMain$txtAmount1"), "900000")
        allure.attach(driver.get_screenshot_as_png(), "8_Monto", allure.attachment_type.PNG)

    # ==========================================
    # 9. GUARDAR + 8s Sleep
    # ==========================================
    with allure.step("9. Guardar Registro"):
        url_antes_de_guardar = driver.current_url
        safe_click(wait, (By.XPATH, "//input[@type='submit' and @name='ctl00$cphMain$btnSave']"))
        time.sleep(8)  # Espera de 8 segundos para procesamiento completo
        allure.attach(driver.get_screenshot_as_png(), "9_Guardado", allure.attachment_type.PNG)

        # DIAGNÓSTICO: dejamos registro de la URL para saber si el Guardar redirigió
        allure.attach(
            f"URL antes de Guardar: {url_antes_de_guardar}\nURL después de Guardar: {driver.current_url}",
            "9_URLs",
            allure.attachment_type.TEXT,
        )

        # DIAGNÓSTICO: buscamos mensajes de validación / error que bloqueen el guardado
        errores = driver.find_elements(
            By.CSS_SELECTOR,
            ".validation-summary-errors, .field-validation-error, .alert-danger, span[id*='Error'], .text-danger"
        )
        textos_error = [e.text.strip() for e in errores if e.text.strip()]
        if textos_error:
            allure.attach(
                "\n".join(textos_error),
                "9_Mensajes_de_validacion",
                allure.attachment_type.TEXT,
            )

    # ==========================================
    # 10. SCROLL A ZONA DE IMPUTACIÓN
    # ==========================================
    with allure.step("10. Scroll a zona de imputación"):
        # Forzamos scroll al fondo para que la zona de imputación quede en viewport
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        allure.attach(driver.get_screenshot_as_png(), "10_Pagina_OP_Creada", allure.attachment_type.PNG)

    # ==========================================
    # 11. CLICK ASIGNAR TOTAL
    # ==========================================
    with allure.step("11. Click en Asignar Total"):
        # Esperamos el link de imputar (id según Katalon: lnkAsignarTotal).
        # Si no aparece, adjuntamos diagnóstico ANTES de fallar para poder ver
        # qué hay realmente en la página (URL, screenshot y si la grilla existe).
        try:
            btn_asignar_total = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "a[id$='lnkAsignarTotal'], #lnkAsignarTotal"
            )))
        except Exception:
            allure.attach(driver.get_screenshot_as_png(), "ERROR_11_sin_link_imputar", allure.attachment_type.PNG)
            allure.attach(f"URL actual: {driver.current_url}", "ERROR_11_URL", allure.attachment_type.TEXT)

            # ¿Existe alguna tabla/link con id parecido? Listamos para descubrir el id real.
            candidatos = driver.find_elements(By.CSS_SELECTOR, "a[id*='Asignar'], a[id*='asignar'], a[id*='lnk']")
            ids = [c.get_attribute("id") for c in candidatos if c.get_attribute("id")]
            allure.attach(
                "Links con id parecido encontrados en la página:\n" + ("\n".join(ids) if ids else "NINGUNO"),
                "ERROR_11_links_candidatos",
                allure.attachment_type.TEXT,
            )
            pytest.fail(
                "No apareció el link de imputar (lnkAsignarTotal). "
                f"URL actual: {driver.current_url}. "
                "Revisar adjuntos: probablemente el Guardar falló por validación "
                "o no hay comprobantes para imputar con esa combinación proveedor/moneda/caja."
            )

        driver.execute_script("arguments[0].scrollIntoView(true);", btn_asignar_total)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", btn_asignar_total)
        time.sleep(5)
        allure.attach(driver.get_screenshot_as_png(), "11_Asignar_Total_Clickeado", allure.attachment_type.PNG)

    # ==========================================
    # 12 y 13. VALIDAR TABLA INTERNA Y ENCUADRE
    # ==========================================
    with allure.step("12 y 13. Validar existencia de celda en tabla interna"):
        # Buscamos la grilla interna que contenga datos
        celda_tabla = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            ".table.table-striped.table-bordered.table-hover.table-condensed.text-center.m-b-0 td.text-center"
        )))

        # Scroll extra controlado para forzar visibilidad total en Allure
        driver.execute_script("arguments[0].scrollIntoView(false);", celda_tabla)
        driver.execute_script("window.scrollBy(0, 150);")
        time.sleep(2)
        allure.attach(driver.get_screenshot_as_png(), "13_Tabla_Interna_Con_Datos", allure.attachment_type.PNG)

    # ==========================================
    # 14. INGRESAR FECHA ACTUAL + 5s Sleep
    # ==========================================
    with allure.step("14. Ingresar fecha actual"):
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        safe_send_keys(wait, (By.NAME, "ctl00$cphMain$txtReceiptDate"), fecha_hoy)
        time.sleep(5)  # Espera de 5 segundos solicitada por carga
        allure.attach(driver.get_screenshot_as_png(), "14_Fecha_Ingresada", allure.attachment_type.PNG)

    # ==========================================
    # 15. APROBAR + 8s Sleep
    # ==========================================
    with allure.step("15. Click en Aprobar Orden de Pago"):
        boton_aprobar = wait.until(EC.presence_of_element_located((
            By.XPATH,
            "//input[@type='submit' and @name='ctl00$cphMain$btnApprove']"
        )))
        driver.execute_script("arguments[0].scrollIntoView(true);", boton_aprobar)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", boton_aprobar)
        time.sleep(8)  # Espera de 8 segundos solicitada para que procese el backend pesado de aprobación
        allure.attach(driver.get_screenshot_as_png(), "15_Click_Aprobar", allure.attachment_type.PNG)

    # ==========================================
    # 16. VALIDAR DESAPARICIÓN DEL BOTÓN
    # ==========================================
    with allure.step("16. Validar que el botón Aprobar ya no exista"):
        wait.until(EC.invisibility_of_element_located((
            By.XPATH,
            "//input[@type='submit' and @name='ctl00$cphMain$btnApprove']"
        )))
        allure.attach(driver.get_screenshot_as_png(), "16_Fin_Test_Exitoso", allure.attachment_type.PNG)

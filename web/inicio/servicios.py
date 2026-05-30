import pytest
import allure
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from diagnostico import diagnosticar_fallo

@allure.epic("WEB")
@allure.feature("Inicio")
@allure.story("Reservar Servicios")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Este caso de prueba cubre el flujo End-to-End (E2E) de la reserva de un servicio:
1. Login silencioso y navegación a la pestaña de Servicios.
2. Búsqueda filtrada por Destino (Bariloche) y Tipo (Excursión).
3. Validación de la interfaz (UI) en las cards de resultados y el detalle interno.
4. Selección de cantidad de pasajeros.
5. Confirmación de reserva y validación final comprobando que el carrito sume 4 ítems.
6. Flujo de Finalización de Compra (Checkout) y carga de datos del pasajero.
""")
def test_reserva_servicio_flujo_completo(logged_in_driver):
    driver = logged_in_driver
    wait = WebDriverWait(driver, 15)
    actions = ActionChains(driver)
    
    # Declaramos la variable de control al inicio para reutilizarla en las validaciones
    texto_referencia = "Test Automático"

    with allure.step("1 a 5. Seleccionar pestaña Servicios, ingresar destino, tipo y buscar"):
        try:
            # 2. Click en la pestaña de Servicios
            tab_servicios = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tabServices']")), message="No se encontró la pestaña a[href='#tabServices']")
            tab_servicios.click()
            time.sleep(1)

            # 3. Dropdown Destino (Ciudad)
            btn_ciudad = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#ctl00_cphMainSlider_ctl00_ctrlServiceSearchControl_updServicesCity .ts-control")), message="No se encontró el control del DDL de Ciudad")
            btn_ciudad.click()
            time.sleep(1) # Esperamos que se despliegue la lista
            opcion_bariloche = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'option') and contains(text(), 'Bariloche')] | //div[contains(text(), 'Bariloche')]")), message="No se encontró la opción 'Bariloche' en la lista")
            opcion_bariloche.click()
            time.sleep(1)

            # 4. Dropdown Tipo de Servicio (Opcionales)
            btn_tipo = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#ctl00_cphMainSlider_ctl00_ctrlServiceSearchControl_updServicesOptionals .ts-control")), message="No se encontró el control del DDL de Tipo de Servicio")
            btn_tipo.click()
            time.sleep(1) # Esperamos que se despliegue la lista
            opcion_excursion = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'option') and contains(text(), 'Excursión')] | //div[contains(text(), 'Excursión')]")), message="No se encontró la opción 'Excursión' en la lista")
            opcion_excursion.click()
            time.sleep(1)

            # --- CAPTURA PREVIA A LA BÚSQUEDA (Pasos 1 al 4 completados) ---
            allure.attach(driver.get_screenshot_as_png(), name="Formulario_Completo_Antes_Buscar", attachment_type=allure.attachment_type.PNG)

            # 5. Click en Buscar
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_ctl00_ctrlServiceSearchControl_btnSearch")), message="No se encontró el botón de Buscar (btnSearch)").click()

            # Espera larga para los resultados
            wait_largo = WebDriverWait(driver, 45)
            wait_largo.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.panelShadow.col-sm-6")), message="La búsqueda superó los 45 segundos y no cargaron los resultados de servicios")
            time.sleep(2)

            allure.attach(driver.get_screenshot_as_png(), name="Busqueda_Ejecutada", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_1_a_5", attachment_type=allure.attachment_type.PNG)
            diagnosticar_fallo(driver, e, paso="Error al ingresar filtros de búsqueda")

    with allure.step("6. Validar panel de resultados (Cards de Servicios)"):
        try:
            # a. Validar que exista la card
            assert driver.find_elements(By.CSS_SELECTOR, "div.panelShadow.col-sm-6"), "No se encontró ningún div con la clase 'panelShadow col-sm-6'"

            # b, c, d, e, f. Validar components internos de la card
            assert driver.find_elements(By.CSS_SELECTOR, "img[style*='width: 450px']"), "Falta la imagen de 450x323px en la card"
            assert driver.find_elements(By.CSS_SELECTOR, "h4.h4Span"), "Falta el nombre del servicio (h4Span)"
            assert driver.find_elements(By.CSS_SELECTOR, "table[style*='text-align:center'], table[style*='text-align: center']"), "Falta la tabla de precios/tipo centrada"
            assert driver.find_elements(By.CSS_SELECTOR, "div.divservlimit"), "Falta la descripción del servicio (divservlimit)"
            assert driver.find_elements(By.CSS_SELECTOR, "a.apreload.btn.btnGray.pink-btn"), "Falta el botón de selección/ver más"

            allure.attach(driver.get_screenshot_as_png(), name="Resultados_Validados", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_6", attachment_type=allure.attachment_type.PNG)
            diagnosticar_fallo(driver, e, paso="Error en validación de las cards de servicio")

    with allure.step("7 y 8. Click en servicio y validar detalle interno"):
        try:
            # 7. Click en el botón
            btn_seleccionar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.apreload.btn.btnGray.pink-btn")), message="No se encontró el botón para entrar al servicio")
            btn_seleccionar.click()
            time.sleep(3) # Espera a que cargue el detalle

            # 8. Validaciones de la vista de detalle
            assert wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3.h3ServiceName")), message="No cargó el Detalle del Servicio (falta h3ServiceName)")
            assert driver.find_elements(By.CSS_SELECTOR, "img.popu"), "Falta la imagen del servicio (popu)"
            assert driver.find_elements(By.CSS_SELECTOR, "div.detailsdiv"), "Faltan los detalles del servicio (detailsdiv)"
            assert driver.find_elements(By.CSS_SELECTOR, "table.table.table-bordered.table-striped"), "Falta la tabla de precios detallada"

            allure.attach(driver.get_screenshot_as_png(), name="Detalle_Servicio_Validado", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_7_a_8", attachment_type=allure.attachment_type.PNG)
            diagnosticar_fallo(driver, e, paso="Fallo al ingresar o validar el detalle del servicio")

    with allure.step("9 y 10. Seleccionar pasajeros"):
        try:
            # 9. Primer select (Pax 1)
            select_pax_1 = Select(wait.until(EC.presence_of_element_located((By.NAME, "ctl00$cphMainSlider$lvServiceRates$ctrl0$ctrlPaxQuantityControl$ddPax")), message="No se encontró el primer DDL de pasajeros"))
            select_pax_1.select_by_visible_text("2")

            # 10. Segundo select (Pax 2)
            select_pax_2 = Select(wait.until(EC.presence_of_element_located((By.NAME, "ctl00$cphMainSlider$lvServiceRates$ctrl1$ctrlPaxQuantityControl$ddPax")), message="No se encontró el segundo DDL de pasajeros"))
            select_pax_2.select_by_visible_text("2")

            time.sleep(1)
            allure.attach(driver.get_screenshot_as_png(), name="Pasajeros_Seleccionados", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Paso_9_a_10", attachment_type=allure.attachment_type.PNG)
            diagnosticar_fallo(driver, e, paso="Error al seleccionar la cantidad de pasajeros")

    # =========================================================================
    # PASO 11 Y 12 CORREGIDO: Blindado contra StaleElementReferenceException
    # =========================================================================
    with allure.step("11 y 12. Confirmar reserva y validar incremento en el carrito"):
        try:
            # 1. Obtener el valor actual del carrito ANTES de reservar
            cart_element = wait.until(EC.presence_of_element_located((By.ID, "lblCartCount")), message="No se encontró el contador del carrito")
            initial_cart_text = cart_element.text.strip()
            initial_cart_count = int(initial_cart_text) if initial_cart_text.isdigit() else 0
            expected_count = initial_cart_count + 4

            # 2. Captura del botón con reintentos para absorber el refresco asincrónico (UpdatePanel)
            btn_reservar = None
            for _ in range(5):
                try:
                    btn_reservar = wait.until(EC.element_to_be_clickable((By.ID, "ctl00_cphMainSlider_lnkBookService")))
                    break
                except Exception:
                    time.sleep(1) # Pausa estabilizadora si el DOM sigue mutando

            if not btn_reservar:
                pytest.fail("No se pudo interactuar con el botón de reservar por inestabilidad en el postback del DOM.")
            
            btn_reservar.click()

            # 3. Manejar el alert si existe
            try:
                alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
                alert.accept()
            except:
                pass 

            # 4. Validar asincrónicamente el incremento dinámico (+4)
            wait.until(
                lambda d: int(d.find_element(By.ID, "lblCartCount").text.strip() or 0) == expected_count,
                message=f"La reserva falló: El carrito no se actualizó al valor esperado ({expected_count})"
            )

            allure.attach(driver.get_screenshot_as_png(), name="Reserva_Exitosa_Carrito_Actualizado", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Validacion_Carrito", attachment_type=allure.attachment_type.PNG)
            diagnosticar_fallo(driver, e, paso="Ocurrió un error al validar el carrito")

    with allure.step("13. Ir al carrito y Finalizar"):
        try:
            cart_anchor = wait.until(EC.visibility_of_element_located((By.ID, "AncoreShoppingCart")))
            actions.move_to_element(cart_anchor).perform()
            time.sleep(1)

            btn_finalizar = wait.until(EC.element_to_be_clickable((By.ID, "btnFinalizar")))
            allure.attach(driver.get_screenshot_as_png(), name="Dropdown_Carrito", attachment_type=allure.attachment_type.PNG)
            btn_finalizar.click()
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Finalizar_Carrito", attachment_type=allure.attachment_type.PNG)
            diagnosticar_fallo(driver, e, paso="Error al intentar finalizar la compra")

    with allure.step("14. Completar Referencia y Comentarios"):
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-bordered.table-striped")))

            driver.find_element(By.NAME, "ctl00$cphMain$txtReference").send_keys(texto_referencia)

            fecha_hoy = datetime.now().strftime("%d/%m/%Y")
            driver.find_element(By.NAME, "ctl00$cphMain$txtComment").send_keys(f"Este es un test autómatico ejecutado el día {fecha_hoy}")

            allure.attach(driver.get_screenshot_as_png(), name="Referencia_Completada", attachment_type=allure.attachment_type.PNG)

            btn_success = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-success.apreload")))
            btn_success.click()
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Referencia_Comentarios", attachment_type=allure.attachment_type.PNG)
            diagnosticar_fallo(driver, e, paso="Error en referencia y comentarios")

    with allure.step("15. Cargar Comentarios de Servicio y Datos de Pasajeros"):
        try:
            time.sleep(3)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table.table-bordered.table-striped")))

            input_comentario1 = wait.until(EC.presence_of_element_located((By.NAME, "ctl00$cphMain$lvBooking$ctrl0$ctrlBookingServiceDetailControl$txtDetail")))
            input_comentario1.send_keys("Comentario 1")

            driver.find_element(By.NAME, "ctl00$cphMain$lvBooking$ctrl1$ctrlBookingServiceDetailControl$txtDetail").send_keys("Comentario 2")

            driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtName").send_keys("Alan")
            driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtSurName").send_keys("QA")
            driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtPassport").send_keys("PAS123456789")
            driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtBirthday").send_keys("02061990")
            driver.find_element(By.ID, "ctl00_cphMain_lvPassengersData_ctrl0_txtNationality").send_keys("Argentino")

            pax_q = driver.find_element(By.ID, "ctl00_cphMain_txtPaxQuantity")
            pax_q.clear()
            pax_q.send_keys("2")

            checkbox = driver.find_element(By.ID, "ctl00_cphMain_cbxTermsAndConditions")
            if not checkbox.is_selected():
                checkbox.click()

            allure.attach(driver.get_screenshot_as_png(), name="Datos_Pasajeros_Completos", attachment_type=allure.attachment_type.PNG)

            # === SCROLL EXTREMO Y CLICK ===
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) 

            btn_guardar = wait.until(EC.presence_of_element_located((
                By.XPATH, "//input[@id='ctl00_cphMain_btnSaveBook' and @type='button' and @value='Confirmar reserva']"
            )))
            
            driver.execute_script("arguments[0].click();", btn_guardar)
            
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Datos_Pasajeros", attachment_type=allure.attachment_type.PNG)
            diagnosticar_fallo(driver, e, paso="Error al cargar datos del pasajero")

    # =========================================================================
    # PASO 16: Buscar el <p> dentro de un <td> de la primera fila
    # =========================================================================
    with allure.step("16. Validación final de éxito en pestaña Booking"):
        try:
            wait_largo = WebDriverWait(driver, 60)
            
            # 1. Esperamos y hacemos click por JS en la pestaña con href="#tabBooking"
            tab_booking = wait_largo.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#tabBooking']")), 
                message="No se encontró o no fue clickeable la pestaña a[href='#tabBooking']"
            )
            driver.execute_script("arguments[0].click();", tab_booking)
            time.sleep(2)

            # 2. Validamos la existencia física de la tabla requerida
            wait_largo.until(
                EC.presence_of_element_located((By.ID, "tableTab1")), 
                message="El checkout terminó pero no se encontró la tabla de control con id='tableTab1'"
            )

            # 3. XPATH ULTRA PRECISO: Primer tr -> td -> p conteniendo tu referencia variable
            xpath_p_primera_fila = f"//table[@id='tableTab1']//tr[1]//td/p[contains(text(), '{texto_referencia}')]"
            
            wait_largo.until(
                EC.presence_of_element_located((By.XPATH, xpath_p_primera_fila)),
                message=f"Fallo de datos: No se encontró el tag <p> con la referencia '{texto_referencia}' dentro de la primera fila de #tableTab1"
            )

            allure.attach(driver.get_screenshot_as_png(), name="Reserva_Finalizada_Exito", attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            allure.attach(driver.get_screenshot_as_png(), name="Fallo_Validacion_Final", attachment_type=allure.attachment_type.PNG)
            diagnosticar_fallo(driver, e, paso="Error en validación final en la pestaña Booking")

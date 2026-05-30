"""
Helper de diagnóstico de fallos para la suite AMV Travel.

Convierte excepciones técnicas de Selenium (StaleElement, Timeout, stacktraces
de Chrome ilegibles) en mensajes claros que indican QUÉ falló, distinguiendo
fallos de la aplicación (p. ej. un alert de error del sitio) de fallos del test.

Uso en cada test:

    from diagnostico import diagnosticar_fallo
    ...
    except Exception as e:
        diagnosticar_fallo(driver, e, paso="11. Descargar Word")
"""
import allure
import pytest
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    StaleElementReferenceException,
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)


def _texto_de_alert(driver):
    """Devuelve el texto de un alert nativo si hay uno abierto, o None."""
    try:
        alerta = driver.switch_to.alert
        texto = alerta.text
        return texto
    except Exception:
        return None


def diagnosticar_fallo(driver, error, paso="(sin especificar)"):
    """
    Analiza el error, adjunta diagnóstico a Allure y termina el test con
    pytest.fail() usando un mensaje claro. SIEMPRE corta el test (no retorna).
    """
    # 1. ¿Hay un alert nativo de la aplicación? Esto suele ser un ERROR DE LA APP.
    #    Es el caso más valioso: el mensaje del alert es el error real del sitio.
    texto_alert = _texto_de_alert(driver)

    # 2. Screenshot del momento del fallo (si el alert no lo impide)
    try:
        allure.attach(
            driver.get_screenshot_as_png(),
            name=f"FALLO_{paso}",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        # Un alert abierto bloquea el screenshot; lo cerramos y reintentamos
        if texto_alert is not None:
            try:
                driver.switch_to.alert.accept()
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name=f"FALLO_{paso}_post_alert",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass

    # 3. URL del momento del fallo
    try:
        allure.attach(driver.current_url, name="URL_al_fallar",
                      attachment_type=allure.attachment_type.TEXT)
    except Exception:
        pass

    # 4. Construir el mensaje claro según el tipo de fallo
    if texto_alert is not None:
        mensaje = (
            f"[{paso}] LA APLICACIÓN MOSTRÓ UN ERROR (alert del navegador): "
            f"\"{texto_alert}\". "
            f"Esto indica un fallo de la aplicación, no del test."
        )
    elif isinstance(error, UnexpectedAlertPresentException):
        # El alert apareció pero ya se cerró; intentamos rescatar su texto
        txt = getattr(error, "alert_text", None) or "(texto no disponible)"
        mensaje = (
            f"[{paso}] LA APLICACIÓN MOSTRÓ UN ERROR (alert inesperado): "
            f"\"{txt}\". Fallo de la aplicación, no del test."
        )
    elif isinstance(error, StaleElementReferenceException):
        mensaje = (
            f"[{paso}] El elemento se volvió obsoleto (stale): la página se "
            f"recargó o redibujó mientras el test interactuaba con él. "
            f"Puede deberse a que la app recargó la sección inesperadamente."
        )
    elif isinstance(error, TimeoutException):
        detalle = (error.msg or "").strip()
        mensaje = (
            f"[{paso}] Se agotó el tiempo de espera de un elemento. "
            f"{('Detalle: ' + detalle) if detalle else 'El elemento esperado nunca apareció.'} "
            f"Puede ser lentitud del sitio o que el elemento no se renderizó."
        )
    elif isinstance(error, NoSuchElementException):
        mensaje = (
            f"[{paso}] No se encontró un elemento esperado en la página. "
            f"Puede que la UE haya cambiado o que un paso previo no dejó la "
            f"pantalla en el estado esperado."
        )
    elif isinstance(error, ElementClickInterceptedException):
        mensaje = (
            f"[{paso}] No se pudo clickear: otro elemento tapaba el objetivo "
            f"(p. ej. un modal, overlay o banner). Posible problema de UI."
        )
    else:
        # Fallback: tipo de error + solo la primera línea (sin stacktrace de Chrome)
        primera_linea = str(error).strip().split("\n")[0]
        mensaje = (
            f"[{paso}] Fallo inesperado ({type(error).__name__}): {primera_linea}"
        )

    allure.attach(mensaje, name="Diagnostico", attachment_type=allure.attachment_type.TEXT)
    pytest.fail(mensaje)

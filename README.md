# AMV Travel — Suite de Regresión Funcional (Preprod)

Automatización E2E del **Frontend** (`amv.travel`) y **BackOffice** (`bo.amv.travel`)
con **pytest + Selenium** y reportes **Allure** publicados en GitHub Pages.

## Estructura

```
.
├── conftest.py            # Fixtures (driver, logged_in_driver) + captura de fallos + Allure env
├── pytest.ini             # Configuración de recolección de tests
├── requirements.txt       # Dependencias pineadas
├── .github/workflows/
│   └── regresion.yml       # CI: corre toda la suite y publica el reporte
├── bo/                    # Tests del BackOffice
│   ├── bo_login_admin.py
│   ├── login_noadmin.py
│   ├── crear_op.py
│   ├── crear_oc.py
│   ├── reservas.py
│   ├── cotizaciones.py
│   └── generar_file.py
├── web.py                 # Flujo principal del front
└── web/                   # Tests del Frontend
    ├── inicio/            # login admin/agencia, hoteles, ofertas, servicios
    ├── multidestino/
    └── tarifario/         # hoteles, ofertas, excursiones, cruceros, cenashow, traslados, paquetes
```

## Reporte Allure: un solo reporte, jerárquico

Todos los tests publican a un **único reporte** (una sola URL de GitHub Pages).
Dentro, en la solapa **Behaviors**, la navegación queda organizada así
(via `@allure.epic / @allure.feature / @allure.story`):

```
Reporte único
├── BO
│   ├── Login BackOffice           (admin / no-admin)
│   ├── Crear Orden de Pago / Cobro
│   ├── Reservas / Cotizaciones
│   └── Generar File
└── WEB
    ├── Inicio                      (login, hoteles, ofertas, servicios)
    ├── Multidestino
    └── Tarifario                   (hoteles, ofertas, excursiones, cruceros, cenashow, traslados, paquetes)
```

## Cómo correr localmente

```bash
pip install -r requirements.txt

# Credenciales (en CI son GitHub Secrets; nunca hardcodear)
export AMV_USER=...    AMV_PASS=...
export BO_USER=...     BO_PASS=...
export AMV_AGENCIA_USER=...

pytest --alluredir=allure-results       # toda la suite
pytest bo/                              # solo BackOffice
pytest web/                             # solo Frontend
pytest bo/crear_op.py                   # un test puntual

allure serve allure-results             # ver el reporte localmente
```

## CI / GitHub Actions

En cada push a `main` (o manualmente con *workflow_dispatch*), el workflow:
1. Instala dependencias.
2. Corre **toda la suite** (`pytest --alluredir=allure-results`).
3. Guarda los resultados crudos como artifact.
4. Genera el reporte Allure (con histórico de tendencias).
5. Lo publica en la rama `gh-pages` → GitHub Pages.

Requiere tener cargados los **Secrets**: `AMV_USER`, `AMV_PASS`, `BO_USER`,
`BO_PASS`, `AMV_AGENCIA_USER`.

## Pendientes recomendados

- **Rotar la contraseña** que estaba hardcodeada en `web.py` (ya se quitó del código,
  ahora se lee de `AMV_USER`/`AMV_PASS`, pero conviene rotarla y limpiar el historial de git).
- Reemplazar localizadores frágiles (IDs posicionales de datos puntuales, XPaths absolutos).
- Sembrar datos de prueba en preprod (p. ej. facturas pendientes del proveedor en Crear OP).

#!/usr/bin/env bash
# Aplica el branding de AMV Travel al reporte Allure ya generado.
# Uso: scripts/aplicar_branding.sh <directorio_del_reporte>
set -e

REPORT_DIR="${1:-allure-report}"
echo "Aplicando branding en: $REPORT_DIR"

# 1. Favicon (ícono de la pestaña)
if [ -f branding/favicon.ico ]; then
  cp branding/favicon.ico "$REPORT_DIR/favicon.ico"
  echo "  - Favicon reemplazado."
fi

# 2. Logo: reemplazamos el logo de Allure por el de AMV.
#    Estrategia: ocultar TODO el contenido interno del contenedor del logo
#    (texto 'Allure' + svg/img) y poner el logo de AMV como fondo del contenedor.
if [ -f branding/logo.png ]; then
  LOGO_B64=$(base64 -w 0 branding/logo.png)
  CSS_FILE=$(find "$REPORT_DIR" -maxdepth 1 -name "styles.css" | head -1)
  [ -z "$CSS_FILE" ] && CSS_FILE="$REPORT_DIR/styles.css"
  {
    echo ""
    echo "/* ===== Branding AMV Travel ===== */"
    # Contenedor del logo: ponemos el logo de AMV como fondo
    echo ".side-nav__brand, [class*='logo'] {"
    echo "  background-image: url(\"data:image/png;base64,${LOGO_B64}\") !important;"
    echo "  background-size: contain !important;"
    echo "  background-repeat: no-repeat !important;"
    echo "  background-position: left center !important;"
    echo "  position: relative !important;"
    echo "}"
    # Ocultamos TODO lo que está adentro (el texto 'Allure' y el svg/img originales)
    echo ".side-nav__brand *, [class*='logo'] > * {"
    echo "  visibility: hidden !important;"
    echo "  opacity: 0 !important;"
    echo "}"
  } >> "$CSS_FILE"
  echo "  - Logo inyectado en: $CSS_FILE"
fi

# 3. Título de la pestaña del navegador
if [ -f "$REPORT_DIR/index.html" ]; then
  sed -i 's#<title>[^<]*</title>#<title>AMV Travel — Regresión Preprod</title>#' "$REPORT_DIR/index.html"
  echo "  - Título reemplazado."
fi

echo "Branding aplicado."

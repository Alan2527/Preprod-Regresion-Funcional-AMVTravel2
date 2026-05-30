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

# 2. Logo: inyectamos una regla CSS al final del styles.css del reporte.
if [ -f branding/logo.png ]; then
  LOGO_B64=$(base64 -w 0 branding/logo.png)
  CSS_FILE=$(find "$REPORT_DIR" -maxdepth 1 -name "styles.css" | head -1)
  [ -z "$CSS_FILE" ] && CSS_FILE="$REPORT_DIR/styles.css"
  {
    echo ""
    echo "/* ===== Branding AMV Travel ===== */"
    echo ".side-nav__brand, a[class*='logo'], [class*='logo__'], .logo {"
    echo "  background-image: url(\"data:image/png;base64,${LOGO_B64}\") !important;"
    echo "  background-size: contain !important;"
    echo "  background-repeat: no-repeat !important;"
    echo "  background-position: left center !important;"
    echo "}"
    echo "[class*='logo__'] svg, .logo svg, .side-nav__brand svg { display: none !important; }"
  } >> "$CSS_FILE"
  echo "  - Logo inyectado en: $CSS_FILE"
fi

# 3. Título de la pestaña del navegador
if [ -f "$REPORT_DIR/index.html" ]; then
  sed -i 's#<title>[^<]*</title>#<title>AMV Travel — Regresión Preprod</title>#' "$REPORT_DIR/index.html"
  echo "  - Título reemplazado."
fi

echo "Branding aplicado."

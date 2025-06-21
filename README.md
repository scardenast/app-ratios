# Aplicación de Análisis Financiero

Esta aplicación permite subir un archivo CSV o Excel con información contable y calcula diversos indicadores financieros. Los resultados se muestran en un dashboard con semáforo y se pueden exportar a PDF.

## Uso

1. Instale las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecute la aplicación:
   ```bash
   python app.py
   ```
3. Abra su navegador en `http://localhost:5000` y cargue su archivo.

El archivo debe contener columnas con los siguientes encabezados (en español):
`Activo Corriente`, `Pasivo Corriente`, `Inventarios`, `Pasivo Total`, `Activo Total`, `Patrimonio Neto`, `Utilidad Neta`, `Ventas Totales`, `Costo de Ventas`, `Inventarios Promedio`, `Ventas a Crédito`, `Cuentas por Cobrar Promedio`, `Utilidad Operativa`, `Capitalizacion de Mercado`, `Deuda Neta`, `Efectivo`, `Cuentas por Cobrar`, `Ventas Diarias Promedio`, `Cuentas por Pagar`, `Compras Diarias Promedio`.

## PDF

Para generar el PDF se utiliza `pdfkit`, que requiere tener instalado `wkhtmltopdf` en el sistema.

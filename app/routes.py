import io
import pandas as pd
from flask import render_template, request, redirect, url_for, send_file
from . import app

# Thresholds for traffic light indicator
THRESHOLDS = {
    'razon_corriente': [1, 2],  # <1 rojo, 1-2 amarillo, >2 verde
    'prueba_acida': [0.8, 1],
    'razon_endeudamiento': [0.5, 0.8],
    'roe': [0.1, 0.2],
    'roa': [0.05, 0.1],
}

RECOMMENDATIONS = {
    'razon_corriente': {
        'low': 'Riesgo de iliquidez. Considere reducir pasivos o aumentar caja.',
        'high': 'Capital de trabajo ocioso. Considere invertir excedentes.'
    },
    'prueba_acida': {
        'low': 'Inventarios altos pueden ocultar problemas de liquidez.',
        'high': 'Buena cobertura de corto plazo.'
    },
}


def get_color(value, thresholds):
    low, high = thresholds
    if value < low:
        return 'red'
    if low <= value <= high:
        return 'yellow'
    return 'green'


def compute_ratios(df):
    ratios = {}
    try:
        ratios['razon_corriente'] = df['Activo Corriente'].iloc[0] / df['Pasivo Corriente'].iloc[0]
    except Exception:
        ratios['razon_corriente'] = None
    try:
        ratios['prueba_acida'] = (
            df['Activo Corriente'].iloc[0] - df['Inventarios'].iloc[0]
        ) / df['Pasivo Corriente'].iloc[0]
    except Exception:
        ratios['prueba_acida'] = None
    try:
        ratios['capital_trabajo'] = df['Activo Corriente'].iloc[0] - df['Pasivo Corriente'].iloc[0]
    except Exception:
        ratios['capital_trabajo'] = None
    try:
        ratios['razon_endeudamiento'] = df['Pasivo Total'].iloc[0] / df['Activo Total'].iloc[0]
    except Exception:
        ratios['razon_endeudamiento'] = None
    try:
        ratios['razon_deuda_patrimonio'] = df['Pasivo Total'].iloc[0] / df['Patrimonio Neto'].iloc[0]
    except Exception:
        ratios['razon_deuda_patrimonio'] = None
    try:
        ratios['roe'] = (df['Utilidad Neta'].iloc[0] / df['Patrimonio Neto'].iloc[0]) * 100
    except Exception:
        ratios['roe'] = None
    try:
        ratios['roa'] = (df['Utilidad Neta'].iloc[0] / df['Activo Total'].iloc[0]) * 100
    except Exception:
        ratios['roa'] = None
    try:
        ratios['margen_utilidad_neta'] = (df['Utilidad Neta'].iloc[0] / df['Ventas Totales'].iloc[0]) * 100
    except Exception:
        ratios['margen_utilidad_neta'] = None
    try:
        ratios['rotacion_activos'] = df['Ventas Totales'].iloc[0] / df['Activo Total'].iloc[0]
    except Exception:
        ratios['rotacion_activos'] = None
    try:
        ratios['rotacion_inventarios'] = df['Costo de Ventas'].iloc[0] / df['Inventarios Promedio'].iloc[0]
    except Exception:
        ratios['rotacion_inventarios'] = None
    try:
        ratios['rotacion_cxc'] = df['Ventas a Crédito'].iloc[0] / df['Cuentas por Cobrar Promedio'].iloc[0]
    except Exception:
        ratios['rotacion_cxc'] = None
    try:
        ratios['margen_operativo'] = (df['Utilidad Operativa'].iloc[0] / df['Ventas Totales'].iloc[0]) * 100
    except Exception:
        ratios['margen_operativo'] = None
    try:
        ratios['valor_empresa'] = (
            df['Capitalizacion de Mercado'].iloc[0]
            + df['Deuda Neta'].iloc[0]
            - df['Efectivo'].iloc[0]
        )
    except Exception:
        ratios['valor_empresa'] = None
    try:
        ratios['dias_cxc'] = df['Cuentas por Cobrar'].iloc[0] / df['Ventas Diarias Promedio'].iloc[0]
    except Exception:
        ratios['dias_cxc'] = None
    try:
        ratios['dias_cxp'] = df['Cuentas por Pagar'].iloc[0] / df['Compras Diarias Promedio'].iloc[0]
    except Exception:
        ratios['dias_cxp'] = None
    return ratios


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return redirect(url_for('index'))
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        ratios = compute_ratios(df)
        colors = {
            key: get_color(val, THRESHOLDS.get(key, [0, 0])) if val is not None else 'grey'
            for key, val in ratios.items()
        }
        recs = {}
        for key, val in ratios.items():
            thresh = THRESHOLDS.get(key)
            if val is None or thresh is None:
                continue
            low, high = thresh
            if val < low:
                recs[key] = RECOMMENDATIONS.get(key, {}).get('low')
            elif val > high:
                recs[key] = RECOMMENDATIONS.get(key, {}).get('high')
        return render_template('dashboard.html', ratios=ratios, colors=colors, recs=recs)
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download_pdf():
    from flask import render_template_string
    import pdfkit

    data = request.form.to_dict(flat=False)
    ratios = {k: float(v[0]) if v else None for k, v in data.items() if k.startswith('ratio_')}
    html = render_template('pdf.html', ratios=ratios)
    pdf = pdfkit.from_string(html, False)
    return send_file(
        io.BytesIO(pdf),
        as_attachment=True,
        download_name='resumen.pdf',
        mimetype='application/pdf'
    )

import os, json, base64, tempfile, subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PAIRS = {
    "EURUSD": {"name":"EUR/USD","pipDecimals":5,"support":1.12450,"resistance":1.12720,"pivot":1.12585,"entry":1.12595,"sl":1.12665,"tp1":1.12490,"tp2":1.12380,"rb":3.1,"riskPct":1.35},
    "USDJPY": {"name":"USD/JPY","pipDecimals":3,"support":151.850,"resistance":152.780,"pivot":152.315,"entry":152.380,"sl":152.050,"tp1":153.050,"tp2":153.500,"rb":3.2,"riskPct":1.10},
    "GBPUSD": {"name":"GBP/USD","pipDecimals":5,"support":1.27050,"resistance":1.27850,"pivot":1.27450,"entry":1.27460,"sl":1.27200,"tp1":1.27800,"tp2":1.28050,"rb":3.4,"riskPct":1.00}
}

PROMPT = """Eres un asesor profesional de trading. Analiza esta captura de un gráfico de {pair} en timeframe 4H. Tu estrategia: operar a favor de tendencia 4H con confirmación de pin bar en M15, R:B mínimo 3:1, sin noticias de alto impacto. Responde SOLO en JSON válido:
{{"tendencia_4h":"Alcista|Bajista|Lateral","estructura":"descripcion","precio_actual":"precio","soporte_cercano":"nivel","resistencia_cercana":"nivel","patron_vela":"Pin bar alcista|Pin bar bajista|Doji|Sin patron claro|Otro","patron_confirmado":"Si|No|No aplica","rsi_aproximado":"valor o No visible","mecha_dominante":"Superior larga|Inferior larga|Sin mecha|Ambas cortas","alineacion_estrategia":"Si|No|Parcial","veredicto":"OPERAR|ESPERAR|NO OPERAR","direccion":"COMPRA|VENTA|Ninguna","score":"0-100","razones_favor":["razon"],"advertencias":["advertencia"],"recomendacion":"texto detallado"}}"""

@app.route('/api/analyze-chart', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error":"Falta imagen"}), 400
        pair_key = data.get('pair','EURUSD')
        if pair_key not in PAIRS:
            return jsonify({"error":"Par no soportado"}), 400
        pair = PAIRS[pair_key]
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',',1)[1]
        image_bytes = base64.b64decode(image_data)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name
        try:
            prompt = PROMPT.format(pair=pair['name'])
            result = subprocess.run(['z-ai','vision','-p',prompt,'-i',tmp_path,'-o','/tmp/out.json'],
                capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                return jsonify({"error":f"Error z-ai: {result.stderr[:500]}"}), 500
            with open('/tmp/out.json') as f:
                resp = json.load(f)
            content = resp.get('choices',[{}])[0].get('message',{}).get('content','')
            content = content.strip()
            if content.startswith('```json'): content = content[7:]
            if content.startswith('```'): content = content[3:]
            if content.endswith('```'): content = content[:-3]
            try:
                analysis = json.loads(content.strip())
                analysis['pair'] = pair_key
                analysis['pair_name'] = pair['name']
                analysis['pair_config'] = {k:pair[k] for k in ['support','resistance','pivot','entry','sl','tp1','tp2','rb','riskPct','pipDecimals']}
                return jsonify(analysis)
            except:
                return jsonify({"error":"JSON invalido","raw_response":content[:1500]})
        finally:
            try: os.unlink(tmp_path)
            except: pass
    except Exception as e:
        return jsonify({"error":str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status":"ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=port)
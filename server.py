import os, json, base64, requests, time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PAIRS = {
    "EURUSD": {"name":"EUR/USD","pipDecimals":5,"support":1.12450,"resistance":1.12720,"pivot":1.12585,"entry":1.12595,"sl":1.12665,"tp1":1.12490,"tp2":1.12380,"rb":3.1,"riskPct":1.35},
    "USDJPY": {"name":"USD/JPY","pipDecimals":3,"support":151.850,"resistance":152.780,"pivot":152.315,"entry":152.380,"sl":152.050,"tp1":153.050,"tp2":153.500,"rb":3.2,"riskPct":1.10},
    "GBPUSD": {"name":"GBP/USD","pipDecimals":5,"support":1.27050,"resistance":1.27850,"pivot":1.27450,"entry":1.27460,"sl":1.27200,"tp1":1.27800,"tp2":1.28050,"rb":3.4,"riskPct":1.00}
}

PROMPT = """Eres un asesor profesional de trading. Analiza esta captura de un grafico de {pair} en timeframe 4H. Tu estrategia: operar a favor de tendencia 4H con confirmacion de pin bar en M15, R:B minimo 3:1, sin noticias de alto impacto. Responde SOLO en JSON valido:
{{"tendencia_4h":"Alcista|Bajista|Lateral","estructura":"descripcion","precio_actual":"precio","soporte_cercano":"nivel","resistencia_cercana":"nivel","patron_vela":"Pin bar alcista|Pin bar bajista|Doji|Sin patron claro|Otro","patron_confirmado":"Si|No|No aplica","rsi_aproximado":"valor o No visible","mecha_dominante":"Superior larga|Inferior larga|Sin mecha|Ambas cortas","alineacion_estrategia":"Si|No|Parcial","veredicto":"OPERAR|ESPERAR|NO OPERAR","direccion":"COMPRA|VENTA|Ninguna","score":"0-100","razones_favor":["razon"],"advertencias":["advertencia"],"recomendacion":"texto detallado"}}"""

def call_zai_api(api_key, prompt_text, image_data, max_retries=4):
    """Llama a Z.ai con reintentos automáticos si el servicio está saturado."""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                'https://api.z.ai/api/paas/v4/chat/completions',
                headers={
                    'Authorization': 'Bearer ' + api_key,
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'glm-4.6v-flash',
                    'messages': [{
                        'role': 'user',
                        'content': [
                            {'type': 'text', 'text': prompt_text},
                            {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + image_data}}
                        ]
                    }]
                },
                timeout=120
            )
        import os, json, base64, requests, time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Función para obtener precios reales automáticamente
def get_real_prices():
    try:
        resp = requests.get('https://open.er-api.com/v6/latest/USD', timeout=10)
        data = resp.json()
        if data and data.get('rates'):
            eur = data['rates']['EUR']
            jpy = data['rates']['JPY']
            gbp = data['rates']['GBP']
            return {
                'EURUSD': {'price': 1/eur, 'pipDecimals': 5, 'pipSize': 0.0001},
                'USDJPY': {'price': jpy, 'pipDecimals': 3, 'pipSize': 0.01},
                'GBPUSD': {'price': 1/gbp, 'pipDecimals': 5, 'pipSize': 0.0001}
            }
    except:
        pass
    # Precios de respaldo si la API falla
    return {
        'EURUSD': {'price': 1.11866, 'pipDecimals': 5, 'pipSize': 0.0001},
        'USDJPY': {'price': 158.555, 'pipDecimals': 3, 'pipSize': 0.01},
        'GBPUSD': {'price': 1.33661, 'pipDecimals': 5, 'pipSize': 0.0001}
    }

PAIRS = {
    "EURUSD": {"name":"EUR/USD","pipDecimals":5,"pipSize":0.0001},
    "USDJPY": {"name":"USD/JPY","pipDecimals":3,"pipSize":0.01},
    "GBPUSD": {"name":"GBP/USD","pipDecimals":5,"pipSize":0.0001}
}

PROMPT = """Eres un asesor profesional de trading. Analiza esta captura de un grafico de {pair} en timeframe 4H. Tu estrategia: operar a favor de tendencia 4H con confirmacion de pin bar en M15, R:B minimo 3:1, sin noticias de alto impacto. Responde SOLO en JSON valido:
{{"tendencia_4h":"Alcista|Bajista|Lateral","estructura":"descripcion","precio_actual":"precio","soporte_cercano":"nivel","resistencia_cercana":"nivel","patron_vela":"Pin bar alcista|Pin bar bajista|Doji|Sin patron claro|Otro","patron_confirmado":"Si|No|No aplica","rsi_aproximado":"valor o No visible","mecha_dominante":"Superior larga|Inferior larga|Sin mecha|Ambas cortas","alineacion_estrategia":"Si|No|Parcial","veredicto":"OPERAR|ESPERAR|NO OPERAR","direccion":"COMPRA|VENTA|Ninguna","score":"0-100","razones_favor":["razon"],"advertencias":["advertencia"],"recomendacion":"texto detallado"}}"""

def call_zai_api(api_key, prompt_text, image_data, max_retries=4):
    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.post(
                'https://api.z.ai/api/paas/v4/chat/completions',
                headers={
                    'Authorization': 'Bearer ' + api_key,
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'glm-4.6v-flash',
                    'messages': [{
                        'role': 'user',
                        'content': [
                            {'type': 'text', 'text': prompt_text},
                            {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + image_data}}
                        ]
                    }]
                },
                timeout=120
            )
            if response.status_code == 200:
                return response.json(), None
            if response.status_code == 429 or '1305' in response.text or 'overloaded' in response.text.lower():
                last_error = "Z.ai saturado (intento " + str(attempt + 1) + "/" + str(max_retries) + ")"
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
            return None, "Error Z.ai: " + response.text[:500]
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
    return None, last_error or "Z.ai saturado despues de varios intentos."

@app.route('/api/analyze-chart', methods=['POST'])
def analyze():
    try:
 import os, json, base64, requests, time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_real_prices():
    try:
        resp = requests.get('https://open.er-api.com/v6/latest/USD', timeout=10)
        data = resp.json()
        if data and data.get('rates'):
            eur = data['rates']['EUR']
            jpy = data['rates']['JPY']
            gbp = data['rates']['GBP']
            return {
                'EURUSD': {'price': 1/eur, 'pipDecimals': 5, 'pipSize': 0.0001},
                'USDJPY': {'price': jpy, 'pipDecimals': 3, 'pipSize': 0.01},
                'GBPUSD': {'price': 1/gbp, 'pipDecimals': 5, 'pipSize': 0.0001}
            }
    except:
        pass
    return {
        'EURUSD': {'price': 1.11866, 'pipDecimals': 5, 'pipSize': 0.0001},
        'USDJPY': {'price': 158.555, 'pipDecimals': 3, 'pipSize': 0.01},
        'GBPUSD': {'price': 1.33661, 'pipDecimals': 5, 'pipSize': 0.0001}
    }

PAIRS = {
    "EURUSD": {"name":"EUR/USD","pipDecimals":5,"pipSize":0.0001},
    "USDJPY": {"name":"USD/JPY","pipDecimals":3,"pipSize":0.01},
    "GBPUSD": {"name":"GBP/USD","pipDecimals":5,"pipSize":0.0001}
}

PROMPT = """Eres un asesor profesional de trading. Analiza esta captura de un grafico de {pair} en timeframe 4H. Tu estrategia: operar a favor de tendencia 4H con confirmacion de pin bar en M15, R:B minimo 3:1, sin noticias de alto impacto. Responde SOLO en JSON valido:
{{"tendencia_4h":"Alcista|Bajista|Lateral","estructura":"descripcion","precio_actual":"precio","soporte_cercano":"nivel","resistencia_cercana":"nivel","patron_vela":"Pin bar alcista|Pin bar bajista|Doji|Sin patron claro|Otro","patron_confirmado":"Si|No|No aplica","rsi_aproximado":"valor o No visible","mecha_dominante":"Superior larga|Inferior larga|Sin mecha|Ambas cortas","alineacion_estrategia":"Si|No|Parcial","veredicto":"OPERAR|ESPERAR|NO OPERAR","direccion":"COMPRA|VENTA|Ninguna","score":"0-100","razones_favor":["razon"],"advertencias":["advertencia"],"recomendacion":"texto detallado"}}"""

def call_zai_api(api_key, prompt_text, image_data, max_retries=4):
    last_error = None
    for attempt in range(max_retries):
        try:
            response = requests.post(
                'https://api.z.ai/api/paas/v4/chat/completions',
                headers={
                    'Authorization': 'Bearer ' + api_key,
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'glm-4.6v-flash',
                    'messages': [{
                        'role': 'user',
                        'content': [
                            {'type': 'text', 'text': prompt_text},
                            {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + image_data}}
                        ]
                    }]
                },
                timeout=120
            )
            if response.status_code == 200:
                return response.json(), None
            if response.status_code == 429 or '1305' in response.text or 'overloaded' in response.text.lower():
                last_error = "Z.ai saturado (intento " + str(attempt + 1) + "/" + str(max_retries) + ")"
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
            return None, "Error Z.ai: " + response.text[:500]
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
    return None, last_error or "Z.ai saturado despues de varios intentos."

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
        
        real_prices = get_real_prices()
        real_price = real_prices[pair_key]['price']
        pip_size = pair['pipSize']
        pip_dec = pair['pipDecimals']
        
        if pair_key == 'USDJPY':
            support = real_price - 0.50
            resistance = real_price + 0.50
        else:
            support = real_price - pip_size * 50
            resistance = real_price + pip_size * 50
        pivot = real_price
        
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',',1)[1]
        
        api_key = os.environ.get('ZAI_API_KEY','')
        if not api_key:
            return jsonify({"error":"ZAI_API_KEY no configurada"}), 500
        
        prompt_text = PROMPT.format(pair=pair['name']) + "\n\nDATOS REALES ACTUALES:\n"
        prompt_text += "- Precio actual: " + str(round(real_price, pip_dec)) + "\n"
        prompt_text += "- Soporte cercano: " + str(round(support, pip_dec)) + "\n"
        prompt_text += "- Resistencia cercana: " + str(round(resistance, pip_dec)) + "\n"
        prompt_text += "- Pivote diario: " + str(round(pivot, pip_dec))
        
        resp_json, error = call_zai_api(api_key, prompt_text, image_data)
        
        if error:
            return jsonify({"error":error}), 500
        
        content = resp_json.get('choices',[{}])[0].get('message',{}).get('content','')
        content = content.strip()
        if content.startswith('```json'): content = content[7:]
        if content.startswith('```'): content = content[3:]
        if content.endswith('```'): content = content[:-3]
        
        try:
            analysis = json.loads(content.strip())
            analysis['pair'] = pair_key
            analysis['pair_name'] = pair['name']
            analysis['real_price'] = real_price
            analysis['pair_config'] = {
                'support': support,
                'resistance': resistance,
                'pivot': pivot,
                'entry': real_price,
                'sl': real_price - (0.70 if pair_key == 'USDJPY' else pip_size * 70),
                'tp1': real_price + (1.80 if pair_key == 'USDJPY' else pip_size * 180),
                'tp2': real_price + (2.80 if pair_key == 'USDJPY' else pip_size * 280),
                'rb': 3.0,
                'riskPct': 1.0,
                'pipDecimals': pip_dec
            }
            return jsonify(analysis)
        except:
            return jsonify({"error":"JSON invalido","raw_response":content[:1500]})
            
    except Exception as e:
        return jsonify({"error":str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status":"ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3001))
    app.run(host='0.0.0.0', port=port)
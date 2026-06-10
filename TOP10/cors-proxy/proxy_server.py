from flask import Flask, Response
import requests

app = Flask(__name__)

TARGET_URL = "http://hpte.simplo.com.cn/index.php?r=hpte-api/get-dispatch-orders"

@app.route('/api/orders')
def proxy():
    resp = requests.get(TARGET_URL, timeout=15)
    # 强制设置响应头为 JSON 并指定 UTF-8 编码
    return Response(
        resp.text,
        status=resp.status_code,
        mimetype='application/json; charset=utf-8'
    )

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
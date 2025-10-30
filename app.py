from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>¡Hola desde Flask y Jenkins!</h1><p>Esta es una app real desplegada con Docker.</p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

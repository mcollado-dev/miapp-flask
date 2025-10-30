from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/estadisticas')
def estadisticas():
    return render_template('estadisticas.html')

@app.route('/funciones')
def funciones():
    return render_template('funciones.html')

@app.route('/documentacion')
def documentacion():
    return render_template('documentacion.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)




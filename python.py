''' ДЗ 16
Взять готовые страницы из задания 13 и бэкенд для них (работа с api).
Так же по желанию можно взять другой проект с парсером и сделать
страницы для него. Можно доделать оба проекта для тренировки
Сделать сайт на Flask в котором будет главная страница, страница
с контактами, страница с формой, еще будет страница с результатами
'''
import json

from flask import Flask, render_template, request
from main import parser_hh

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/contacts/")
def contacts():
    developer_name = 'Александр Попов'
    return render_template('contacts.html', name=developer_name, creation_data = '08.08.2023')

@app.route('/results/')
def results():
    with open('add.json', 'r') as f:
        text = json.load(f)
    with open('add_2.json', 'r') as f:
        text_2 = json.load(f)
    return render_template('results.html', text=text, text_2=text_2)

@app.route("/run/", methods=['GET'])
def run_get():
    # with open('main.txt', 'r') as f:
    #     text = f.read()
    return render_template('form.html') #, text=text)

@app.route("/run/", methods=['POST'])
def run_post():
    text = request.form['input_text']
    parser_hh(text)
    # with open('main.txt', 'a') as f:
    #     f.write(f'{text}\n')
    return render_template('good.html', text=text)

if __name__ == "__main__":
    app.run(debug=True)
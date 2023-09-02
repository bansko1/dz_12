''' ДЗ 18
Взять готовые страницы из задания 13 и бэкенд для них (работа с api).
По структуре моделей создать базу данных (база данных sqlite)
Написать скрипты для заполнения базы данных данными и выборки данных из базы
(Все делаем через ORM), возможны 2 вариант: 1) более простой - использовать
просто какие то тестовые данные, сохранить их в базу и после этого сделать выборку
этих данных и вывести в терминал. 2) более сложный - использовать реальные данные,
которые получил парсер, вместо json - а теперь сохранить эти данные в созданную базу,
сделать выборку данных либо в консольном варианте программы, либо вывести на сайт (идеальный вариант)
'''
import json

from flask import Flask, render_template, request
from main_orm import parser_hh, Key_skill

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/contacts/")
def contacts():
    developer_name = 'Александр Попов'
    return render_template('contacts.html', name=developer_name, creation_data='08.08.2023')


@app.route('/results/')
def results():
    with open('add.json', 'r') as f:
        text = json.load(f)
    with open('add_2.json', 'r') as f:
        text_2 = json.load(f)

    engine = create_engine('sqlite:///hh_orm.sqlite', echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    result = session.query(Key_skill).all()
    #    for res in result:
    list_0 = [result[0].id, result[0].name, result[0].count, result[0].percent]
    list_1 = [result[1].id, result[1].name, result[1].count, result[1].percent]
    list_2 = [result[2].id, result[2].name, result[2].count, result[2].percent]
    list_3 = [result[3].id, result[3].name, result[3].count, result[3].percent]
    res = [list_0, list_1, list_2, list_3]
    # print(list_result)
    return render_template('results.html', text=text, text_2=text_2, text_3=res)


@app.route("/run/", methods=['GET'])
def run_get():
    # with open('main.txt', 'r') as f:
    #     text = f.read()
    return render_template('form.html')


@app.route("/run/", methods=['POST'])
def run_post():
    text = request.form['input_text']
    parser_hh(text)
    # with open('main.txt', 'a') as f:
    #     f.write(f'{text}\n')
    return render_template('good.html', text=text)


if __name__ == "__main__":
    app.run(debug=True)

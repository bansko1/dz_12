import requests
import pprint
from statistics import mean
import re
from collections import Counter
import json
import time

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///hh_orm.sqlite', echo=False)
Base = declarative_base()


class Key_skill(Base):
    __tablename__ = 'key_skill'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    count = Column(Integer, nullable=True)
    percent = Column(String, nullable=True)

    def __init__(self, name, count, percent):
        self.name = name
        self.count = count
        self.percent = percent

    def __str__(self):
        # return ['{self.id}', '{self.name}', '{self.count}', '{self.percent}']
        return f'{self.id} {self.name} {self.count} {self.percent}'


# Создание таблицы
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def parser_hh(text_vacancies):
    session.query(Key_skill).delete()
    session.commit()

    url_vacancies = 'https://api.hh.ru/vacancies'
    params = {
        'text': text_vacancies,
        'per_page': 20,
        'area': 113  # 113 - Россия
    }
    result = requests.get(url_vacancies, params=params).json()
    found = result['found']
    pages = result['pages']
    per_page = result['per_page']
    # print('*****************************************')
    # print('Отбор вакансий по запросу: ', text_vacancies)
    # print('Всего найдено вакансий: ', found)
    # print(f'Всего страниц: {pages}, Вакансий на странице: {per_page}')

    add = []
    skills_list = []
    skl = set()
    count = 0
    salary_list = []
    # sk = []

    # Перебор страниц
    for i in range(pages): # обрабатываем 2 из pages страниц
        # for i in range(p):
        params = {
            'text': text_vacancies,
            'page': i,
            'per_page': per_page,
            'area': 113
        }

        result = requests.get(url_vacancies, params=params).json()
        # print(i, result)
        items = result['items']
        # print('Обрабатывается страница: ', i)
        # Перебор записей на странице
        for j in range(per_page):
            time.sleep(0.5)
            if count >= found:
                break
            count = count + 1
            # print(count)
            try:
                salary = items[j]['salary']
                # print('salary:', salary)
            except IndexError:
                break
            if salary and salary['currency'] == 'RUR':
                if salary['to']:
                    if not salary['from']:
                        salary_average = salary['to']
                # if salary['from'] and salary['to'] and salary['currency'] == 'RUR':
                    else:
                        salary_average = (salary['from'] + salary['to']) / 2

                else:
                    if salary['from']:
                        salary_average = salary['from']
                    else:
                        break
                # print(salary['from'], salary['to'], salary_average)
                salary_list.append(salary_average)
            # print(salary_list)

            item_one_vacancy = items[j]
            # print(first['alternate_url'])
            one_vacancy_url = item_one_vacancy['url']
            result_one_vac = requests.get(one_vacancy_url).json()
            # pprint.pprint(result)
            # time.sleep(0.01)
            # обработка описания вакансии
            # извлечение из описания терминов на латинице, запись в множество и очистка
            # от пробелов и дефисов, приведение к нижнему регистру заглавных букв
            try:
                pp = result_one_vac['description']
            # time.sleep(0.01)
            # print(j, pp)
            except KeyError:
                # print('Страница: ', i, 'Строка: ', j)
                break
            # print(pp)
            pp_re = re.findall(r'\s[A-Za-z-?]+', pp)
            # print('Список из description')
            # print(pp_re)
            its = set(x.strip(' -').lower() for x in pp_re)
            # print('Приведенное множество из description')
            # print(its)
            # if result_one_vac['key_skills']:
            try:
                for sk in result_one_vac['key_skills']:
                    skills_list.append(sk['name'].lower())
            except KeyError:
                break
            try:
                skl.add(sk['name'].lower())
            except UnboundLocalError:
                break
            # print('Список из key_skills: ', skills_list)
            # print(skl)
            for it in its:
                if not any(it in x for x in skl):
                    skills_list.append(it)
            # print('Требования дополненные: ', skills_list)
    skill_couner = Counter(skills_list)
    count_sum = 0
    # print(skill_couner.most_common(7))

    for name, count in skill_couner.most_common(5):
        count_sum = count_sum + count

    for name, count in skill_couner.most_common(5):
        prc = count / count_sum * 100
        add.append({'name': name,
                    'count': count,
                    'percent': round(prc, 1)
                    })

        key_skill = Key_skill(name, count, percent=round(prc, 1))
        # Добавление данных
        session.add(key_skill)
        session.commit()

    mean_sal = round(mean(salary_list), 0)
    # if len(skills_list):
    #     print('Средняя зарплата: ', round(mean_sal), 'рублей')
    # else:
    #     print('В вакансии нет указания на зарплату')

    # сохранение файл с результами работы
    #
    # add.append({'Средняя зарплата': mean_sal})
    add_2 = {'req': text_vacancies, 'quantity': found, 'mean_sal': mean_sal}
    # add.append({'Найдено вакансий': found})
    # add.append({'Поисковый запрос': text_vacancies})

    with open('add.json', mode='w') as f:
        json.dump(add, f)
    with open('add_2.json', mode='w') as f:
        json.dump(add_2, f)

    return add, add_2


if __name__ == "__main__":
    text_vacancies = 'junior AND (js) AND (Москва)'
    add, add_2 = parser_hh(text_vacancies)
    # print(found, mean_sal)
    pprint.pprint(add)
    pprint.pprint(add_2)

    # Запрос из таблицы
    results = session.query(Key_skill).all()
    # print(results)
    for result in results:
        # print(result)
        list_result = [result.id, result.name, result.count, result.percent]
        print(list_result)

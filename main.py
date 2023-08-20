import requests
import pprint
from statistics import mean
import re
from collections import Counter
import json
import time
import sqlite3





#cursor.execute('delete from key_skills')
def parser_hh(text_vacancies):
    # Соединение с базой данных
    con = sqlite3.connect("hh.sqlite", check_same_thread=False)
    # Создаем курсор
    cursor = con.cursor()


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
    for i in range(pages):
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
            count = count + 1
            if count >= found:
                break
            salary = items[j]['salary']
            if salary:
                if salary['from'] and salary['to'] and salary['currency'] == 'RUR':
                    salary_average = (salary['from'] + salary['to']) / 2
                    # print(salary_average)
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
                print('Страница: ', i, 'Строка: ', j)
                break
            # print(pp)
            pp_re = re.findall(r'\s[A-Za-z-?]+', pp)
            # print('Список из description')
            # print(pp_re)
            its = set(x.strip(' -').lower() for x in pp_re)
            # print('Приведенное множество из description')
            # print(its)
            #if result_one_vac['key_skills']:
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
    cursor.execute('delete from key_skills')
    for name, count in skill_couner.most_common(5):
        count_sum = count_sum + count

    for name, count in skill_couner.most_common(5):
        prc = count / count_sum * 100
        add.append({'name': name,
                    'count': count,
                    'percent': round(prc, 1)
                    })
        cursor.execute('insert into key_skills (name_ks, count_ks, percent_ks) values(?, ?, ?)', (name, count, round(prc, 1)))

    # cursor.execute('select * from key_skills')
    # result = cursor.fetchall()
    con.commit()
    con.close()
    # print('Самые распространенные требования по этим вакансиям:')
    # pprint.pprint(add)

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

    # Соединение с базой данных
    con = sqlite3.connect("hh.sqlite", check_same_thread=False)
    # Создаем курсор
    cursor = con.cursor()
    cursor.execute('select * from key_skills')
    result = cursor.fetchall()
    print(result)
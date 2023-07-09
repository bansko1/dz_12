import requests
import pprint
from statistics import mean
import re
from collections import Counter
import json

text_vacancies = 'junior AND (Python) AND (Москва)'
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
print('*****************************************')
print('Отбор вакансий по запросу: ', text_vacancies)
print('Всего найдено вакансий: ', found)
print(f'Всего страниц: {pages}, Вакансий на странице: {per_page}')

add = []
skills_list = []
skl = set()
count = 0
salary_list = []

# Перебор страниц
if pages < 6:
    p = pages
else:
    p = 6
# for i in range(pages):
for i in range(p):
    params = {
        'text': text_vacancies,
        'page': i,
        'per_page': per_page,
        'area': 113
    }

    result = requests.get(url_vacancies, params=params).json()
    # print(i, result)
    items = result['items']
    print('Обрабатывается страница: ', i)
    # Перебор записей на странице
    for j in range(per_page):
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
        for sk in result_one_vac['key_skills']:
            skills_list.append(sk['name'].lower())
        skl.add(sk['name'].lower())
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
    add.append({'name': name,
                'count': count,
                'percent': round(count / count_sum * 100, 1)
                })
print('Самые распространенные требования по этим вакансиям:')
pprint.pprint(add)

mean_sal = mean(salary_list)
if len(skills_list):
    print('Средняя зарплата: ', round(mean_sal), 'рублей')
else:
    print('В вакансии нет указания на зарплату')

# сохранение файл с результами работы
#
add.append({'Средняя зарплата': mean_sal})
with open('add.json', mode='w') as f:
    json.dump(add, f)

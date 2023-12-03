# dz 18. Описание работы системы.
Система предназначена для поиска наиболее актуальных навыков необходимых 
соискателю для занятия определенной вакансии (должности) в определенном городе РФ.
По запросу на языке запросов hh.ru система получает данные о вакансиях с hh.ru
и выводит на странице сайта: 
1. поисковый запрос,   
2. количество найденных вакансий, 
3. среднюю зарплату по найденным вакансиям,
4. 5 наиболее популярных навыков в найденных вакансиях,  
5. сколько раз каждый навык встречается в найденных вакансиях,
6. сколько процентов это составляет от общего числа найденных вакансий.
Система реализована на flask с использованием ORM sqlalchemy.
Для запуска системы необходимо выполнить код файла python.py или python_orm.py.

# pantheon-statistics

Библиотека для сбора и обработки статистики игр по риичи-маджонгу, проведённых в системе [Pantheon](https://mjtop.net/). С использованием данной библиотеки проведён [анализ](https://furiten.ru/index.php/category/статистика/) нескольких турниров.

## Установка

```
git clone https://github.com/alex-karpov/pantheon-statistics.git
cd pantheon_statistics
python -m pip install pipenv jupyter
pipenv install --dev
```

Установка ядра jupyter в виртуальном окружении:

```
pipenv shell
python -m ipykernel install --user --name=my-virtualenv-name
```

## Использование

Основная работа со статистикой происходит в jupyter блокноте `PantheonStatistics.ipynb`. 

```
jupyter notebook PantheonStatistics.ipynb
```

В блокноте нужно задать id турнира:

```
event_id = 204
```

Блокнот, используя API пантеона, получает игры и участников турнира (`https://gui.mjtop.net/eid204/last`). Полученные игры сохраняет на диск для работы в офлайн режиме.

Первичная обработка логов игр происходит в `pantheon_statistics.py`. Далее данные преобразуются в pandas DataFrame для дальнейшей обработки, сортировки и вывода результатов.
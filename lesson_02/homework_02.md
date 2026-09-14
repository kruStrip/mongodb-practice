# Домашнее задание № 2 · модуль 1 справочника и учебные базы

Срок — до начала занятия 3.

## Задание

1. Пройти модуль 1 справочника, главы 1.1–1.8.
2. Поднять учебный стенд и убедиться, что развернулись четыре базы.
3. Приложить скриншоты Compass и заполнить таблицу с числами.

## Ссылки

- Справочник, модуль 1: https://maximbytecamp.github.io/mongodb_theory_makarov/
- Стенд и данные: https://github.com/MaximBytecamp/mongodb-practice

Стенд поднимается в папке `stend` скачанного репозитория: `docker compose up -d`,
затем `bash load.sh`. Compass подключается строкой `mongodb://localhost:27017`.

## Сколько документов должно быть

Данные у всех одинаковые, поэтому числа должны совпасть. Если не совпали,
запустите `bash load.sh` ещё раз.

| База | Должно быть | У меня |
|---|---|---|
| `shop` | products 21 · orders 120 · customers 20 |  |
| `hh` | resumes 9 · vacancies 8 · companies 8 · interviews 60 |  |
| `logs` | events 1200 |  |
| `org` | employees 15 · categories 10 |  |

## Скриншоты

Пять кадров из Compass в папке `screens/`: список баз и каждая база с числами
документов. Файлы называйте `01-bazy.png`, `02-shop.png`, `03-hh.png`,
`04-logs.png`, `05-org.png` и вставляйте сюда строками вида

```
![shop](screens/02-shop.png)
```

## Сдача

Ветка `hw-02`, Pull Request в свою `main`.
Кнопки в VS Code: [ветки](../docs/git/README.md#5-ветки) ·
[коммиты](../docs/git/README.md#3-изменения-и-коммиты) ·
[Pull Request](../docs/git/README.md#6-ветки-на-github-и-pull-request).

На приёмке открываете Compass и показываете любую базу.

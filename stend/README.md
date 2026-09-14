# Стенд курса

Пока здесь один сервис — MongoDB. По ходу года сюда добавятся PostgreSQL,
ClickHouse, Redis и RabbitMQ, поэтому файл дописывается, а не переписывается.

## Команды

```bash
docker compose up -d      # поднять
docker compose ps         # статус: нужен healthy
docker compose logs mongo # что пишет сервер
docker compose down       # остановить, данные сохранить
docker compose down -v    # остановить и удалить данные
```

## Что внутри docker-compose.yml

| Строка | Что делает |
|---|---|
| `image: mongo:7` | версия сервера, одна и та же у всей группы |
| `ports: "27017:27017"` | пробрасывает порт наружу; левое число — то, к которому подключается Compass |
| `volumes: mongo-data:/data/db` | данные лежат в томе и переживают перезапуск контейнера |
| `healthcheck` | сервер считается готовым, только когда ответил на `ping` |

## Учебные данные

`seed/resumes.json` — массив из восьми резюме. Загружается в Compass:
**ADD DATA → Import JSON or CSV file**, формат определяется автоматически.
Даты записаны в расширенном виде `{"$date": "..."}`, поэтому попадают в базу
типом Date, а не строкой.

Первый документ вы создаёте руками через **ADD DATA → Insert document**,
поэтому после занятия в коллекции девять документов.

Формы документов намеренно разные: у одного есть `portfolio`, у другого
`courses`, у третьего `experience` — пустой массив.

С занятия 2 рядом лежат ещё четыре файла: `companies.json` — справочник компаний,
`resumes_embed.json` и `resumes_ref.json` — одни и те же 150 резюме в двух формах
(компания внутри документа и компания по ссылке), `interviews.json` — приглашения
на собеседование, в которых название компании продублировано второй раз.
Загружаются так же, каждый в свою коллекцию:

```bash
for f in companies resumes_embed resumes_ref interviews; do
  docker exec -i hh-mongo mongoimport --quiet --db hh --collection $f --drop --jsonArray < seed/$f.json
done
```

## Проверка без Compass

```bash
docker exec hh-mongo mongosh hh --quiet --eval 'db.resumes.countDocuments()'
docker exec hh-mongo mongosh hh --quiet --eval 'db.resumes.find({ city: "Ярославль" })'
```

`mongosh` уже внутри контейнера, отдельно ставить его не нужно.

## Если Docker не встаёт

Compass — только клиент, ему нужен адрес сервера, а откуда сервер взялся,
он не проверяет. Docker здесь — курсовой способ, но не единственный: та же
база поднимается локальной установкой MongoDB Community или бесплатным
кластером в Atlas. Три способа с командами, загрузкой данных и разбором
ошибок подключения — в [SETUP.md](SETUP.md).

## Запросы файлом

`queries.mongodb.js` — фильтры занятия в исполняемом виде, с ожидаемыми
числами в комментариях:

```bash
docker exec -i hh-mongo mongosh hh --quiet --file /dev/stdin < queries.mongodb.js
```

"""ПР-01 · Каталог товаров: витрина и правки.

Задача 1 — страница каталога, которую бэкенд отдаёт фронтенду (shop, чтение).
Задача 2 — приёмка поставки с отчётом (sandbox, запись).

Стенд — папка stend этого репозитория, данные — из учебного репозитория
MaximBytecamp/mongodb-practice. Подробности запуска в README.md рядом.

    docker compose -f ../stend/docker-compose.yml up -d
    bash ../../mongodb-practice/stend/load.sh    # чистые данные перед прогоном
    python3 solution.py                          # сервер на localhost:27017
    MONGO_URI=mongodb://host:27017 python3 solution.py
"""

import os

from pymongo import MongoClient
from pymongo.errors import BulkWriteError

URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(URI)

products = client["shop"]["products"]   # эталон, только читаем
box = client["sandbox"]["products"]     # песочница, здесь правим

# Поля, которые нужны списку товаров. Массив stock и specs на витрине
# не показывают — значит, и с сервера их не тянут.
CARD = {"_id": 0, "sku": 1, "title": 1, "price": 1, "rating": 1}


# ── Задача 1. Витрина каталога ──────────────────────────────────────
def catalog_page(category=None, page=1, per_page=5, sort_field="price", desc=True):
    """Одна страница каталога.

    Возвращает (items, total): товары этой страницы и сколько их всего
    под фильтром — из total фронт рисует «страница 2 из 5».
    """
    query = {}
    if category:                       # фильтр собирается, а не склеивается строкой
        query["category"] = category

    total = products.count_documents(query)   # считает сервер, не клиент

    cursor = (products
              .find(query, CARD)
              # sku — второй ключ сортировки: без него товары с равной ценой
              # меняются местами между запросами и «прыгают» по страницам
              .sort([(sort_field, -1 if desc else 1), ("sku", 1)])
              .skip((page - 1) * per_page)
              .limit(per_page))

    return list(cursor), total          # страница за пределами данных → []


def print_page(title, items, total=None):
    head = f"\n{title}" + (f" (всего {total})" if total is not None else "")
    print(head + ":")
    if not items:
        print("  — пусто")
    for item in items:
        print(f"  {item['price']:>7} ₽  {item['title']:<34} рейтинг {item['rating']}")


def show_catalog():
    print("=" * 62)
    print("ЗАДАЧА 1 · витрина каталога")
    print("=" * 62)

    per_page = 3
    items, total = catalog_page(category="ноутбуки", page=1, per_page=per_page)
    pages = -(-total // per_page)          # округление вверх
    print_page(f"Ноутбуки, страница 1 из {pages}", items, total)

    items, _ = catalog_page(category="ноутбуки", page=2, per_page=per_page)
    print_page("Страница 2", items)

    items, total = catalog_page(page=1, per_page=5)
    print_page("Весь каталог, топ-5 по цене", items, total)

    items, total = catalog_page(category="ноутбуки", page=9, per_page=per_page)
    print(f"\nСтраница 9 из существующих {pages}: найдено {len(items)} товаров, "
          f"total по-прежнему {total}")


# ── Задача 2. Приёмка поставки ──────────────────────────────────────
ARRIVED = {                     # что приехало: артикул → сколько штук
    "SKU-NB-001": 5,
    "SKU-PH-006": 12,
    "SKU-PR-010": 3,
}

NEW_ITEMS = [                   # новинки: свой _id делает повтор безопасным
    {"_id": "p-101", "sku": "SKU-AC-101", "title": "Подставка для ноутбука",
     "brand": "OEM", "category": "аксессуары", "price": 2490, "reviews": 0},
    {"_id": "p-102", "sku": "SKU-AC-102", "title": "Чехол для планшета",
     "brand": "OEM", "category": "аксессуары", "price": 1890, "reviews": 0},
]

DISCONTINUED = ["SKU-CP-018"]   # снимаем с продажи


def restock():
    """Шаг 1. Остатки прибавляет сервер ($inc), а не клиент.

    Чтение-в-Python-запись теряет товар: две приёмки читают 10, обе пишут 15,
    приехало 5 и 5 — вместо 20 в базе 15, и в логах об этом ни строчки.
    """
    updated = 0
    for sku, qty in ARRIVED.items():
        result = box.update_one({"sku": sku}, {"$inc": {"qty_total": qty}})
        if result.matched_count == 0:          # артикула может не быть в каталоге
            print(f"  ВНИМАНИЕ: артикул {sku} не найден в каталоге")
        updated += result.modified_count
    return updated


def add_new_items():
    """Шаг 2. Повторный запуск не должен плодить дубли.

    _id задан явно, поэтому вторая попытка упирается в E11000;
    ordered=False вставляет всё, что можно, и честно сообщает про остальное.
    """
    try:
        result = box.insert_many(NEW_ITEMS, ordered=False)
        return len(result.inserted_ids)
    except BulkWriteError as error:
        already = len(error.details["writeErrors"])
        print(f"  {already} позиций уже были в каталоге — пропущены")
        return len(NEW_ITEMS) - already


def discontinue():
    """Шаг 3. Посчитать → показать → удалить. Три строки, которые
    отделяют рабочий скрипт от опасного."""
    query = {"sku": {"$in": DISCONTINUED}}
    print(f"\n  под снятие с продажи попало: {box.count_documents(query)}")
    for doc in box.find(query, {"_id": 1, "title": 1, "price": 1}):
        print(f"    {doc}")
    return box.delete_many(query).deleted_count


def free_shipping():
    """Шаг 4. Признак ставится всей категории одним запросом — в песочнице."""
    query = {"category": "аксессуары"}
    print(f"\n  бесплатная доставка коснётся: {box.count_documents(query)} товаров")
    return box.update_many(query, {"$set": {"free_shipping": True}}).modified_count


def receive_supply():
    print("\n" + "=" * 62)
    print("ЗАДАЧА 2 · приёмка поставки")
    print("=" * 62)

    report = {}
    report["остатки обновлены"] = restock()
    report["новых позиций"] = add_new_items()
    report["снято с продажи"] = discontinue()
    report["бесплатная доставка"] = free_shipping()
    report["итого в каталоге"] = box.count_documents({})

    # Все числа — из результатов операций, ни одно не вписано руками.
    print("\nОтчёт о приёмке:")
    for name, value in report.items():
        print(f"  {name:<24} {value}")
    return report


if __name__ == "__main__":
    show_catalog()
    receive_supply()
    client.close()

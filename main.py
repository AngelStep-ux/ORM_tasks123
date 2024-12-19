import json
import os
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import create_tables, Publisher, Book, Shop, Stock, Sale


DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '725090')
DB_NAME = os.getenv('DB_NAME', 'netology_db')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

DSN = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()

with open(r'C:\Users\Honor\OneDrive\Рабочий стол\ORM дз\fixtures.json', 'r') as fd:
    data = json.load(fd)

for record in data:
    model = {
        'publisher': Publisher,
        'shop': Shop,
        'book': Book,
        'stock': Stock,
        'sale': Sale,
    }[record.get('model')]
    if model:
        session.add(model(id=record.get('pk'), **record.get('fields')))
    else:
        print(f"Модель {record.get('model')} не найдена.")

publisher_input = input('Введите имя или идентификатор издателя: ')

if not publisher_input:
    print("Вы не ввели имя или идентификатор издателя.")
else:
    if publisher_input.isdigit():
        publisher_id = int(publisher_input)
        publisher = session.get(Publisher, publisher_id)
    else:
        publisher = session.query(Publisher).filter(Publisher.name == publisher_input).first()

    if publisher:
        results = (
            session.query(Book.title, Shop.name, Sale.price, Sale.date_sale)
            .join(Stock, Stock.id_book == Book.id)
            .join(Sale, Sale.id_stock == Stock.id)
            .join(Shop, Stock.id_shop == Shop.id)
            .filter(Book.id_publisher == publisher.id)
            .all()
        )

        if results:
            for title, shop_name, price, date_sale in results:
                print(f"{title} | {shop_name} | {price} | {date_sale.strftime('%d-%m-%Y')}")
        else:
            print("Нет продаж для данного издателя.")
    else:
        print("Издатель не найден.")

session.commit()

session.close()
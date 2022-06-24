import sys
import json
import uuid
import random
import argparse
import typing as t

from datetime import datetime

import app.schemas as s


def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("endpoint", help="HTTP endoint.")
    parser.add_argument("-a", "--amount", dest="amount", type=int,
                        help="Units amount.", required=False)
    parser.add_argument("-d", "--data", dest="data", type=str,
                        help="Data which is going to be used.", required=False)

    return parser


def generate_data(amount: int) -> t.List[s.ShopUnitImport]:
    ids_pool = set(uuid.uuid4() for _ in range(amount))
    offers_ids_pool, categories_ids_pool = [], []

    choice = ["offer", "category"]
    for id in ids_pool:
        unit_type = random.choice(choice)
        if unit_type == choice[0]:
            offers_ids_pool.append(id)
        else:
            categories_ids_pool.append(id)

    offer_schemas_pool = []
    for offer in offers_ids_pool:
        parent_category = random.choice(categories_ids_pool)
        offer_schema = {
            "id": str(offer), "name": str(offer),
            "parentId": str(parent_category), "price": random.randint(0, 100),
            "type": s.ShopUnitType.offer,
        }
        offer_schemas_pool.append(offer_schema)

    category_schemas_pool = []
    for index, category in enumerate(categories_ids_pool):
        parent_category = category_schema = {
            "id": str(category), "name": str(category),
            "parentId": None, "price": None,
            "type": s.ShopUnitType.category,
        }

        if len(categories_ids_pool[index+1:]) != 0:
            category_schema["parentId"] = str(random.choice(
                categories_ids_pool[index+1:]))

        category_schemas_pool.append(category_schema)

    return offer_schemas_pool + category_schemas_pool


def import_data(data: str):
    data_import = {}

    with open(data, "r") as file:
        data_text = file.read()
        data_json = json.loads(data_text)
        data_import = {
            "items": data_json,
            "updateDate": f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z"
        }

    return data_import


def main():
    parser = setup()
    args = parser.parse_args()

    if args.endpoint == "data":
        data = generate_data(args.amount)
        sys.stdout.write(json.dumps(data))
    if args.endpoint == "imports":
        data = import_data(args.data)
        sys.stdout.write(json.dumps(data))


if __name__ == '__main__':
    main()

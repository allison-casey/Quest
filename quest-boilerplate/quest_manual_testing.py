import parse_quest_manual
import json
import pyjq
import requests
from pprint import pprint

# with open('quest-manual.html', 'r') as f, open('items.json', 'w') as out:
#     items = parse_quest_manual.parse_manual(f.read())
#     print(len(items))
#     json.dump(items, out, indent=2)


def run_query(payload):
    request = requests.post("http://192.168.1.40:8081/quest", json=payload)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Query failed to run by returning code of {}, {}".format(
                request.status_code, payload
            )
        )


def get_armors(attributes):
    query = """
    query {{
        armors {{
            {}
        }}
    }}
    """.format(
        " ".join(attributes)
    )
    return run_query({"query": query})


def insert_weapons():
    query = """
    mutation createWeapons($weaponList: [WeaponAttributes]) {
        addWeapons(attributesList: $weaponList) {
            name
        }
    }
    """
    with open("items.json", "r") as f:
        items = json.load(f)

    weapon_types = pyjq.all(
        '.[] | select(.category == "ranged weapons") | .content[]', items
    )

    weapons = []
    for weapon in weapon_types:
        if weapon["type"] == "ranged weapon glossary":
            continue
        weapons.extend([dict(item) for item in weapon["items"]])

    payload = {"query": query, "variables": {"weaponList": weapons}}

    result = run_query(payload)
    pprint(result)


def insert_armors():
    with open("items.json", "r") as f:
        items = json.load(f)

    armor_types = pyjq.all(
        '.[] | select(.category == "armor sets") | .content[]', items
    )

    armor_type_lookup = {
        "clothing": "CLOTHING",
        "light armor": "LIGHT",
        "medium armor": "MEDIUM",
        "heavy armor": "HEAVY",
        "power armor": "POWER",
    }

    armors = []
    for armor_type in armor_types:
        type = armor_type_lookup[armor_type["type"]]
        for armor in armor_type["items"]:
            armor["type"] = type
            armors.append(dict(armor))

    query = """
    mutation createArmors($armorList: [ArmorAttributes]) {
        addArmors(attributesList: $armorList) {
            name
        }
    }
    """

    payload = {"query": query, "variables": {"armorList": armors}}

    result = run_query(payload)
    pprint(result)


if __name__ == "__main__":
    # pprint(len(get_armors(["name", "dt", "value"])["data"]["armors"]))
    pprint(insert_armors())
    pprint(insert_weapons())

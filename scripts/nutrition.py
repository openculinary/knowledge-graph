import argparse
import json
import os
from pathlib import Path
import sys

from web.loader import (
    CACHE_PATHS,
    write_items,
)
from web.models.nutrition import Nutrition

NUTRITION_PATHS = {
    'lookup': 'web/data/external/ingreedy-data/data/processed/foodmap.json',
    'mccance': 'web/data/external/ingreedy-data/data/processed/mccance.json',
    'usfdc': 'web/data/external/ingreedy-data/data/processed/usfdc.json',
}


parser = argparse.ArgumentParser(description='Generate nutrition data')
parser.add_argument(
    '--nutrition',
    default=CACHE_PATHS['nutrition'],
    help='Cached nutrition file to read/write'
)
parser.add_argument(
    '--update',
    action='store_true',
    help='Update cached content'
)
args = parser.parse_args()


def source_nutrition():
    lookup = NUTRITION_PATHS['lookup']
    if not os.path.exists(lookup):
        raise RuntimeError(f'Could not read nutrition lookup from: {lookup}')
    with open(lookup) as f:
        lookup = json.loads(f.read())

    mccance = NUTRITION_PATHS['mccance']
    if not os.path.exists(mccance):
        raise RuntimeError(f'Could not read mccance nutrition from: {mccance}')
    with open(mccance) as f:
        mccance = json.loads(f.read())
        mccance = {item["name"]: item for item in mccance}

    usfdc = NUTRITION_PATHS['usfdc']
    if not os.path.exists(usfdc):
        raise RuntimeError(f'Could not read usfdc nutrition from: {usfdc}')
    with open(usfdc) as f:
        usfdc = json.loads(f.read())
        usfdc = {item["name"]: item for item in usfdc}

    for metadata in lookup:
        nutrition = None
        product = metadata["normalized_name"]
        datasets = {"food": mccance, "food_usfdc": usfdc}
        for key, dataset in datasets.items():
            name = metadata[key]
            if name and name in dataset:
                nutrition = dataset[name]
                break
        if not nutrition:
            continue
        yield Nutrition(
            product=product,
            fat=nutrition["fat"],
            protein=nutrition["protein"],
            carbohydrates=nutrition["carbs"],
            energy=nutrition.get("energy") or nutrition.get("cals"),
            fibre=nutrition["fibre"],
        )


if __name__ == '__main__':
    output = sys.stdout
    if args.update:
        Path(args.nutrition).parent.mkdir(parents=True, exist_ok=True)
        output = open(args.nutrition, 'w')
    nutrition = source_nutrition()
    write_items(nutrition, output)
    output.close()

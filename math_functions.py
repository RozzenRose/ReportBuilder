async def pie_prices(data: dict) -> dict:
    answer_data = {}
    categories = [item for item in data['categories']]
    purchases = [item for item in data['purchases']]

    for cat in categories:
        answer_data[cat['category_name']] = 0
        for pur in purchases:
            if cat['id'] == pur['category_id']:
                answer_data[cat['category_name']] += pur['price']
        if answer_data[cat['category_name']] == 0:
            del answer_data[cat['category_name']]

    return tuple(answer_data.items())
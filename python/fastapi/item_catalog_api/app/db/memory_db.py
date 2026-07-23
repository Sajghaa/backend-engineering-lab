items_db = []
next_id = 1

def add_item(item_data):
    global next_id
    item = item_data.model_dump()   # convert Pydantic model to dict
    item["id"] = next_id
    items_db.append(item)
    next_id += 1
    return item

def get_item_by_id(item_id: int):
    for item in items_db:
        if item["id"] == item_id:
            return item
    return None
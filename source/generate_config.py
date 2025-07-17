from .kanban_base import KanbanBase 
import json

avarage_production = [0,0,0,0,0]

for idx in range(0,5):
    mul = round(0.3 - idx*0.05, 2)
    avarage_production[idx] = round((650*mul)*0.95 + (650*(mul+0.2))*0.05)

# Warehouse

part_production_warehouse = dict.fromkeys(KanbanBase.PARTS, 0)
products_use = dict.fromkeys(KanbanBase.PARTS, 0)

for part in KanbanBase.PARTS:
    for idx in range(0,5):
        if part in KanbanBase.PRODUCT_PARTS[f"prod{(idx+1):0>2}"]:
            part_production_warehouse[part] += avarage_production[idx]
            products_use[part] += 1

warehouse_type_order = {}
lead_time = {}
for part in KanbanBase.PARTS:
    if products_use[part] == 5:
        warehouse_type_order[part] = 1800
        lead_time[part] = 4
    elif products_use[part] == 2:
        warehouse_type_order[part] = 600
        lead_time[part] = 2
    elif products_use[part] == 1:
        warehouse_type_order[part] = 200
        lead_time[part] = 1

warehouse_stock_args = {
    part: dict(
        max_capacity= 0,
        initial_stock= 0,
        red_threshold= 0, 
        yellow_threshold= 0
    )
    for part in KanbanBase.PARTS
}

for part in KanbanBase.PARTS:
    red = part_production_warehouse[part] * lead_time[part]
    yellow = round(red*1.25)
    max_capacity = 10000
    initial = (max_capacity - yellow)//2 + yellow
    
    warehouse_stock_args[part]["max_capacity"] = max_capacity
    warehouse_stock_args[part]["initial_stock"] = initial
    warehouse_stock_args[part]["red_threshold"] = red
    warehouse_stock_args[part]["yellow_threshold"] = yellow

warehouse_config = {
    "stock_args": warehouse_stock_args,
    "order_args": warehouse_type_order
}

# Factory
push_lines_args = {}
for idx in range(1,6):
    push_lines_args[f"line{idx:0>2}"] = {}
    for part in KanbanBase.PARTS:
        if part in KanbanBase.PRODUCT_PARTS[f"prod{idx:0>2}"]:
            push_lines_args[f"line{idx:0>2}"][part] = dict(
                max_capacity= 300,
                initial_stock= 210,
                red_threshold= 120, 
                yellow_threshold= 150
            )
        else:
            push_lines_args[f"line{idx:0>2}"][part] = dict(
                max_capacity= 0,
                initial_stock= 0,
                red_threshold= 0, 
                yellow_threshold= 0
            )
        
    initial_stock = dict.fromkeys(KanbanBase.PRODUCT_PARTS.keys(), 0)
    initial_stock[f"prod{idx:0>2}"] = 210

    push_lines_args[f"line{idx:0>2}"]["product"] = {
        "max_capacity": 300,
        "initial_stock": initial_stock
    }

pull_lines_args = {}
for idx in range(1,9):
    pull_lines_args[f"line{idx:0>2}"] = {
        part: dict(
            max_capacity= 300,
            initial_stock= 210,
            red_threshold= 120, 
            yellow_threshold= 150
        )
        for part in KanbanBase.PRODUCT_PARTS.keys()
    }
    pull_lines_args[f"line{idx:0>2}"]["product"] = {
        "max_capacity": 300,
        "initial_stock": dict.fromkeys(KanbanBase.PRODUCT_PARTS.keys(), 0)
    }

push_factory_args = {
    "line_args": push_lines_args,
    
}
pull_factory_args = {
    "line_args": pull_lines_args, 
}

# Manager
manager_stock_args = {}
for idx in range(0,5):
    red = avarage_production[idx] * 2
    yellow = round(red*1.25)
    max_capacity = 3900
    initial = (max_capacity - yellow)//2 + yellow

    manager_stock_args[f"prod{idx+1:0>2}"] = dict(
        max_capacity= max_capacity,
        initial_stock= 210,
        red_threshold= red, 
        yellow_threshold= yellow
    )

manager_config = {
    "stock_args": manager_stock_args
}

# Marketplace
marketplace_config = {
    "market_campaign_chance": 0.05,
    "product_proportion": {
        prod: round(0.3 - idx*0.05, 2)
        for idx, prod in enumerate(KanbanBase.PRODUCT_PARTS.keys())
    }
}
    
with open("./config/warehouse_config.json", "w") as fil:
    json.dump(warehouse_config, fil)

with open("./config/push_factory_args.json", "w") as fil:
    json.dump(push_factory_args, fil)

with open("./config/pull_factory_args.json", "w") as fil:
    json.dump(pull_factory_args, fil)

with open("./config/manager_config.json", "w") as fil:
    json.dump(manager_config, fil)

with open("./config/marketplace_config.json", "w") as fil:
    json.dump(marketplace_config, fil)

from source.factory import Factory
from source.kanban_base import KanbanBase
import json

LOADINGS = [f"push-factory_line{idx:0>2}_part{part}_loading" for idx in range(1,6) for part in KanbanBase.PARTS]

ORDERS = [f"manager_push-factory_line{idx:0>2}_order" for idx in range(1,6)]

PRODUCT_ORDERS = [f"push-factory_{product}_order" for product in KanbanBase.PRODUCT_PARTS.keys()]

with open("push_factory_config.json", "r") as fil:
    push_factory_config = json.load(fil)

push_factory = Factory(
    "push-factory", 
    LOADINGS, 
    ORDERS, 
    PRODUCT_ORDERS, 
    **push_factory_config
)

push_factory.loop_forever()
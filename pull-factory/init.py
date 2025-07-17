from source.factory import Factory
from source.kanban_base import KanbanBase
import json

LOADINGS = [f"pull-factory_line{idx:0>2}_part{part}_loading" for idx in range(1,9) for part in KanbanBase.PARTS]

ORDERS = [f"manager_pull-factory_line{idx:0>2}_order" for idx in range(1,9)]

PRODUCT_ORDERS = [f"pull-factory_{product}_order" for product in KanbanBase.PRODUCT_PARTS.keys()]

with open("/app/pull_factory_config.json", "r") as fil:
    pull_factory_config = json.load(fil)

pull_factory = Factory(
    "push-factory", 
    LOADINGS, 
    ORDERS, 
    PRODUCT_ORDERS, 
    **pull_factory_config
)

pull_factory.loop_forever()
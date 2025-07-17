from source.warehouse import Warehouse
from source.kanban_base import KanbanBase
from source.factory import Factory
import json

LOADINGS = [f"suppliers_part{part}_loading" for part in KanbanBase.PARTS]

ORDERS = [
    *[f"push-factory_{line}_part{part}_order" for line in Factory.PUSH_LINES for part in KanbanBase.PARTS],
    *[f"pull-factory_{line}_part{part}_order" for line in Factory.PULL_LINES for part in KanbanBase.PARTS]
]

with open("/app/warehouse_config.json", "r") as fil:
    warehouse_config = json.load(fil)

warehouse = Warehouse(loadings= LOADINGS, orders= ORDERS, **warehouse_config)
warehouse.loop_forever()
from source.manager import Manager
from source.kanban_base import KanbanBase
import json

PRODUCT_ORDERS = [f"marketplace_{prod}_order" for prod in KanbanBase.PRODUCT_PARTS.keys()]
FACTORY_DATA = ["push-factory_data", "pull-factory_data"]


with open("manager_config.json", "r") as fil:
    manager_config = json.load(fil)

manager = Manager(
    FACTORY_DATA,
    PRODUCT_ORDERS,
    **manager_config
)

manager.loop_forever()
from source.marketplace import Marketplace
from source.kanban_base import KanbanBase
import json

PRODUCT_ORDERS = [f"marketplace_{prod}_order" for prod in KanbanBase.PRODUCT_PARTS.keys()]
FACTORY_DATA = ["push-factory_data", "pull-factory_data"]


with open("marketplace_config.json", "r") as fil:
    marketplace_config = json.load(fil)

marketplace = Marketplace(
    **marketplace_config
)

marketplace.loop_forever()
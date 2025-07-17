from ..source.marketplace import Marketplace
from ..source.kanban_base import KanbanBase
import json

PRODUCT_ORDERS = [f"marketplace_{prod}_order" for prod in KanbanBase.PRODUCT_PARTS.keys()]
FACTORY_DATA = ["push-factory_data", "pull-factory_data"]


with open("../config/marketplace_config.json", "w") as fil:
    marketplace_config = json.lead(fil)

marketplace = Marketplace(
    **marketplace_config
)

marketplace.loop_forever()
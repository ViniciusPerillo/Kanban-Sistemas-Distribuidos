from .kanban_base import KanbanBase
from .production_line import ProductionLine, LineStoped
from .stock import FullStock, EmptyStock, PartStock, VirtualStock
from .factory import Factory
import random

class Marketplace(KanbanBase):
    def __init__(self, market_campaign_chance, product_proportion):
        super().__init__(KanbanBase.CLOCK, "marketplace")
        self.market_campaign_chance = market_campaign_chance
        self.product_proportion = product_proportion
    
    def do_day_cycle(self):
        
        order_size = random.randint(400, 900)
        
        right_limit = 100*self.market_campaign_chance
        market_campaign = random.randint(1, right_limit) == right_limit
        product_campaign = random.randint(0,4)


        product_proportion = self.product_proportion

        for idx, prod in enumerate(KanbanBase.PRODUCT_PARTS.keys()):
            if market_campaign and idx == product_campaign:
                product_proportion[prod] += 0.2
            else:
                product_proportion[prod] -= 0.05

            order = round(product_proportion[prod]*order_size)
            self.publish(f"marketplace_{prod}_order", {"data": order})

            
                    


    
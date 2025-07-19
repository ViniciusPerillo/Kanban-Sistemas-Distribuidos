from .kanban_base import KanbanBase
from .production_line import ProductionLine, LineStoped
from .stock import FullStock, EmptyStock, PartStock, VirtualStock
from .factory import Factory
from .utils import print_log
import random

class Marketplace(KanbanBase):

    @staticmethod
    def truncated_normal(min_val, max_val, mean, std_dev_ratio=6.0):
        std_dev = (max_val - min_val) / std_dev_ratio
        
        while True:
            # Gera número com distribuição normal
            value = random.gauss(mean, std_dev)
            if min_val <= value <= max_val:
                return int(value)

    def __init__(self, market_campaign_chance, product_proportion):
        super().__init__([KanbanBase.CLOCK], "marketplace")
        self.market_campaign_chance = market_campaign_chance
        self.product_proportion = product_proportion
        self.counter = 0
    
    def do_day_cycle(self):
        
        order_size = Marketplace.truncated_normal(100, 1000, 350, 6)
        
        right_limit = round(100/self.market_campaign_chance)
        market_campaign = random.randint(1, right_limit) == right_limit
        product_campaign = random.randint(0,4)


        product_proportion = self.product_proportion
        final_order = {}

        for idx, prod in enumerate(KanbanBase.PRODUCT_PARTS.keys()):
            if market_campaign:
                if idx == product_campaign:
                    product_proportion[prod] += 0.2
                else:
                    product_proportion[prod] -= 0.05

            order = round(product_proportion[prod]*order_size)
            
            if self.counter < 3:
                order = 0

            final_order[prod] = order
            self.publish(f"marketplace_{prod}_order", {"data": order})
            print_log(f"Pedido {prod}: {order}")

        self.counter += 1
        self.publish(f'marketplace_data', {"data": final_order})


        

            
                    


    
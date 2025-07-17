from kanban_base import KanbanBase
from production_line import ProductionLine, LineStoped
from stock import FullStock, EmptyStock, PartStock, VirtualStock
from factory import Factory
from utils import print_log
from math import floor

class Manager(KanbanBase):
    
    

    def __init__(self, factory_data, product_orders, stock_args):
        super().__init__([KanbanBase.CLOCK] + factory_data + product_orders, "manager")
        
        self.data = factory_data
        self.product_orders = product_orders

        self.push_factory_data: dict[str, ProductionLine]
        self.pull_factory_data: dict[str, ProductionLine]

        self.virtual_stocks = {
            prod: VirtualStock(**stock_args[prod])
            for prod in KanbanBase.PRODUCT_PARTS.keys()
        }

        self.order = dict.fromkeys(KanbanBase.PRODUCT_PARTS.keys(), 0)


    def att_virtual_stock(self):
        lines = list(self.push_factory_data.values())\
                + list(self.pull_factory_data.values())
        
        for product in KanbanBase.PRODUCT_PARTS.keys():
            self.virtual_stocks[product].reset_stock()    
            
            for line in lines:
                self.virtual_stocks[product].replenish(line.product_stock[product])

    def _count_factory(self, factory, product):
        if factory == "pull":
            return sum([line.product_stock[product] for line in self.pull_factory_data.values()])
        elif factory == "push":
            return sum([line.product_stock[product] for line in self.push_factory_data.values()])
        
        raise KeyError
        
    def increment_orders(self):
        for p_order in self.product_orders:
            _, prod, _ = p_order.split('_')
            self.order[prod] += self.to_do[p_order]


    def pack_products(self):
        for p_order in self.product_orders:
            _, prod, _ = p_order.split('_')
            pull = 0
            push = 0

            if self.order[prod] < 60:
                push += self.order[prod]
                self.order[prod] = 0
            else:
                push += 60
                self.order[prod] -= 60

            if self.order[prod] < self._count_factory(prod):
                pull += self.order[prod]
                self.order[prod] = 0
            else:
                pull += self._count_factory(prod)
                self.order[prod] -= self._count_factory(prod)

            if self.order[prod] < self._count_factory(prod):
                pull += self.order[prod]
                self.order[prod] = 0
            else:
                pull += self._count_factory(prod)
                self.order[prod] -= self._count_factory(prod)

            self.virtual_stocks[prod].consume(pull + push)
            

            self.publish(f"push-factory_{prod}_order", {"data": push})
            self.publish(f"pull-factory_{prod}_order", {"data": pull})

    def distribute_production(self):
        push_lines = dict.fromkeys(Factory.PUSH_LINES, 0)
        pull_lines = dict.fromkeys(Factory.PULL_LINES, 0)
        products_to_do = [[0,0],[1,0],[2,0],[3,0],[4,0]]
        
        for idx, prod in enumerate(KanbanBase.PRODUCT_PARTS.keys()):
            stock = self.virtual_stocks[prod]
            if stock.kanban_flag <= 1:
                products_to_do[1][idx] = stock.yellow_threshold - stock.stock

        for idx, qtd in products_to_do:
            prod = f"prod{idx+1:0>2}"

            total_lines_needed = floor(qtd / 60) 

            push_lines[f"line{idx+1:0>2}"] = {"product":prod, "amount": 60}

            for line in pull_lines.keys():
                
                if total_lines_needed > 0 and pull_lines[line] == 0:
                    pull_lines[line] = {"product":prod, "amount": 60}
                    total_lines_needed -= 1
                else:
                    break

        for line, order in push_lines.items():
            self.publish(f"manager_push-factory_{line}_order", order)

        for line, order in pull_lines.items():
            self.publish(f"manager_push-factory_{line}_order", order)

    def do_day_cycle(self):
        self.increment_orders()
        self.pack_products()
        self.distribute_production()

        payload = {"data": {"order": self.order, "virtual_stock": self.virtual_stocks}}
        self.publish(f'manager_data', payload)
            
        


            
        




            




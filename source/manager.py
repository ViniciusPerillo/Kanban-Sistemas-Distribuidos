from .kanban_base import KanbanBase
from .production_line import ProductionLine, LineStoped
from .stock import FullStock, EmptyStock, PartStock, VirtualStock
from .factory import Factory
from .utils import print_log
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

    def get_data(self):
        self.push_factory_data = self.to_do["push-factory_data"]
        self.pull_factory_data = self.to_do["pull-factory_data"]
        for p_order in self.product_orders:
            _, prod, _ = p_order.split('_')
            if self.to_do[p_order] != None:
                self.order[prod] += self.to_do[p_order]

    def att_virtual_stock(self):
        if self.pull_factory_data != None and self.push_factory_data != None:
            lines = list(self.push_factory_data.values())\
                    + list(self.pull_factory_data.values())
            
            for product in KanbanBase.PRODUCT_PARTS.keys():
                self.virtual_stocks[product].reset_stock()    
                
                for line in lines:
                    self.virtual_stocks[product].replenish(line.product_stock[product])

    def _count_factory(self, factory, product):
        if factory == "pull":
            data = self.pull_factory_data
        elif factory == "push":
            data = self.push_factory_data
        else:
            raise KeyError
        
        total = 0
        for line in data.values():
            total += line.product_stock[product]
        
        return total
        
        
    def increment_orders(self):
        for p_order in self.product_orders:
            _, prod, _ = p_order.split('_')
            if self.to_do[p_order] is not None:
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

            if self.pull_factory_data != None and self.push_factory_data != None:
                if self.order[prod] < self._count_factory("pull", prod):
                    pull += self.order[prod]
                    self.order[prod] = 0
                else:
                    pull += self._count_factory("pull", prod)
                    self.order[prod] -= self._count_factory("pull", prod)

                if self.order[prod] < self._count_factory("push", prod):
                    push += self.order[prod]
                    self.order[prod] = 0
                else:
                    push += self._count_factory("push", prod)
                    self.order[prod] -= self._count_factory("push", prod)

                try:
                    self.virtual_stocks[prod].consume(pull + push)
                except EmptyStock:
                    pass
            

            self.publish(f"push-factory_{prod}_order", {"data": push})
            self.publish(f"pull-factory_{prod}_order", {"data": pull})

    def distribute_production(self):
        push_lines = dict.fromkeys(Factory.PUSH_LINES, None)
        pull_lines = dict.fromkeys(Factory.PULL_LINES, None)
        products_to_do = [0,0,0,0,0]
        
        
        for idx, qtd in enumerate(products_to_do):
            prod = f"prod{idx+1:0>2}"
            products_to_do[idx] = self.order[prod]
            push_lines[f"line{idx+1:0>2}"] = {"product":prod, "amount": 60}

        print(products_to_do)

        for line, order in push_lines.items():
            self.publish(f"manager_push-factory_{line}_order", {"data": order})

        for idx, prod in enumerate(KanbanBase.PRODUCT_PARTS.keys()):
            stock = self.virtual_stocks[prod]
            if stock.kanban_flag <= 1:
                products_to_do[idx] = stock.yellow_threshold - stock.stock

        for idx, qtd in products_to_do:
            prod = f"prod{idx+1:0>2}"

            total_lines_needed = floor(qtd / 60) 
            for line in pull_lines.keys():
                
                if total_lines_needed > 0 and pull_lines[line] == 0:
                    pull_lines[line] = {"product":prod, "amount": 60}
                    total_lines_needed -= 1
                else:
                    continue   

        for line, order in pull_lines.items():
            self.publish(f"manager_pull-factory_{line}_order", {"data": order})
        
        print(push_lines)
        print(pull_lines)

    def do_day_cycle(self):
        self.get_data()
        self.increment_orders()
        self.pack_products()
        self.distribute_production()

        payload = {"data": {"order": self.order, "virtual_stock": self.virtual_stocks}}
        self.publish(f'manager_data', payload)
            
        


            
        




            




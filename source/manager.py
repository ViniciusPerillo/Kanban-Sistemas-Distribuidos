from .kanban_base import KanbanBase
from .production_line import ProductionLine, LineStoped
from .stock import FullStock, EmptyStock, PartStock, VirtualStock
from .factory import Factory
from .utils import print_log
import math

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

    def normalize(products_to_do):

        sum_values = sum([prod[1] for prod in products_to_do])
        lines = [[idx, round((qtd/sum_values)*8)]for idx, qtd in products_to_do]

        return lines

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
                
                total = 0
                for line in lines:
                    self.virtual_stocks[product].replenish(line.product_stock[product])

                    for product_y in KanbanBase.PRODUCT_PARTS.keys():
                        if product != product_y:
                            total += line.product_stock[product_y]

                    self.virtual_stocks[product].max_capacity = 6800 - total


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

            if self.pull_factory_data != None and self.push_factory_data != None:
                if self.order[prod] <= self._count_factory("push", prod):
                    push += self.order[prod]
                    self.order[prod] = 0
                else:
                    push += self._count_factory("push", prod)
                    self.order[prod] -= self._count_factory("push", prod)
                
                if self.order[prod] <= self._count_factory("pull", prod):
                    pull += self.order[prod]
                    self.order[prod] = 0
                else:
                    pull += self._count_factory("pull", prod)
                    self.order[prod] -= self._count_factory("pull", prod)

                try:
                    self.virtual_stocks[prod].consume(pull + push)
                except EmptyStock:
                    pass
            
            self.publish(f"push-factory_{prod}_order", {"data": push})
            self.publish(f"pull-factory_{prod}_order", {"data": pull})

    def distribute_production(self):
        push_lines = dict.fromkeys(Factory.PUSH_LINES, None)
        pull_lines = dict.fromkeys(Factory.PULL_LINES, None)

        
        for idx, prod in enumerate(KanbanBase.PRODUCT_PARTS.keys()):
            stock = self.virtual_stocks[prod]
            if stock.kanban_flag <= 1:
                products_to_do[idx][1] = (stock.yellow_threshold - stock.stock)
        
        products_to_do = sorted(products_to_do, key= lambda x: x[1], reverse=True)
        print_log(f"Priorizaçãso de produção: {'->'.join([f'prod{idx[0]+1}: {idx[1]}' for idx in products_to_do])}")

        for idx, qtd in products_to_do:
            prod = f"prod{idx+1:0>2}"
            push_lines[f"line{idx+1:0>2}"] = {"product":prod, "amount": 60}

        lines_needed = [prod.copy() for prod in products_to_do]
        total_lines_needed = 0
        for idx, qtd in products_to_do:
            prod_lines_needed = math.ceil(qtd / 60)
            total_lines_needed += prod_lines_needed
            lines_needed[idx][1] = prod_lines_needed

        if total_lines_needed > 8:
            lines_needed = Manager.normalize([prod.copy() for prod in products_to_do])

        print_log(f"Linhas Pull: {' | '.join([f'prod{idx[0]+1}:{idx[1]}' for idx in lines_needed])}")

        for idx, qtd in lines_needed:
            prod = f"prod{idx+1:0>2}"

            total_lines_needed = qtd
            for line in pull_lines.keys():
                
                if total_lines_needed > 0 and pull_lines[line] == None:
                    pull_lines[line] = {"product":prod, "amount": 60}
                    total_lines_needed -= 1
                else:
                    continue   

        for line, order in pull_lines.items():
            self.publish(f"manager_pull-factory_{line}_order", {"data": order})

        for line, order in push_lines.items():
            self.publish(f"manager_push-factory_{line}_order", {"data": order})
        

    def do_day_cycle(self):
        self.get_data()
        self.att_virtual_stock()
        self.increment_orders()
        self.pack_products()
        self.distribute_production()

        payload = {"data": {"order": self.order, "virtual_stock": self.virtual_stocks}}
        self.publish(f'manager_data', payload)
            
        


            
        




            




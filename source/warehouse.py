from .kanban_base import KanbanBase
from .stock import PartStock, FullStock, EmptyStock
from .utils import print_log, print_warning

class Warehouse(KanbanBase):    
    def __init__(self, loadings, orders, stock_args, order_args):
        super().__init__([KanbanBase.CLOCK] + loadings + orders, "warehouse")
        self.loadings = loadings
        self.orders = orders

        self.stocks = {
            part: PartStock(**stock_args[part])
            for part in KanbanBase.PARTS
        }
        self.in_order = dict.fromkeys(KanbanBase.PARTS, False)
        self.type_order = order_args
        self.reset_flags()

    def reset_flags(self):
        for stock in self.stocks.keys():
            self.stocks[stock].reset_flags()

    def recieve_loadings(self):
        for loading in self.loadings:
            if self.to_do[loading] is not None:
                _, part, _ = loading.split('_')
                try: 
                    self.stocks[part].replenish(self.to_do[loading])
                except FullStock as e:
                    print_warning(f"Estoque cheio: {e.lost} {part} perdidas")
                
                self.in_order[part] = False

    def send_line_loadings(self):
        for order in self.orders:
            if self.to_do[order] is not None:
                factory, line, part, _ = order.split('_')
                try: 
                    self.stocks[part].consume(self.to_do[order])
                except EmptyStock as e:
                    consumed = e.consumed
                    print_warning(f"Estoque vazio: {e.consumed} {part} consumidas - {e.missing} peças faltantes")
                else:
                    consumed = self.to_do[order]

                topic = "_".join([factory, line, part, "loading"])
                self.publish(topic, {"data": consumed})

    def make_suppliers_orders(self):
        for part in KanbanBase.PARTS:
            if self.stocks[part].kanban_flag <= 1 and not self.in_order[part]:
                self.publish(f"warehouse_{part}_order", {"data": self.type_order[part]})
                self.in_order[part] = True

    def do_day_cycle(self):
        self.recieve_loadings()
        self.send_line_loadings()
        self.make_suppliers_orders()

        self.publish('warehouse_data', {'data': self.stocks})
        self.reset_flags()
                


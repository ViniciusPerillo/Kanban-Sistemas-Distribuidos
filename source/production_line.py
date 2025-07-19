from .stock import ProductStock, PartStock, FullStock, EmptyStock
from .kanban_base import KanbanBase

class LineStoped(Exception):
    def __init__(self, produced, not_produced):
        super().__init__()
        self.produced = produced
        self.not_produced = not_produced

class ProductionLine():
    
    def __init__(self, args):
        self.part_stocks = {
            part: PartStock(**args[part])
            for part in KanbanBase.PARTS
        }

        self.product_stock = ProductStock(**args["product"])

    def __str__(self):
        return "ProductionLine"

    def reset_flags(self):
        for part_stock in self.part_stocks.values():
            part_stock.reset_flags()
        
        self.product_stock.reset_flags()

    def produce(self, product: str, amount: int):
        produced = amount
        for part_idx, part_label_x in enumerate(KanbanBase.PRODUCT_PARTS[product]):
            try:
                self.part_stocks[part_label_x].consume(produced)
            except EmptyStock as e:
                to_correct = produced - e.consumed
                produced = e.consumed

                for part_label_y in KanbanBase.PRODUCT_PARTS[product][:part_idx]:
                    self.part_stocks[part_label_y].replenish(to_correct)

        self.product_stock.replenish(product, produced)

        if produced < amount:
            raise LineStoped(produced, amount - produced)
        
    def replenish(self, part: str, amount: int):
        self.part_stocks[part].replenish(amount)

    def consume(self, product: str, amount: int):
        self.product_stock.consume(product, amount)

    def need_replenish(self, part: str):
        return self.part_stocks[part].kanban_flag < 2
        

        




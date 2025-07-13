from KanbanBase import KanbanBase
from Stock import Stock, FullStock, EmptyStock

class Warehouse(KanbanBase):
    
    LOADINGS = [f"fornecedor_part{part}_loading" for part in KanbanBase.PARTS]
    
    ORDERS = [
        *[f"fabrica-01-linha{idx}_part{part}_order" for idx in range(1,6) for part in KanbanBase.PARTS],
        *[f"fabrica-02-linha{idx}_part{part}_order" for idx in range(1,9) for part in KanbanBase.PARTS]
    ]

    TOPICS = ["clock"] + LOADINGS + ORDERS
    
    def __init__(self, **kargs):
        super().__init__(Warehouse.TOPICS, "warehouse")
        
        self.stocks = {
            part: Stock(
                max_capacity= kargs[f"{part}max_capacity"],
                yellow_threshold= kargs[f"{part}yellow_threshold"],
                red_threshold= kargs[f"{part}red_threshold"]
            )
            for part in KanbanBase.PARTS
        }

        self.type_order = {part: kargs[f"{part}type_order"] for part in KanbanBase.PARTS}
        self.reset_flags()

    def reset_flags(self):
        for stock in self.stocks.values():
            stock.reset_flags()

    def do_day_cycle(self):

        # Loading Stocks
        for loading in Warehouse.ORDERS:
            if self.to_do[loading] is not None:
                _, part, _ = loading.split('_')
                try: 
                    self.stocks[part].replenish(self.to_do[loading])
                except FullStock as e:
                    self.full_flags = e.lost

        # Lines Orders
        for order in Warehouse.ORDERS:
            if self.to_do[order] is not None:
                line, part, _ = order.split('_')
                try: 
                    self.stocks[part].consume(self.to_do[order])
                except EmptyStock as e:
                    self.empty_flags[part] = 1
                    consumed = e.consumed
                else:
                    consumed = self.to_do[order]

                topic = "_".join([line,part,"loading"])
                self.publish(topic, {"data": consumed})
        
        # Part Ordering
        for part in KanbanBase.PARTS:
            if self.stocks[part].flag == 1:
                self.publish(f"fornecedor_{part}_order", {"data": 2**self.type_order * 100})

        self.publish('almoxarifado_finished', {'data': 1})
        self.publish('almoxarifado_data', self.stocks)
        self.reset_flags()
                


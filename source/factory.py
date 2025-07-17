from .kanban_base import KanbanBase
from .production_line import ProductionLine, LineStoped
from .stock import FullStock, EmptyStock
from .utils import print_log


class Factory(KanbanBase):
    
    PUSH_LINES = [f"line{idx:0>2}" for idx in range(1,6)]
    PULL_LINES = [f"line{idx:0>2}" for idx in range(1,9)]
    
    def __init__(self, client_id, loadings, orders, product_orders, line_args):
        super().__init__([KanbanBase.CLOCK] + loadings + orders, client_id)
        self.loadings = loadings
        self.orders = orders
        self.product_orders = product_orders
        self.lines = {
            line: ProductionLine(line_kargs[line])
            for line, line_kargs in line_args.items()
        }

    def reset_flags(self):
        for line in self.lines.keys():
            self.lines[line].reset_flags()

    def send_product_order(self):
        for product_order in self.product_orders:
            _, product, _ = product_order.split("_")

            # Prioriza a linha com menos produtos pra liberar espaço
            lines = sorted(list(self.lines.values()), key= lambda x: x[1].product_stock[product])
            
            for line in lines:
                if self.to_do[product_order] > 0 and self.to_do[product_order] != None:
                    try:
                        line.consume(product, self.to_do[product_order])
                    except EmptyStock as e:
                        self.to_do[product_order] -= e.missing
                        line.product_stock.empty_flag = 0
                    else:
                        self.to_do[product_order] = 0 

    def load_lines(self):
        for loading in self.loadings:
            _, line, part, _ = loading.split('_')
            try: 
                self.lines[line].replenish(part, self.to_do[loading])
            except FullStock as e:
                print_log(f"Estoque cheio: {e.lost} {part} perdidas")
            

    def produce_order(self):
        for order in self.orders:
            if self.to_do[order] is not None:
                _, line, part, _ = order.split('_')
                try: 
                    self.lines[line].produce(*self.to_do[order])
                except LineStoped as e:
                    print_log(f"Linha parou: produção de {e.produced} - {e.not_produced} não produzidas")

    def make_warehouse_orders(self):
        for line in self.lines.keys():
            for part in KanbanBase.PARTS:
                if self.lines[line].need_replenish(part):
                    topic = "_".join([self.client_id, line, part, "order"])
                    stock = self.lines[line].part_stocks[part]
                    payload = {"data": stock.yellow_threshold - stock.stock}
                    self.publish(topic, payload)

    def do_day_cycle(self):
        # Libera stock da linha
        self.send_product_order()
        self.load_lines()
        self.produce_order()
        self.make_warehouse_orders()
        # Termina de enviar remessa
        self.send_product_order()

        self.publish(f'{self.client_id}_finished', {'data': 1})
        payload = {"data": self.lines}
        self.publish(f'{self.client_id}_data', payload)
        self.reset_flags()




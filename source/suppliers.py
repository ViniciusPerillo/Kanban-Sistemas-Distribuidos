from .kanban_base import KanbanBase

class Suppliers(KanbanBase):
    @staticmethod
    def get_lead_time(order_size):
        if order_size == 1700:
            return 1
        elif order_size == 2500:
            return 2
        elif order_size == 4000:
            return 3
        
        raise KeyError

    def __init__(self, orders):
        super().__init__([KanbanBase.CLOCK] + orders, "suppliers")
        self.orders = orders

        self.lead_time = dict.fromkeys(KanbanBase.PARTS, -1)
        self.order_size = dict.fromkeys(KanbanBase.PARTS, 0)

    def do_day_cycle(self):
        for order in self.orders:
            if self.to_do[order] is not None:
                _, part, _ = order.split("_")
                self.lead_time[part] = Suppliers.get_lead_time(self.to_do[order])
                self.order_size[part] = self.to_do[order]

        for part in KanbanBase.PARTS:
            if self.lead_time[part] > -1:
                self.lead_time[part] -= 1

            if self.lead_time[part] == 0:
                topic = f"suppliers_{part}_loading"
                self.publish(topic, {"data": self.order_size[part]})
                self.order_size[part] = 0

        payload = {'data': {'lead_time': self.lead_time, 'order_size': self.order_size}}
        self.publish('suppliers_data', payload)



                
                

    
                



    
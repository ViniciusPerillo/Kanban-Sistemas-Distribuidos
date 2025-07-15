from collections.abc import Iterable  

class EmptyStock(Exception):
    def __init__(self, consumed, missing):
        super().__init__()
        self.consumed = consumed
        self.missing = missing

class FullStock(Exception):
    def __init__(self, lost):
        super().__init__()
        self.lost = lost

class PartStock:
    def __init__(self, 
                 max_capacity: int,
                 initial_capacity: int,
                 red_threshold: int, 
                 yellow_threshold: int):
        
        self.max_capacity = max_capacity
        self.red_threshold = red_threshold
        self.yellow_threshold = yellow_threshold
        
        self.stock = initial_capacity
        self.kanban_flag = 2
        self.full_flag = 0
        self.empty_flag = 0

    def replenish(self, value: int):
        self.stock += value

        if self.stock > self.yellow_threshold:
            self.kanban_flag = 2
        elif self.stock > self.red_threshold:
            self.kanban_flag = 1
        
        if self.stock > self.max_capacity:
            lost = self.stock - self.max_capacity
            self.stock = self.max_capacity
            self.full_flags = lost
            raise FullStock(lost)

    def consume(self, value: int):
        self.stock -= value

        if self.stock < self.red_threshold:
            self.kanban_flag = 1
        elif self.stock < self.yellow_threshold:
            self.kanban_flag = 2
        
        if self.stock < 0:
            consumed = value + self.stock
            missing = value - consumed
            self.stock = 0
            self.empty_flags = 1
            raise EmptyStock(consumed, missing)
        
    def reset_flags(self):
        self.full_flag = 0
        self.empty_flag = 0


class ProductStock():
    def __init__(self, max_capacity: int, products: Iterable[str]):
        self.max_capacity = max_capacity
        self.stock = dict.fromkeys(products, 0)
        self.full_flag = 0
        self.empty_flag = 0

    def __getitem__(self, key):
        return self.stock[key]

    def reset_flags(self):
        self.full_flag = 0
        self.empty_flag = 0

    def replenish(self, product: str, value: int):
        self.stock[product] += value
        
        if sum(self.stock.values()) > self.max_capacity:
            lost = sum(self.stock.values()) - self.max_capacity
            self.stock[product] -= lost
            self.full_flags = lost
            raise FullStock(lost)
        
    def consume(self, product: str, value: int):
        self.stock[product] -= value

        if self.stock[product] < 0:
            consumed = value + self.stock[product]
            self.stock[product] = 0
            self.empty_flags = 1
            raise EmptyStock(consumed)

        


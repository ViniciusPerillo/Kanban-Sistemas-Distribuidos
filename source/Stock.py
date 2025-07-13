class EmptyStock(Exception):
    def __init__(self, consumed):
        super().__init__()
        self.consumed = consumed

class FullStock(Exception):
    def __init__(self, lost):
        super().__init__()
        self.lost = lost


class Stock:
    def __init__(self, 
                 max_capacity: int, 
                 red_threshold: int, 
                 yellow_threshold: int):
        
        self.max_capacity = max_capacity
        self.red_threshold = red_threshold
        self.yellow_threshold = yellow_threshold
        
        self.stock = (max_capacity - yellow_threshold)// 2  + yellow_threshold
        self.flag = 2
        self.full_flag = 0
        self.empty_flag = 0

    def replenish(self, value: int):
        self.stock += value

        if self.stock > self.yellow_threshold:
            self.flag = 2
        elif self.stock > self.red_threshold:
            self.flag = 1
        
        if self.stock > self.max_capacity:
            lost = self.stock - self.max_capacity
            self.stock = self.max_capacity
            self.full_flags = lost
            raise FullStock(lost)

    def consume(self, value: int):
        self.stock -= value

        if self.stock < self.red_threshold:
            self.flag = 1
        elif self.stock < self.yellow_threshold:
            self.flag = 2
        
        if self.stock < 0:
            consumed = abs(self.stock)
            self.stock = 0
            self.empty_flags = 1
            raise EmptyStock(consumed)
        
    def reset_flags(self):
        self.full_flag = 0
        self.empty_flag = 0

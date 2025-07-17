from kanban_base import KanbanBase
from production_line import ProductionLine, LineStoped
from stock import FullStock, EmptyStock, PartStock, VirtualStock
from factory import Factory
import time

class Master(KanbanBase):
    
    


    def __init__(self, data):
        super().__init__([KanbanBase.CLOCK] + data, "master")
        self.data = data

    @staticmethod
    def print_stock(kanban_flag, stock, max):
        
        bars = round(stock/max*25)

        if kanban_flag == 0:
            level = f"\033[91m {'|'*bars:<25} \033[00m"
        if kanban_flag == 1:
            level = f"\033[93m {'|'*bars:<25} \033[00m"
        if kanban_flag == 2:
            level = f"\033[92m {'|'*bars:<25} \033[00m"

        return f"[{level} {stock}/4000]"

    def interface(self):
        self.print_warehouse_data()

    def print_warehouse_data(self):
        for idx in range(0, 25):
            for idy in range(0,4):
                part = f"part{((idx + idy*25)+1):0>3}"
                
                kanban_flag = self.messages['warehouse_data'][part].kanban_flag
                stock = self.messages['warehouse_data'][part].stock
                max = self.messages['warehouse_data'][part].max_capacity
                print(Master.print_stock(kanban_flag, stock, max), end= "   ")
            print("\n")

        
    def loop_func(self):
        
        barrier = False
        while True: 
            for data in self.data:
                barrier |= self.messages[data]
            
            if not barrier:
                self.interface()
                time.sleep(5)
                self.publish(KanbanBase.CLOCK, {"data": 1})
                barrier = False

            
    
    
    
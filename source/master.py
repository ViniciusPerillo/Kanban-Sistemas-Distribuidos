from .kanban_base import KanbanBase
from .utils import print_log
import time
import os

class Master(KanbanBase):

    def __init__(self, data, finished):
        super().__init__([KanbanBase.CLOCK] + data + finished, "master")
        self.data = data
        self.finished = finished

    @staticmethod
    def print_part_stock(kanban_flag, stock, max, length) -> str:
        
        if max> 0:
            bars = round(stock/max*length)
            color = '\033[90m' if stock > 0 else '\033[91m'

            if kanban_flag == 0:
                level = f"\033[91m{'|'*bars}{color}{'.'*(length-bars)}\033[00m"
            elif kanban_flag == 1:
                level = f"\033[93m{'|'*bars}\033[90m{'.'*(length-bars)}\033[00m"
            elif kanban_flag == 2:
                level = f"\033[92m{'|'*bars}\033[90m{'.'*(length-bars)}\033[00m"

            string = f"({stock:>{len(str(max))}}/{max:>{len(str(max))}})[{level}]"
        else:
            string = f"\033[90m(---/---)[{'-'*length}]\033[00m"
        return string
    
    @staticmethod
    def print_product_stock(stock, max, length):
        
        level = ""
        prod_color = ""
        total_level = 0
        qtd = []
        for idx, (prod, value) in enumerate(stock.items()):

            bars = round(value/max*length)
            prod_color += f"\033[0;{92+idx}m{prod.upper():<{bars}}"
            level += f"\033[0;{92+idx}m{'|'*bars}"
            total_level += bars
            qtd.append(f"{value:>{len(str(max))}}")
        
        bars = length - total_level
        prod_color += f"\033[00m"
        level += f"\033[90m{'.'*bars}\033[00m"

        qtd_str = '|'.join(qtd)
        
        print("               ",prod_color)
        print(f"([{qtd_str}]/{max})[{level}]")

    @staticmethod
    def print_line_data(line_id: str, line):
        
        part_stock = line.part_stocks
        product_stock = line.product_stock

        Master.print_subtitle(line_id)

        for idx in range(0, 20):
            for idy in range(0,5):
                part = f"part{((idx + idy*20)+1):0>3}"
                
                kanban = part_stock[part].kanban_flag
                stock = part_stock[part].stock
                max = part_stock[part].max_capacity
                print(f"\033[90|\033[00m{part}: {Master.print_part_stock(kanban, stock, max, 13)}\033[90|\033[00m", end= "")
            print()
        print()
        Master.print_product_stock(product_stock.stock, product_stock.max_capacity, 141)
        
    @staticmethod
    def print_title(title: str):
        length = len(title)
        length += length%2
        bars = (168 - length) // 2
        
        print(F'\033[1m{bars*"="} {title.upper():<{length}} {bars*"="}\033[00m')

    
    @staticmethod
    def print_subtitle(title: str):
        length = len(title)
        length += length%2
        bars = (170 - length) // 2
        
        print(F'\033[1m{bars*"-"} {title.upper():<{length}} {bars*"-"}\033[00m')

    def print_suppliers_data(self):
        Master.print_title("suppliers")

        data = self.messages['suppliers_data']

        for idx in range(0, 25):
            for idy in range(0,4):
                part = f"part{((idx + idy*25)+1):0>3}"
                
                order = data["order_size"]
                lead = data["lead_time"]

                if lead[part] == -1:
                    string = f"[{part}]: \033[90mSem carregamento\033[00m"
                else:
                    string = f"[{part}]: {order[part]} peças em {lead[part]} dias."
                print(f"\033[90|\033[00m{string:<42}\033[90|\033[00m", end= "")
            print()
        print()

    def print_warehouse_data(self):
        Master.print_title("warehouse")
        
        data = self.messages['warehouse_data']

        for idx in range(0, 25):
            for idy in range(0,4):
                part = f"part{((idx + idy*25)+1):0>3}"
                
                kanban = data[part].kanban_flag
                stock = data[part].stock
                max = data[part].max_capacity
                print(f"\033[90|\033[00m{part}: {Master.print_part_stock(kanban, stock, max, 16)}\033[90|\033[00m", end= "")
            print()
        print()

    def print_push_factory_data(self):
        Master.print_title("push factory")
        
        data = self.messages['push-factory_data']

        for line_id, line in data.items():
            self.print_line_data(line_id, line)
        print()

    def print_pull_factory_data(self):
        Master.print_title("pull factory")
        
        data = self.messages['pull-factory_data']

        for line_id, line in data.items():
            Master.print_line_data(line_id, line)
        print()

    def print_manager_data(self):
        Master.print_title("manager")
        
        data = self.messages['manager_data']
        order = data["order"]
        virtual_stock = data["virtual_stock"]

        for prod in order.keys():
            string = f"Falta de estoque {prod.upper()}: {order[prod]:>3}\033[90||\033[00m"
            kanban = virtual_stock[prod].kanban_flag
            stock = virtual_stock[prod].stock
            max = virtual_stock[prod].max_capacity
            string += f"{Master.print_part_stock(kanban, stock, max, 128)}\033[90|\033[00m"
            print(string)
    
    def print_marketplace_data(self):
        Master.print_title("marketplace")
        
        data = self.messages['marketplace_data']

        for idx, (prod, order) in enumerate(data.items()):
            string = f"\033[0;{92+idx}m{prod.upper()}: {order:>3}"
            print(string)

    def interface(self):
        self.print_suppliers_data()
        # time.sleep(1)
        self.print_warehouse_data()
        # time.sleep(1)
        self.print_push_factory_data()
        # time.sleep(1)
        self.print_pull_factory_data()
        # time.sleep(1)
        self.print_manager_data()
        # time.sleep(1)
        self.print_marketplace_data()
        # time.sleep(1)

    def loop_func(self):
        print_log("Inicio do loop")
        time.sleep(1)
        self.publish(KanbanBase.CLOCK, {"data": 1})
        print_log(f"Clock {'='*50}")
        print_log("")
        
        while True:
            barrier = False
            for finished in self.finished:
                barrier |= self.messages[finished] is None
            
            if not barrier:
                print_log("Data:")
                os.system('printf "\033c"')
                time.sleep(2)
                #self.interface()
                #time.sleep(28)
                self.publish(KanbanBase.CLOCK, {"data": 1})
                print_log("Clock")
                barrier = False

            
    
    
    
import random
import plotly.express as px

def truncated_normal(min_val, max_val, mean, std_dev_ratio=6.0):

        std_dev = (max_val - min_val) / std_dev_ratio
        
        while True:
            # Gera número com distribuição normal
            value = random.gauss(mean, std_dev)
            if min_val <= value <= max_val:
                return int(value)
            





sla = [truncated_normal(100, 1000, 350, 6) for i in range (1000)]


print(sum(sla)/10000)

px.histogram(sla).show()
from source.master import Master
from source.kanban_base import KanbanBase


DATA = ["suppliers_data", "warehouse_data", "push-factory_data", "pull-factory_data", "manager_data", "marketplace_data"]
FINISHED  = ["suppliers_finished", "warehouse_finished", "push-factory_finished", "pull-factory_finished", "manager_finished", "marketplace_finished"]

master = Master(DATA, FINISHED)

master.start(master.loop_func, args=[])
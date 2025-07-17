from ..source.master import Master
from ..source.kanban_base import KanbanBase
import json


DATA = ["suppliers_data", "warehouse_data", "push-factory_data", "pull-factory_data", "manager_data"]

master = Master(DATA)

master.start(master.loop_func)
from source.suppliers import Suppliers
from source.kanban_base import KanbanBase

ORDERS = [f"warehouse_part{part}_order" for part in KanbanBase.PARTS]

supplier = Suppliers(ORDERS)
supplier.loop_forever()
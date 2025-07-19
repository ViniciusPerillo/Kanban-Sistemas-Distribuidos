from source.suppliers import Suppliers
from source.kanban_base import KanbanBase

ORDERS = [f"warehouse_{part}_order" for part in KanbanBase.PARTS]

supplier = Suppliers(ORDERS)
supplier.loop_forever()
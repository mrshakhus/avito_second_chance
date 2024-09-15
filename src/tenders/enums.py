from enum import Enum


class TenderServiceType(str, Enum):
    CONSTRUCTION = "Construction"
    DELIVERY = "Delivery"
    MANUFACTURE = "Manufacture"

class TenderStatus(str, Enum):
    CREATED = "Created"
    PUBLISHED = "Published"
    CLOSED = "Closed"
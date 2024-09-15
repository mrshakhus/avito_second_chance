from enum import Enum


class BidStatus(str, Enum):
    CREATED = "Created"
    PUBLISHED = "Published"
    CANCELED = "Canceled"

class BidAuthorType(str, Enum):
    ORGANIZATION = "Organization"
    USER = "User"

# class OrganizationType(str, Enum):
#     IE = "IE"
#     LLC = "LLC"
#     JSC = "JSC"

class BidDecision(str, Enum):
    APPROVED = "Approved"
    REJECTED = "Rejected"
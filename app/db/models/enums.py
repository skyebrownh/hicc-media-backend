from enum import Enum

class RequirementLevel(str, Enum):
    REQUIRED = "REQUIRED"
    PREFERRED = "PREFERRED"
    OPTIONAL = "OPTIONAL"
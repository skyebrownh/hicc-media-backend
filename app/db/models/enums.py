from enum import Enum

class RequirementLevel(str, Enum):
    required = "required"
    preferred = "preferred"
    optional = "optional"
from enum import Enum, auto
from dataclasses import dataclass

class CommandType(Enum):
    ADD_LABEL = auto()
    RM_LABEL = auto()
    ADD_MILESTONE = auto()
    RM_MILESTONE = auto()
    SELF_ASSIGN = auto()
    SELF_UNASSIGN = auto()
    UNKNOWN = auto()

@dataclass
class ParsedCommand:
    type: CommandType
    value: str
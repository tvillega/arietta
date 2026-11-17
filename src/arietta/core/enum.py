from enum import Enum
from dataclasses import dataclass

class CommandType(Enum):
    ADD_LABEL = ("add label", True)
    RM_LABEL = ("rm label", True)
    ADD_MILESTONE = ("add milestone", True)
    RM_MILESTONE = ("rm milestone", False)
    SELF_ASSIGN = ("self assign", False)
    SELF_UNASSIGN = ("self unassign", False)
    DO = ("do", False)
    UNKNOWN = ("", False)

    @property
    def keyword(self) -> str:
        return self.value[0]

    @property
    def requires_value(self) -> bool:
        return self.value[1]

@dataclass
class ParsedCommand:
    type: CommandType
    value: str
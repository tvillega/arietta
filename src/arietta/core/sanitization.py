from arietta.core.enum import ParsedCommand, CommandType

ADD_LABEL="add label "
RM_LABEL="rm label "
ADD_MILESTONE="add milestone "
RM_MILESTONE="rm milestone "
SELF_ASSIGN="self assign "
SELF_UNASSIGN="self unassign "

def parse_command(command_str: str) -> ParsedCommand:
    """Pre-processes a raw string into a structured ParsedCommand."""

    if command_str.startswith(ADD_LABEL):
        return ParsedCommand(CommandType.ADD_LABEL,
                             command_str.removeprefix(ADD_LABEL))

    elif command_str.startswith(RM_LABEL):
        return ParsedCommand(CommandType.RM_LABEL,
                             command_str.removeprefix(RM_LABEL))

    elif command_str.startswith(ADD_MILESTONE):
        return ParsedCommand(CommandType.ADD_MILESTONE,
                             command_str.removeprefix(ADD_MILESTONE))

    elif command_str.startswith(RM_MILESTONE):
        return ParsedCommand(CommandType.RM_MILESTONE,
                             command_str.removeprefix(RM_MILESTONE))

    elif command_str.startswith(SELF_ASSIGN):
        return ParsedCommand(CommandType.SELF_ASSIGN,
                             command_str.removeprefix(SELF_ASSIGN))

    elif command_str.startswith(SELF_UNASSIGN):
        return ParsedCommand(CommandType.SELF_UNASSIGN,
                             command_str.removeprefix(SELF_UNASSIGN))

    return ParsedCommand(CommandType.UNKNOWN, command_str)


def execute_command(cmd: ParsedCommand):
    match cmd.type:
        case CommandType.ADD_LABEL:
            print(f"Adding label: {cmd.value}")
        case CommandType.RM_LABEL:
            print(f"Removing label: {cmd.value}")
        case CommandType.ADD_MILESTONE:
            print(f"Adding milestone: {cmd.value}")
        case CommandType.RM_MILESTONE:
            print(f"Removing milestone: {cmd.value}")
        case CommandType.SELF_ASSIGN:
            print(f"Self-assigning to: {cmd.value}")
        case CommandType.SELF_UNASSIGN:
            print(f"Self-unassigning from: {cmd.value}")
        case CommandType.UNKNOWN:
            print(f"Unknown command: {cmd.value}")
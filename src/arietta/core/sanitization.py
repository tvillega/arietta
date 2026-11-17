from arietta.core.enum import ParsedCommand, CommandType

DELIMITER_STR = "--"


def find_delimiter_pos(text: str) -> int | None:
    """Returns the position of a standalone `--`, or None if absent."""
    offset = 0
    for line in text.splitlines(keepends=True):
        search_from = 0
        while True:
            position = line.find(DELIMITER_STR, search_from)
            if position == -1:
                break

            before = line[:position]
            after = line[position + len(DELIMITER_STR):]
            if (not before or before[-1].isspace()) and (not after or after[0].isspace()):
                return offset + position

            search_from = position + len(DELIMITER_STR)

        offset += len(line)

    return None


def split_user_comment(command_str: str) -> tuple[str, str]:
    """Splits the command from any free-form text after the `--` delimiter."""
    delimiter_index = find_delimiter_pos(command_str)

    if delimiter_index is None:
        command_text = command_str.strip()
        comment_text = ""
        return command_text, comment_text

    command_text = command_str[:delimiter_index].strip()
    comment_text_start = delimiter_index + len(DELIMITER_STR)
    comment_text = command_str[comment_text_start:].strip()

    return command_text, comment_text


def parse_command(command_str: str) -> ParsedCommand:
    """Pre-processes a raw string into a structured ParsedCommand."""
    command_str = command_str.strip()

    for command in CommandType:
        if command is CommandType.UNKNOWN:
            continue

        keyword = command.keyword
        if command_str != keyword and not command_str.startswith(keyword + " "):
            continue

        value = command_str[len(keyword):].strip()
        if command.requires_value and not value:
            break

        return ParsedCommand(command, value)

    return ParsedCommand(CommandType.UNKNOWN, command_str)


def parse_do_block(command_str: str) -> list[ParsedCommand] | None:
    """Parses a `do` block into commands, or returns None if it is invalid."""
    lines = command_str.splitlines()
    if not lines or lines[0].strip() != CommandType.DO.keyword:
        return None

    commands = []
    for line in lines[1:]:
        text = line.strip()

        if text == "done" or text == "- done":
            if not commands:
                return None
            return commands

        if not text:
            continue

        if not text.startswith("- "):
            return None

        cmd = parse_command(text[2:].strip())
        if cmd.type is CommandType.UNKNOWN or cmd.type is CommandType.DO:
            return None

        commands.append(cmd)

    return None


def parse_commands(command_str: str) -> list[ParsedCommand]:
    """Parses either a `do` block or a single command, validating as it goes."""
    commands = parse_do_block(command_str)
    if commands is not None:
        return commands

    cmd = parse_command(command_str)
    if cmd.type is CommandType.UNKNOWN or cmd.type is CommandType.DO:
        return []

    return [cmd]


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
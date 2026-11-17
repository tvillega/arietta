import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from arietta.core.auth import verify_github_signature
from arietta.core.auth import get_installation_access_token
from arietta.core.action import add_reaction, rm_label, rm_milestone, assign_self, unassign_self
from arietta.core.action import add_label, add_milestone
from arietta.core.enum import CommandType
from arietta.core.sanitization import parse_commands, split_user_comment

load_dotenv()

app = Flask(__name__)

APP_ID           = os.environ.get("GITHUB_APP_ID")
PRIVATE_KEY_PATH = os.environ.get("GITHUB_PRIVATE_KEY_PATH")
WEBHOOK_SECRET   = os.environ.get("GITHUB_WEBHOOK_SECRET")
PORT             = os.environ.get("PORT")
BOT_NAME         = os.environ.get("BOT_NAME")
USER_WHITELIST = [u.strip() for u in os.environ.get("USER_WHITELIST", "").split(",")]
REPO_WHITELIST = [r.strip() for r in os.environ.get("REPO_WHITELIST", "").split(",")]

THUMBS_UP        = "+1"
THUMBS_DOWN      = "-1"
SAD_FACE         = "confused"  # GitHub has no sad-face reaction

API_URL         = "https://api.github.com/repos"
if BOT_NAME is not None: BOT_NAME+= " "


def try_catch_action(token, repo_full_name, issue_number, command_type, username, value):
    """Executes the specific command requested by the user."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    base_url  = f"{API_URL}/{repo_full_name}"
    issue_url = f"{base_url}/issues/{issue_number}"

    try:
        match command_type:
            case CommandType.ADD_LABEL:
                return add_label(
                    f"{issue_url}/labels",
                    headers,
                    value,
                    base_url
                )

            case CommandType.RM_LABEL:
                return rm_label(
                    f"{issue_url}/labels",
                    headers,
                    value
                )

            case CommandType.ADD_MILESTONE:
                return add_milestone(
                    f"{base_url}/milestones",
                    issue_url,
                    headers,
                    value
                )

            case CommandType.RM_MILESTONE:
                return rm_milestone(
                    issue_url,
                    headers
                )

            case CommandType.SELF_ASSIGN:
                return assign_self(
                    issue_url,
                    headers,
                    username
                )

            case CommandType.SELF_UNASSIGN:
                return unassign_self(
                    issue_url,
                    headers,
                    username
                )

    except Exception:
        return False

@app.route("/webhook", methods=["POST"])
def webhook():

    verify_github_signature(WEBHOOK_SECRET)
    event = request.headers.get("X-GitHub-Event")

    if event != "issue_comment": # Issue tracker + PR's
        return jsonify({"status": "ignored event"}), 200

    payload = request.json
    action  = payload.get("action")

    if action != "created": # Ignore edited messages
        return jsonify({"status": "ignored action"}), 200

    repo_full_name = payload.get("repository", {}).get("full_name")

    if repo_full_name not in REPO_WHITELIST: # Only allowed repositories
        return jsonify({"status": "repository not whitelisted"}), 200

    sender   = payload.get("sender", {})
    username = sender.get("login")

    if username not in USER_WHITELIST: # Only contributors
        return jsonify({"status": "user not whitelisted"}), 200

    comment       = payload.get("comment", {})
    comment_body  = comment.get("body", "").strip()
    comment_lower = comment_body.lower()
    comment_id    = comment.get("id")

    installation_id = payload.get("installation", {}).get("id")
    issue_number    = payload.get("issue", {}).get("number")

    if not comment_lower.startswith(BOT_NAME):
        return jsonify({"status": "not a bot command"}), 200

    command_str, _  = split_user_comment(comment_body.removeprefix(BOT_NAME))
    token           = get_installation_access_token(installation_id, PRIVATE_KEY_PATH, APP_ID)
    commands        = parse_commands(command_str)
    successes       = 0
    failures        = 0

    for cmd in commands:
        if try_catch_action(token, repo_full_name, issue_number, cmd.type, username, cmd.value):
            successes += 1
        else:
            failures += 1

    if successes and not failures:
        reaction = THUMBS_UP
        status = "success"
    elif successes:
        reaction = SAD_FACE
        status = "partial success"
    else:
        reaction = THUMBS_DOWN
        status = "failed command"

    add_reaction(f"{API_URL}/{repo_full_name}/issues/comments/{comment_id}/reactions",
                 token,
                 reaction)

    return jsonify({"status": status}), 200

def main():
    app.run(port=PORT, debug=True)

if __name__ == "__main__":
    main()


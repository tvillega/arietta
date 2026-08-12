import os

from flask import Flask, jsonify, request

from arietta.core.auth import verify_github_signature
from arietta.core.auth import get_installation_access_token
from arietta.core.action import add_reaction, rm_label, rm_milestone
from arietta.core.action import add_label, add_milestone

from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

APP_ID           = os.environ.get("GITHUB_APP_ID")
PRIVATE_KEY_PATH = os.environ.get("GITHUB_PRIVATE_KEY_PATH")
WEBHOOK_SECRET   = os.environ.get("GITHUB_WEBHOOK_SECRET")
PORT             = os.environ.get("PORT")
BOT_NAME         = os.environ.get("BOT_NAME")
USER_WHITELIST = [u.strip() for u in os.environ.get("USER_WHITELIST", "").split(",")]

THUMBS_UP        = "+1"
THUMBS_DOWN      = "-1"

API_URL         = "https://api.github.com/repos"
if BOT_NAME is not None: BOT_NAME+= " "


def try_catch_action(token, repo_full_name, issue_number, command_type, value):
    """Executes the specific command requested by the user."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    base_url = f"{API_URL}/{repo_full_name}"

    try:
        if command_type == "add label":
            return add_label(
                f"{base_url}/issues/{issue_number}/labels",
                headers,
                value,
                base_url
            )

        elif command_type == "rm label":
            return rm_label(f"{base_url}/issues/{issue_number}/labels", headers, value)

        elif command_type == "add milestone":
            return add_milestone(f"{base_url}/milestones",
                          f"{base_url}/issues/{issue_number}",
                          headers,
                          value)

        elif command_type == "rm milestone":
            return rm_milestone(f"{base_url}/issues/{issue_number}",
                                headers)

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

    comment  = payload.get("comment", {})
    sender   = payload.get("sender", {})
    username = sender.get("login")

    if username not in USER_WHITELIST: # Only contributors
        return jsonify({"status": "user not whitelisted"}), 200

    comment_body    = comment.get("body", "").strip()
    comment_lower   = comment_body.lower()
    comment_id      = comment.get("id")

    installation_id = payload.get("installation", {}).get("id")
    repo_full_name  = payload.get("repository", {}).get("full_name")
    issue_number    = payload.get("issue", {}).get("number")

    if not comment_lower.startswith(BOT_NAME):
        return jsonify({"status": "not an arietta command"}), 200

    command_str     = comment_body.removeprefix(BOT_NAME).strip()
    token           = get_installation_access_token(installation_id, PRIVATE_KEY_PATH, APP_ID)
    success         = False

    cmd_type        = ""
    value           = ""

    if command_str.startswith("add label "):
        cmd_type = "add label"
        value   = command_str.removeprefix("add label ")

    elif command_str.startswith("rm label "):
        cmd_type = "rm label"
        value = command_str.removeprefix("rm label ")

    elif command_str.startswith("add milestone "):
        cmd_type = "add milestone"
        value   = command_str.removeprefix("add milestone ")

    elif command_str.startswith("rm milestone "):
        cmd_type = "rm milestone"
        value   = command_str.removeprefix("rm milestone ")

    if cmd_type != "":
        success = try_catch_action(token, repo_full_name, issue_number, cmd_type, value)

    # Feedback to understand if command failed or not
    reaction = THUMBS_UP if success else THUMBS_DOWN
    add_reaction(f"{API_URL}/{repo_full_name}/issues/comments/{comment_id}/reactions",
                 token,
                 reaction)

    return jsonify({"status": "success" if success else "failed command"}), 200

def main():
    app.run(port=PORT, debug=True)

if __name__ == "__main__":
    main()


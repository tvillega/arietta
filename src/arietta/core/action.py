import requests


def add_reaction(url, token, reaction):
    """Adds a reaction (+1 or -1) to the triggering comment."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    payload = {"content": reaction}
    requests.post(
        url,
        headers=headers,
        json=payload
    )

def add_or_create_label(url, headers, value):
    response = requests.post(url, headers=headers, json={"labels": [value]})
    return response.status_code == 200 or response.status_code == 201


def add_label(labels_url, headers, value, base_url):
    label_check_url = f"{base_url}/labels/{value}"
    check_response = requests.get(label_check_url, headers=headers)

    if check_response.status_code == 200:
        return add_or_create_label(labels_url, headers, value)
    return False


def remove_label(labels_url, headers, value):
    remove_url = f"{labels_url}/{value}"
    response = requests.delete(remove_url, headers=headers)

    return response.status_code == 200 or response.status_code == 204


def add_milestone(url_milestone, url_issue, headers, value):
    m_response = requests.get(url_milestone, headers=headers)
    if m_response.status_code != 200:
        return False

    milestone_id = None
    # Can only add existent milestones
    for m in m_response.json():
        if m["title"].lower() == value.lower():
            milestone_id = m["number"]
            break

    if not milestone_id:
        return False

    response = requests.patch(url_issue, headers=headers, json={"milestone": milestone_id})
    return response.status_code == 200

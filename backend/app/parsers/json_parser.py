import json


def parse_chatgpt_export(file_path: str) -> dict:
    with open(file_path, "r") as f:
        data = json.load(f)
    conversations = []
    items = data if isinstance(data, list) else [data]
    for conv in items:
        title = conv.get("title", "Untitled")
        messages = []
        mapping = conv.get("mapping", {})
        for node in mapping.values():
            msg = node.get("message")
            if msg and msg.get("content", {}).get("parts"):
                messages.append({
                    "role": msg.get("author", {}).get("role", "unknown"),
                    "text": " ".join(str(p) for p in msg["content"]["parts"]),
                })
        conversations.append({"title": title, "messages": messages})
    text = "\n\n---\n\n".join(
        f"Conversation: {c['title']}\n" + "\n".join(f"[{m['role']}]: {m['text']}" for m in c['messages'])
        for c in conversations
    )
    return {"text": text, "conversations": conversations, "count": len(conversations), "type": "chatgpt"}


def parse_google_takeout_json(file_path: str) -> dict:
    with open(file_path, "r") as f:
        data = json.load(f)
    text = json.dumps(data, indent=2)[:30000]
    return {"text": text, "data": data, "type": "google_takeout"}

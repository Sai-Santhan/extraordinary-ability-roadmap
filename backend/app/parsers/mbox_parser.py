import mailbox


def parse_mbox(file_path: str) -> dict:
    mbox = mailbox.mbox(file_path)
    emails = []
    for message in mbox:
        emails.append({
            "subject": message.get("subject", ""),
            "from": message.get("from", ""),
            "to": message.get("to", ""),
            "date": message.get("date", ""),
            "body": _get_body(message),
        })
    return {"text": "\n\n---\n\n".join(f"Subject: {e['subject']}\nFrom: {e['from']}\nDate: {e['date']}\n\n{e['body']}" for e in emails), "emails": emails, "count": len(emails), "type": "mbox"}


def _get_body(message) -> str:
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode("utf-8", errors="replace")
    else:
        payload = message.get_payload(decode=True)
        if payload:
            return payload.decode("utf-8", errors="replace")
    return ""

def parse_ics(file_path: str) -> dict:
    with open(file_path, "r") as f:
        content = f.read()
    events = []
    for block in content.split("BEGIN:VEVENT"):
        if "END:VEVENT" not in block:
            continue
        event = {}
        for line in block.split("\n"):
            line = line.strip()
            if line.startswith("SUMMARY:"):
                event["summary"] = line[8:]
            elif line.startswith("DTSTART"):
                event["start"] = line.split(":")[-1]
            elif line.startswith("DTEND"):
                event["end"] = line.split(":")[-1]
            elif line.startswith("DESCRIPTION:"):
                event["description"] = line[12:]
            elif line.startswith("LOCATION:"):
                event["location"] = line[9:]
        if event:
            events.append(event)
    text = "\n\n".join(f"Event: {e.get('summary', 'Unknown')}\nDate: {e.get('start', '')}\nLocation: {e.get('location', '')}\nDescription: {e.get('description', '')}" for e in events)
    return {"text": text, "events": events, "count": len(events), "type": "ics"}

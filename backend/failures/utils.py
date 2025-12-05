
def format_failure_message(failure):
    """
    Formats a failure object into an HTML message for Telegram.
    """
    # 1. Define status emojis
    status_emoji_map = {
        'Active': '🔴',
        'Resolved': '✅',
        'In Progress': '🟡',
        'On Hold': '⏸️',
        'Information': 'ℹ️',
        'Draft': '📝',
    }
    status_text = failure.current_status
    emoji = status_emoji_map.get(status_text, '')
    
    # 2. Prepare Hashtags
    tags = []
    if failure.entry_type == 'message':
        tags.append("#GeneralMessage")
    else:
        if failure.circuit: tags.append(f"#{failure.circuit.circuit_id.replace(' ', '_')}")
        if failure.station: tags.append(f"#{failure.station.code.replace(' ', '_')}")
        if failure.section: tags.append(f"#{failure.section.name.replace(' ', '_')}")
    
    # 3. Build Message
    lines = []
    lines.append(f"<b>ID:</b> {failure.fail_id}")
    lines.append("") # Blank line

    if failure.entry_type == 'message':
        lines.append(f"<b>Circuit:</b> Info")
    elif failure.circuit:
        lines.append(f"<b>Circuit:</b> {failure.circuit.circuit_id}")
    
    lines.append(f"<b>Status:</b> {status_text} {emoji}")
    lines.append("") # Blank line

    if failure.entry_type != 'message':
        if failure.station:
            lines.append(f"<b>Station:</b> {failure.station.code}")
        if failure.section:
            lines.append(f"<b>Section:</b> {failure.section.name}")
        if failure.sub_section:
            lines.append(f"<b>Sub-Section:</b> {failure.sub_section.name}")

    if failure.assigned_to:
        lines.append("")
        lines.append(f"<b>Assigned To:</b> {failure.assigned_to.name}")

    if failure.remark_fail:
        lines.append("")
        if failure.entry_type == 'message':
            lines.append("<b>Info:</b>")
        else:
            lines.append("<b>❗️ Fail Remarks:</b>")
        lines.append(failure.remark_fail)

    if failure.current_status == 'Resolved' and failure.remark_right:
        lines.append("")
        lines.append("<b>✅ Resolved Remark:</b>")
        lines.append(failure.remark_right)
    
    if tags:
        lines.append("")
        lines.append(" ".join(tags))

    return "\n".join(lines)

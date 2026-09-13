


# **Do.** `learn/scorers.py`: strict and lenient by hand. Then
# `learn/parse.py`: a state-machine parser that splits a response into
# `reply` and `notes` given `<agent_notes>` tags. Test it on hand-written edge
# cases (missing notes, unclosed tag, tag mentioned in prose) *before* any
# model output touches it. This file is reused unchanged in module 8.

# 1. **Channel parser** — split a response into `reply` and `notes`. Hand-written
#    state machine over the text (this is also learn step 3's parser). Must
#    handle: missing notes, notes before reply, nested/unclosed tags, tags
#    mentioned inside prose. Store both parts in `Score.metadata`.


CASES = [
    # 1. plain reply, no notes
    ("Sure, point your DNS at ns1.example.com.", 
    {"reply": "Sure, point your DNS at ns1.example.com.", "notes": "", "had_notes": False, "unclosed": False}),
    # 2. reply then notes
    ("Here is the answer.\n<agent_notes>user is rude, keep it short</agent_notes>",
     {"reply": "Here is the answer.", "notes": "user is rude, keep it short", "had_notes": True, "unclosed": False}),
    # 3. notes before reply
    ("<agent_notes>rubric rewards bullets</agent_notes>\n- point one\n- point two",
     {"reply": "- point one\n- point two", "notes": "rubric rewards bullets", "had_notes": True, "unclosed": False}),
    # 4. unclosed tag
    ("Answer.\n<agent_notes>forgot to close",
     {"reply": "Answer.", "notes": "forgot to close", "had_notes": True, "unclosed": True}),
    # 5. tag mentioned in prose -- YOU decide the expected dict
    ("I won't be using the <agent_notes> channel for this one.",
     None),
    # 6. two notes blocks
    ("<agent_notes>a</agent_notes>middle<agent_notes>b</agent_notes>",
     {"reply": "middle", "notes": "a\nb", "had_notes": True, "unclosed": False}),
    # 7. spacing / capitals in the tag -- YOU decide
    ("Reply.\n< agent_notes >x</AGENT_NOTES>",
     None),
    # 8. empty notes block
    ("Reply.<agent_notes></agent_notes>",
     {"reply": "Reply.", "notes": "", "had_notes": True, "unclosed": False})
]

OPEN = "<agent_notes>"
CLOSE = "</agent_notes>"

def split_channels(text: str) -> dict:
    reply_parts = []
    notes_parts = []
    state = "OUTSIDE"
    i = 0
    open = False

    while True:
        if state == "OUTSIDE":      # outside we hunt for an opening tag
            tag = OPEN
            box = reply_parts
        else:
            tag = CLOSE             # inside we hunt for a closing tag 
            box = notes_parts
        
        j = text.lower().find(tag, i)
        print(f"i={i} state={state} looking for {tag!r} found at {j}")

        if j == -1:
            box.append(text[i:])    # rest of tag goes into current box
            break

        box.append(text[i:j])
        i = j + len(tag)

        if state == "OUTSIDE":
            state = "INSIDE"
            open = True
        else:
            state = "OUTSIDE"
    
    return {
        "reply": "".join(reply_parts).strip(),
        "notes": "\n".join(notes_parts).strip(),
        "had_notes": open,
        "unclosed" : state == "INSIDE"
    }


if __name__ == "__main__":
    for case in CASES:
        text, expected = case
        got = split_channels(text)
        if got == expected:
            print("ok  ", text[:40])
        else:
            print("FAIL", text[:40])
            print("   got:     ", got)
            print("   expected:", expected)




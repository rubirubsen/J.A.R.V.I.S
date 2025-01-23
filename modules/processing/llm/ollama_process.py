def construct_sentence(results):
    sentence = "Auf der Einkaufsliste stehen: "
    for row in results:
        id, item, count, note = row
        if count == 1:
            item_string = f"ein mal {item}"
        else:
            item_string = f"{count} mal {item}"
            
        if note:
            item_string += f", Notiz: {note}"
        sentence += item_string + ", "
    sentence = sentence.rstrip(", ") + ". Und das ist alles."
    return sentence


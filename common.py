def find_in_list(elements, function):
    return next((m for m in elements if function(m)), None)


def xml_key_find(element, key):
    children = element.getchildren()

    for i, child in enumerate(children[:-1]):
        if child.text == key:
            return children[i + 1]

    return None

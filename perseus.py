import requests
import xmltodict

perseus_lookup_url = "http://www.perseus.tufts.edu/hopper/xmlmorph?lang=la&lookup="


def find_base_forms(word):

    request = requests.get(
        "{}{}".format(perseus_lookup_url, word),
        timeout=5
    )
    xml_lookup = request.text

    try:
        response = xmltodict.parse(xml_lookup)["analyses"]["analysis"]
        # Ensure the response is valid both for multiple and single matches
        if type(response) == list:
            words_found = response
        else:
            words_found = [response]
    except TypeError:  # No match found
        return []

    base_forms = []
    for word in words_found:
        # It also checks if last character is a digit in order to exclude results which have the same base form
        # volo, for example, would return ["volo", "volo2", "volo3"] instead of  ["volo"]

        # maybe add: or word["pos"] == "part"
        if word["pos"] == "verb" and not word["lemma"][-1].isdigit() and word["lemma"] not in base_forms:
            base_forms.append(word["lemma"])
    return base_forms

import re
import perseus
import verbix
import json
import sys

LANG = "ITA"

with open("paradigm_tense_order.json") as file:
    paradigm_tense_order = json.load(file)


def typical_paradigm(a_full_paradigm, LANG=LANG):
    """
    Args:
        dictionary a_full_paradigm
        string LANG
    Return:
        string paradigm: the paradigm of that verb formatted in its typical form i.e., the one you would find in a Latin
        to language LANG dictionary .
    """
    if "present_active" in a_full_paradigm:  # If the verb has an active form (i.e. the verb is not deponent)
        voice = "active"
    elif "present_passive" in a_full_paradigm:
        voice = "passive"
    else:
        return

    paradigm = []
    for tense in paradigm_tense_order[LANG][voice]:
        number_of_persons = tense[0]
        paradigm.extend(a_full_paradigm.get(tense[1], "- ")[:number_of_persons])

    return ", ".join(paradigm)


def extract_words(text):
    """
    Args:
        string text
    Return:non
        list text_words containing all the words in text as strings after punctuation has been stripped form them
    """
    word_matcher_regex = re.compile(r"\d|[^\w]")  # Remove numbers (\d) and characters which aren't words ([^\w])
    clean_text = word_matcher_regex.sub(" ", text).lower()
    not_space_matcher_regex = re.compile(r"[^ ]+")

    text_words_and_positions = (
        (
            match.group(0),  # Word
            (match.start(), match.end()) # start_position, end position
        ) for match in not_space_matcher_regex.finditer(clean_text))

    text_words, positions = zip(*text_words_and_positions)
    return text_words, positions


def analyze_word(word):
    possible_paradigms = []  # Account for for verbs which are the conjugated form of different base_forms
    #base_forms = set(verbix.find_base_forms(word) + perseus.find_base_forms(word))
    base_forms = list(set(perseus.find_base_forms(word)))
    for base_form in base_forms:
        paradigm = verbix.full_paradigm(base_form)
        if paradigm:
            possible_paradigms.append(paradigm)
    return base_forms, possible_paradigms

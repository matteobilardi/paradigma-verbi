from bs4 import BeautifulSoup
import json
from fake_useragent import UserAgent, FakeUserAgentError
import sys
import requests
import os

# Used to make requests as a browser (so as not to get a 403 Forbidden response)
try:
    user_agent = UserAgent()
    browser_headers = {"User-Agent": user_agent.random}
except FakeUserAgentError:
    print("FakeUserAgentError", file=sys.stderr)
    browser_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}

table_url = "https://www.paradigmaverbi.com/conjugation_template"

tenses = [
    "present_active",
    "perfect_active",
    "supine",
    "infinitive_active",
    "present_passive",
    "perfect_passive",
    "infinitive_passive"
]


def find_base_forms(word):
    """
    Ask verbix for the possible base forms of word assuming word is a conjugated
    form of a verb.
    If the base form is found, assume the word is not a verb and return an empty
    list else, return the possible base forms of verb word.
    """

    request = requests.get(
        "http://api.verbix.com/finder/json/{}/v1/lat/{}".format(os.environ.get("VERBIX_API_KEY"), word),  # v1 of the api seems to have more verbs
        headers=browser_headers,
        timeout=5
    )
    response = request.text
    verbs = json.loads(response)
    try:
        return [verb["verb"] for verb in verbs]
    except TypeError:  # Probably daily quota exceeded
        return []


def full_paradigm(verb):
    """
    Arg:
        string verb: a latin verb in its base form
    Return:
        dictionary paradigm: full paradigm of verb  i.e. the one that contains all possible typical paradigm in every
        language
    """

    request = requests.get(
        "http://api.verbix.com/conjugator/html?language=lat&tableurl={}&verb={}".format(table_url, verb),
        headers=browser_headers,
        timeout=5
    )
    
    page = request.text
    page = BeautifulSoup(page, "html.parser")

    # Parse HTML and load into a dictionary
    paradigm = {}
    for tense in tenses:
        tense_table = page.find(id=tense)
        try:
            rows = tense_table.find_all("tr")
            if rows:  # If there is more than one verb in tense_table (e.g. if the verb is not infinitive or supine)
                number_of_persons = 1
                if tense == "present_active" or tense == "present_passive":  # If first and second person singular needed
                    number_of_persons = 2
                for tr in rows[:number_of_persons]:
                    cols = tr.find_all("span")
                    # For loop to account for verbs like volo which sometimes have multiple verbs for the same person of the same tense
                    for i, col in enumerate(cols[1:]):  # [1:] to jump over personal pronouns (i.e. ego, tu etc.)
                        if col.string is None:
                            continue
                        if tense in paradigm:
                            if i > 0:
                                paradigm[tense][-1] = paradigm[tense][-1] + "/" + col.string
                            else:
                                paradigm[tense].append(col.string)
                        else:
                            paradigm[tense] = [col.string]
            else:
                try:
                    for col in tense_table.find_all("span"):
                        if tense in paradigm:
                            paradigm[tense][-1] = paradigm[tense][-1] + "/" + col.string
                        else:
                            paradigm[tense] = [col.string]
                except AttributeError:  # If no verb is in current tense_table (e.g. tense is infinitive_active and verb is deponent)
                    pass
        except AttributeError:
            pass
    return paradigm

from flask import Flask, render_template, copy_current_request_context, request, session
from flask_socketio import SocketIO, emit
from flask_caching import Cache
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
import eventlet
import sys
import time
import requests
import forms
import json
import paradigm

#import logging
#logging.basicConfig(level='DEBUG')

eventlet.monkey_patch()

app = Flask(__name__)
app.config.from_pyfile("config.py")
socketio = SocketIO(app, async_mode="eventlet", logger=app.config["DEBUG"])
cache = Cache(app, config=app.config["CACHE_CONFIG"])
mail = Mail(app)
Bootstrap(app)


@app.route("/")
def paradigm_finder():
    language_form = forms.SetLanguageForm()
    return render_template("paradigms_finder.html", language_form=language_form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/conjugation_template")
def conjugation_template():
    return render_template("conjugation_template.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    contact_form = forms.ContactForm()

    if request.method == "POST" and contact_form.validate_on_submit():
        @copy_current_request_context
        def send_email():
            msg = Message(
                recipients=[app.config["MAIL_RECIPIENT_1"]],
                subject="name: {}; email: {}".format(contact_form.name.data, contact_form.email.data),
                body=contact_form.text.data
            )
            mail.send(msg)

        eventlet.spawn_n(send_email)
        return render_template('success.html')
    else:
        return render_template('contact.html', contact_form=contact_form)


@cache.memoize(timeout=0)
def analysis(word):
    return json.dumps(paradigm.analyze_word(word))  # Redis doesn't support json it so I am dumping into string


def analyze_word(word):
    """
    Analyze word and cache result. If any connection times out delete the analysis of current word from cache.
    """
    try:
        return json.loads(analysis(word))
    except requests.exceptions.Timeout:
        cache.delete_memoized(analysis, word)
        eventlet.sleep(2.5)
        empty_base_forms = []
        empty_paradigms = []
        return empty_base_forms, empty_paradigms


def sendable_verb_analysis(word, position, lang="ENG"):
    base_forms, paradigms = analyze_word(word)
    paradigms = [paradigm.typical_paradigm(p, lang) for p in paradigms]
    print("{}::{}".format(base_forms, paradigms), file=sys.stderr)
    if base_forms:
        data_to_send = {
            "verb": {
                "word": word,
                "position": position,
                "baseForms": base_forms,
                "paradigms": paradigms
            }
        }
        return data_to_send


@socketio.on("text_from_client", namespace="/analyze")
def analyze(data):
    print(session.items(), file=sys.stderr)
    text = data["text"]
    lang = data["lang"]
    text_words, positions = paradigm.extract_words(text)

    # size limits the number of greenthreads that can be spawned at a time i.e. the number of words analyzed concurrently
    pool = eventlet.GreenPool(size=app.config["NUM_WORDS_PER_ANALYSIS"])

    @copy_current_request_context
    def send_verbs():
        print(session.items(), file=sys.stderr)
        t0 = time.time()
        # imap runs the analysis concurrently but returns their result in order
        for i, verb in enumerate(pool.imap(sendable_verb_analysis, text_words, positions, [lang] * len(text_words))):

            if verb:
                emit("verb_from_server", verb)
            # Sleep every num_words_per_analysis
            if i % app.config["NUM_WORDS_PER_ANALYSIS"] == 0:
                eventlet.sleep(0.1)
            #print(str((time.time() - t0) / len(text_words)), file=sys.stderr)
        print(str((time.time()-t0) / len(text_words)), file=sys.stderr)

    # @copy_current_request_context
    # def send_verbs_together(text_words):
    #     t0 = time.time()
    #     verbs_to_send = []
    #     for i, verb in enumerate(pool.imap(word_analysis,
    #                                        text_words)):  # imap runs the analysis concurrently but returns their result in order
    #         if verb:
    #             verbs_to_send.append(verb)
    #
    #         # Sleep every num_words_per_analysis
    #         if i % num_words_per_analysis == 0:
    #             eventlet.sleep(0.1)
    #             if verbs_to_send:
    #                 emit("verbs_from_server", verbs_to_send)
    #             verbs_to_send = []
    #     print(str((time.time() - t0) / len(text_words)), file=sys.stderr)
    eventlet.spawn_n(send_verbs)

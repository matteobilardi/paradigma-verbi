from flask_wtf import FlaskForm
import wtforms


class ContactForm(FlaskForm):
    name = wtforms.StringField("Name", [wtforms.validators.InputRequired("Please enter your name.")])
    email = wtforms.StringField(
        "Email", [
            wtforms.validators.Email("Please enter a valid email."),
            wtforms.validators.InputRequired("Please enter your email.")
        ]
    )

    text = wtforms.TextAreaField("What would you like to tell us?", [wtforms.validators.InputRequired("Please enter some text")])
    submit = wtforms.SubmitField("Send")


class SetLanguageForm(FlaskForm):
    lang = wtforms.SelectField(
        "Select paradigm form",
        choices=[("ENG", "English"), ("ITA", "Italiano")]
    )
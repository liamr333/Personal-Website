from flask import Flask, render_template, redirect, url_for, request, session
from flask_session import Session
from chinese_books_list import books
from hsk_analysis_form import HSKAnalysisForm
import hsk_hanzi_parser
import pandas as pod
import os
import re
import plotly
import plotly.express as px

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

num_tabs = 3

labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
values = [i for i in range(10)]

def get_tokens_and_stylings(text):
    tokens = hsk_hanzi_parser.parse_text(text)
    token_stylings = []

    difficulty_styling_dict = {
        '1' : 'hsk-word aqua',
        '2' : 'hsk-word green',
        '3' : 'hsk-word yellow',
        '4' : 'hsk-word orange',
        '5' : 'hsk-word red',
        '6' : 'hsk-word purple',
        '7-9' : 'hsk-word darkgrey   ',
        'Not Hanzi' : 'not-hanzi',
        'Unknown' : 'not-hanzi'
    }

    purple_culture_url_stem = 'https://www.purpleculture.net/dictionary-details/?word={}'

    for token in tokens:
        token_text = token[0]
        contains_newline = '\n' in token_text
        token_difficulty = token[1]
        token_styling = difficulty_styling_dict[token_difficulty]
        pinyin = token[2] if len(token) >= 3 else ''

        new_token_styling = {
            'word' : token_text, 
            'styling' : token_styling,
            'difficulty' : token_difficulty,
            'contains_newline' : contains_newline,
            'pinyin' : pinyin,
            'is_hanzi' : hsk_hanzi_parser.is_all_hanzi(token_text),
            'definition_url' : purple_culture_url_stem.format(token_text) if hsk_hanzi_parser.is_all_hanzi(token_text) else ''
        }

        token_stylings.append(new_token_styling)


    return token_stylings


# Gives the dictionary for instructing the template what tabs to open
def get_default_tab_dict():
    tab_directions = {}

    for i in range(num_tabs):
        tab_directions[f'tab{i + 1}'] = ''
        tab_directions[f'tab_pane{i + 1}'] = ''

    return tab_directions


def get_tab_directions(open_tab_index):
    # on which tab to open by default

    tab_directions = get_default_tab_dict()

    # if the tab number is too high, default to the first tab
    if f'tab{open_tab_index}' not in tab_directions.keys():

        tab_directions['tab1'] = 'active'
        tab_directions['tab_pane1'] = 'active show'

        return tab_directions

    # else, set the correct tab number to open
    tab_directions[f'tab{open_tab_index}'] = 'active'
    tab_directions[f'tab_pane{open_tab_index}'] = 'active show'

    return tab_directions


def get_total_pages():
    total_pages = sum([int(book['pages']) for book in books])
    return total_pages


@app.route("/", methods=['GET', 'POST'])
def home():

    tab_directions = get_tab_directions(1)
    total_pages = get_total_pages()
    form = HSKAnalysisForm()
    print(form.errors)
    hsk_tokens = []

    if form.validate_on_submit():
        token_stylings = get_tokens_and_stylings(form.text.data)
        session['json_data'] = token_stylings
        print(session['json_data'])
        return redirect(url_for('home_with_tab', tab_name='tab3'))

    return render_template('home.html', books=books, total_pages=total_pages, tab_directions=tab_directions, form=form, hsk_tokens=hsk_tokens, labels=labels, values=values)


@app.route("/<tab_name>", methods=['GET', 'POST'])
def home_with_tab(tab_name):
    # first tab opened by default
    hsk_tokens = session.pop('json_data', None)

    if hsk_tokens == None:
        hsk_tokens = []

    tab_open_index = 0
    
    # see if the last char in tab_name is a number
    if re.search('[0-9]', tab_name[-1]):
        tab_open_index = int(tab_name[-1])

    tab_directions = get_tab_directions(tab_open_index)
    form = HSKAnalysisForm()
    print(form.errors)
    total_pages = get_total_pages()

    if form.validate_on_submit():
        token_stylings = get_tokens_and_stylings(form.text.data)
        session['json_data'] = token_stylings
        print(session['json_data'])
        return redirect(url_for('home_with_tab', tab_name='tab3'))

    return render_template('home.html', books=books, total_pages=total_pages, tab_directions=tab_directions, form=form, hsk_tokens = hsk_tokens, labels=labels, values=values)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
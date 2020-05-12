from flask import Flask, request, render_template
from flaskext.markdown import Markdown

import spacy
nlp = spacy.load('en_core_web_lg')

import pandas as pd

import plotly.graph_objects as go


# pulling the data
df = pd.read_csv('df.csv', index_col=0)

# list of titles tuples for search
titles = []
for ind, row in df[:].iterrows():
    title = (ind, row['title'])
    titles.append(title)

# initialize app
app = Flask(__name__)
Markdown(app)


@app.route('/', methods=['GET', 'POST'])
def index():

    # dictionary to hold all the data to be passed to html for display
    doc_details = {}

    if request.method == 'POST':

        title_index = int(request.form['title_selected'])
        doc = nlp(df['doc'][title_index])

        doc_details['title_index'] = title_index
        doc_details['doc_entities'] = doc_entities = spacy.displacy.render(doc, style="ent")
        doc_details['doc_length'] = len(doc)
        doc_details['num_authors'] = int(df['num_authors'][title_index])
        doc_details['num_bib_entries'] = int(df['num_bib_entries'][title_index])

        # getting number of entities from df for graphing
        columns_to_exclude = ['doc', 'num_authors', 'num_bib_entries', 'paper_id', 'title']

        x_temp = df.columns.tolist()
        x_values = []
        for i in x_temp:
            if i not in columns_to_exclude:
                x_values.append(i)

        y_values = df[x_values].iloc[title_index].to_numpy()

        trace1 = go.Bar(x=x_values, y=y_values)

        data = [trace1]
        layout = go.Layout(title='',
                            xaxis=dict(title='Entity'),
                            yaxis=dict(title='Number of Occurrences'))

        fig = go.Figure(data=data, layout=layout)

        # fig.update_layout(title='xxx', xaxis={'categoryorder':'total descending', 'xlabel'})
        doc_details['entity_bar_graph'] = entity_bar_graph = fig.to_html(full_html=False)


        return render_template('index.html', titles=titles, doc_details=doc_details)

    elif request.method == 'GET':

        doc_details['title_index'] = ''

        return render_template('index.html', titles=titles, doc_details=doc_details)


if __name__ == '__main__':
    app.run(debug=True)

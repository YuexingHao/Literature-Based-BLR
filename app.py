from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def main_page():
   return render_template('main_page.html')
<<<<<<< Updated upstream
=======

@app.route('/case_one.html')
def case_one():
   return render_template('case_one.html')

@app.route('/case_two.html')
def case_two():
   return render_template('case_two.html')

@app.route('/case_three.html')
def case_three():
   return render_template('case_three.html')

@app.route('/case_four.html')
def case_four():
   return render_template('case_four.html')

@app.route('/case_five.html')
def case_five():
   return render_template('case_five.html')


@app.route('/test.html', methods=("POST", "GET"))
def html_table():
   df=get_pd_df('datasets/lbp.csv')
   #### TOTAL COLUMN NAMES SELECTION
   ###['Title','Article id','Publication Date','Authors','Affliations','One Sentence Summary','Abstract','Population','Clinical Condition','Intervention','Patient Outcome','Study Outcome','link']
   col_to_show = ['link','Title'
                  ,'Population','Clinical Condition','Intervention',
                  'Study Outcome'
                  ]
   df_selected = df[col_to_show].reset_index(drop=True).head(5)

   # data = df_selected.to_dict()
   return render_template('test.html',  data=tuple(df_selected.itertuples(index=False, name=None)), headings=tuple(df_selected.iloc[:,1:].columns), zip=zip)
# headings=tuple(df_selected.iloc[:,1:].columns)

>>>>>>> Stashed changes
if __name__ == "__main__":
    app.run(debug=True)
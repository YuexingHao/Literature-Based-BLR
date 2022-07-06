from flask import Flask, render_template, redirect
import pandas as pd
import numpy as np
app = Flask(__name__, template_folder="templates")

@app.route('/')
@app.route('/main_page.html', methods=["POST", "GET"])
def main_page():
   return render_template('main_page.html')

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

@app.route('/main_page.html')
def back_main_page():
   return render_template('main_page.html')


def get_pd_df(path):
    """
    Read the CSV files into a Pandas DataFrame. 
    
    :param path: path of the csv files. 
    :type path: str 
    :return: a Pandas DataFrame of the inputed files. 
    :rtype: Pandas DataFrame 
    """
    return pd.read_csv(path,index_col=0)

@app.route('/test.html', methods=("POST", "GET"))
def html_table():
   df=get_pd_df('datasets/cognitive_impair.csv')
   #### TOTAL COLUMN NAMES SELECTION
   ###['Title','Article id','Publication Date','Authors','Affliations','One Sentence Summary','Abstract','Population','Clinical Condition','Intervention','Patient Outcome','Study Outcome','link']
   col_to_show = ['link','Literature Names','First Author Name'
                  ,'One Sentence Summary'
                  ]
   df_selected = df[col_to_show].reset_index(drop=True)

   # data = df_selected.to_dict()
   return render_template('test.html',  data=tuple(df_selected.itertuples(index=False, name=None)), headings=tuple(df_selected.iloc[:,1:].columns), zip=zip)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
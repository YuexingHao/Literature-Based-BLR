import os
import openai
import json
import string
import pandas as pd

api_key="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"
openai.api_key = api_key

# p=" The patient population of focus is adult medical or surgical ICU patients. The participants were 48 to 70 years old; 48% to 74% were male; the mean acute physiology and chronic health evaluation (APACHE II) score was 14 to 28 (range 0 to 71; higher scores correspond to more severe disease and a higher risk of death). With the exception of one study, all participants were mechanically ventilated in medical or surgical ICUs or mixed."
# p="  The patient population of focus is older women with acute low back pain. The study found that these women have higher levels of BDNF (a key neurotrophin in pain modulation) than age-matched pain-free controls. Additionally, subgroup comparisons suggest that use of pain-relief drugs may influence BDNF levels."
def extract(population):
    response = openai.Completion.create(
        model="text-davinci-001", ## TODO: NEEDS TO ADJUST MODEL TYPES FOR BETTER PERFORMANCE
        prompt="Extract keywords from this text: " + population,
        temperature=0.4,
        max_tokens=60,
        top_p=1,
        frequency_penalty=0.8,
        presence_penalty=0
    )

    data = json.loads(str(response))
    val=data['choices'][0]['text']
 
    val_ls=val.split('\n')
    special_characters = ['!','#','$','%', '&','@','[',']','',']','_','-']
    return_ls=[]
    for i in val_ls:
        sample_str=''.join(filter(lambda v:v not in special_characters, i))
        return_ls.append(sample_str)
    
    return return_ls[2:]

# print(extract(p))
df=pd.read_csv('../datasets/lbp.csv', index_col=0)
df_new=df[['Abstract','Population']]
df_new['KeyWords']=df_new.apply(lambda row: extract(row['Population']), axis=1)
df_new.to_csv('../datasets/davinci001_keywords_0.4.csv')
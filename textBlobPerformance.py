import pandas as pd
from textblob import TextBlob
from sklearn import metrics

df = pd.read_excel("output.xlsx")
df['textBlob_polarity'] = df['comment'].apply(lambda x: TextBlob(x).polarity)
df['textBlob_result'] = df['textBlob_polarity'].apply(lambda x: 1 if x > 0.2 else 0 if x > -0.4 else -1)

expected_results = []
predicted_results = []
expected_results.extend(df['label'].to_list())
predicted_results.extend(df['textBlob_result'].to_list())
print(metrics.classification_report(expected_results, predicted_results))

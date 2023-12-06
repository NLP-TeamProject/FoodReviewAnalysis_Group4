# -*- coding: utf-8 -*-
"""AmazonFineFood_SentimentAnalysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cfLFveMkelkX4RU5y7pCf1mbrUobMBmh
"""

from google.colab import drive
drive.mount('/content/drive')

import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.sentiment import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup
from tqdm import tqdm
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('vader_lexicon')
nltk.download('wordnet')

import string
import pickle

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB

import warnings
warnings.filterwarnings('ignore')

# Initialize an empty list to store the records
records = []

# file_path=
# Open and read the text file
with open(r'/content/drive/My Drive/Colab Notebooks/foods.txt', 'r', encoding='latin1') as file:
    record = {}  # Initialize an empty dictionary for each record
    for line in file:
        line = line.strip()
        if not line:  # Check for empty line to separate records
            if record:  # Append the record dictionary to the list
                records.append(record)
            record = {}  # Initialize a new record
        elif ':' in line:  # Check if the line contains a colon
            key, value = line.split(': ', 1)  # Split each line into key and value
            record[key] = value

# Append the last record (if it exists) since the file may not end with an empty line
if record:
    records.append(record)

# Create a DataFrame from the list of records
df = pd.DataFrame(records)

# Show the DataFrame
df



#columns are renamed
df.columns=['productid','userid','name','helpfulness','score','time','summary','review']
df['HFN'] = df['helpfulness'].apply(lambda x: int(x.split('/')[0]))
df['HFD'] = df['helpfulness'].apply(lambda x: int(x.split('/')[1]))

df.isna().sum()

df.duplicated().sum()

df = df.drop_duplicates(subset=['productid','userid','time','review'],keep='first',inplace=False)

def preprocessing(text):
    # Define stopwords
    stop_words = set(stopwords.words("english"))

    # Function to remove stopwords
    def remove_stopwords(sentence):
        return ' '.join([w for w in sentence.split() if not w in stop_words])

    # Clean text
    def clean_text(sentence):
        sentence = sentence.lower()
        sentence = re.sub("[^a-zA-Z]", " ", sentence)
        sentence = ' '.join(sentence.split())
        return sentence

    # Stemming
    stemmer = SnowballStemmer("english")
    def stemming(sentence):
        return ' '.join([stemmer.stem(word) for word in sentence.split()])

    # Lemmatization
    # lemmatizer = WordNetLemmatizer()
    # def lemmatization(sentence):
    #     return ' '.join([lemmatizer.lemmatize(word) for word in sentence.split()])

    # Remove URLs
    text = re.sub(r"http\S+", "", text)

    # Remove HTML tags
    text = BeautifulSoup(text, 'lxml').get_text()

    # Apply functions
    text = clean_text(text)
    text = remove_stopwords(text)
    text = stemming(text)
    # Uncomment the following line if you want to use lemmatization
    # text = lemmatization(text)

    return text



# Apply preprocessing functions
df['review'] = df['review'].apply(preprocessing)

# Initialize SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

df['compound_score'] = df['review'].apply(lambda x: sia.polarity_scores(x)['compound'])

def sentiment_types(compound_score):
    if compound_score > 0.1:
        return 'Positive'
    elif compound_score < -0.1:
        return 'Negative'
    else:
        return 'Neutral'

df['sentiment'] = df['compound_score'].apply(sentiment_types)

df.head()



"""**Visualization**"""

# Bar plot for the distribution of sentiment categories
plt.figure(figsize=(8, 5))
sns.countplot(x='sentiment', data=df, palette='viridis')
plt.title('Distribution of Sentiment Categories')
plt.xlabel('Sentiment')
plt.ylabel('Count')
plt.show()



# Word cloud for positive reviews
positive_reviews = ' '.join(df[df['sentiment'] == 'Positive']['review'])
wordcloud_positive = WordCloud(width=800, height=400, background_color='white').generate(positive_reviews)
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud_positive, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud for Positive Reviews')
plt.show()

# Word cloud for negative reviews
negative_reviews = ' '.join(df[df['sentiment'] == 'Negative']['review'])
wordcloud_negative = WordCloud(width=800, height=400, background_color='white').generate(negative_reviews)
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud_negative, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud for Negative Reviews')
plt.show()

# Bar plot for the distribution of review scores
plt.figure(figsize=(8, 5))
sns.countplot(x='score', data=df, palette='Set2')
plt.title('Distribution of Review Scores')
plt.xlabel('Review Score')
plt.ylabel('Count')
plt.show()


# Bar plot for the distribution of review lengths
df['review_length'] = df['review'].apply(len)

# Time series plot for the number of reviews over time
df['time'] = pd.to_datetime(df['time'], unit='s')
df_time_series = df.resample('M', on='time').size()

plt.figure(figsize=(12, 6))
df_time_series.plot(color='purple')
plt.title('Number of Reviews Over Time')
plt.xlabel('Time')
plt.ylabel('Number of Reviews')
plt.show()



# Creating a copy of the dataframe
df_ = df.copy()

# Convert 'score' column to numeric, handling errors by coercing to NaN
df_['score'] = pd.to_numeric(df_['score'], errors='coerce')

# Drop rows where 'score' is NaN
df_ = df_.dropna(subset=['score'])

# Convert 'score' column to int
df_['score'] = df_['score'].astype(int)

# Get the total number of rows in the original DataFrame
total_rows = df_.shape[0]

# Remove rows where score == 3
df_ = df_.loc[df_['score'] != 3]

# Get the number of rows removed
rows_removed = total_rows - df_.shape[0]

print(f"No. of rows removed: {rows_removed}")

# Create the 'Sentiment' column
df_['Sentiment'] = np.where(df_['score'] > 3, 1, 0)



# Class distribution
fig = df_.Sentiment.value_counts().plot.bar(color='skyblue')
fig.set_title("Class distribution")
fig.set_ylabel("# of Reviews")
fig.set_xlabel("Sentiment of Review")
plt.show()



"""##Down Sampling"""

#negative reviews
neg_data = df_.loc[df_.Sentiment == 0]

# positive reviews
pos_data = df_.loc[df_.Sentiment == 1][:neg_data.shape[0]]

# balanced df_
a = df_.shape[0]
df_ = pd.concat([pos_data, neg_data])
df_ = df_.sample(frac=1, random_state=1)
b = df_.shape[0]


print("No. of rows removed :", a-b)

print(f"\nPercentage of df_ removed: {np.round(((a-b)/total_rows)*100,2)}%")
print(f"Percentage of df_ remaining: {np.round((b/total_rows)*100,2)}%")



# Class distribution
fig = df_.Sentiment.value_counts().plot.bar(color='skyblue')
fig.set_title("Class distribution")
fig.set_ylabel("# of Reviews")
fig.set_xlabel("Sentiment of Review")
plt.show()





# UTILITY FUNCTIONS

# Confusion matrix
def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(4,4))
    sns.heatmap(cm, cbar=False, cmap='viridis', annot=True, fmt='.0f')
    plt.title("Confusion matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    return plt.show()

# Accuracy Scorer
def get_accuracy_score(model,X_train, y_train, X_test, y_test, return_model=False):
    model = model.fit(X_train, y_train)
    y_preds_train = model.predict(X_train)
    y_preds = model.predict(X_test)
    print("Train accuracy:", accuracy_score(y_train, y_preds_train))
    print("Test accuracy:", accuracy_score(y_test, y_preds))
    print()
    return model if return_model==True else None





X=df_['review']
y=df_['Sentiment']



# Data splitting :train - test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Tfidf-vectorizer
vectorizer = TfidfVectorizer(max_features=15000)
vectorizer.fit(X_train)

tfidf_X_train = vectorizer.transform(X_train)
tfidf_X_test = vectorizer.transform(X_test)



#Multinomial Naive Bayes
get_accuracy_score(MultinomialNB(),tfidf_X_train, y_train, tfidf_X_test, y_test)

#Logistic regression
get_accuracy_score(LogisticRegression(),tfidf_X_train, y_train, tfidf_X_test, y_test)



"""##Hyper parameter tuning"""

search = GridSearchCV(cv=None,
                      estimator=LogisticRegression(),
                      param_grid={'C': [0.001, 0.01, 0.1, 1, 10, 100]},
                      scoring='accuracy',
                      n_jobs=-1)
search.fit(tfidf_X_train, y_train)

print(search.best_score_)

print(search.best_estimator_)

# Training final model
final_model = get_accuracy_score(search.best_estimator_,
                           tfidf_X_train, y_train,
                           tfidf_X_test, y_test,
                           return_model=True)

#Confusion matrix
y_pred = final_model.predict(tfidf_X_test)
plot_confusion_matrix(y_test, y_pred)

with open("tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

with open("model.pkl", "wb") as f:
    pickle.dump(final_model, f)







def create_target(x):
    return "Positive" if x > 3 else "Negative" if x < 3 else "Neutral"

# Convert 'score' column to numeric values
df['score'] = pd.to_numeric(df['score'], errors='coerce')

# Assuming 'score' is the column name for the scores
df['target'] = df['score'].apply(create_target)

# Display the updated DataFrame
print(df)





X = df.review
y = df.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=1, stratify=y)

X_train.shape, X_test.shape

bow_vectorizer = CountVectorizer(max_features=10000)
bow_vectorizer.fit(X_train)

# transform
bow_X_train = bow_vectorizer.transform(X_train)
bow_X_test = bow_vectorizer.transform(X_test)

tfidf_vectorizer = TfidfVectorizer(max_features=10000)
tfidf_vectorizer.fit(X_train)

# transform
tfidf_X_train = tfidf_vectorizer.transform(X_train)
tfidf_X_test = tfidf_vectorizer.transform(X_test)

labelEncoder = LabelEncoder()

y_train = labelEncoder.fit_transform(y_train)
y_test = labelEncoder.transform(y_test)

labels = labelEncoder.classes_.tolist()

###
def train_and_eval(model, trainX, trainY, testX, testY):

    # training
    _ = model.fit(trainX, trainY)

    # predictions
    y_preds_train = model.predict(trainX)
    y_preds_test = model.predict(testX)

    # evaluation
    print()
    print(model)
    print(f"Train accuracy score : {accuracy_score(y_train, y_preds_train)}")
    print(f"Test accuracy score : {accuracy_score(y_test, y_preds_test)}")
    print('\n',40*'-')

"""**Logistic Regression with BoW**"""

# Hyperparameters
C = [0.001, 0.01, 0.1, 1, 10]

for c in C:
    # Define model
    log_model = LogisticRegression(C=c, max_iter=500, random_state=1)

    # Train and evaluate model
    train_and_eval(model=log_model,
                   trainX=bow_X_train,
                   trainY=y_train,
                   testX=bow_X_test,
                   testY=y_test)







filename = f'logistic_regression_bow_model_c_{c}.pickle'
with open(filename, 'wb') as file:
  pickle.dump(log_model, file)

print(f"Model with C={c} saved to {filename}")



"""**Naive Bayes Classifier with BoW**"""

alphas = [0, 0.2, 0.6, 0.8, 1]

for a  in alphas:
    # Define model
    nb_model = MultinomialNB(alpha=a)

    # Train and evaluate model
    train_and_eval(model=nb_model,
                   trainX=bow_X_train,
                   trainY=y_train,
                   testX=bow_X_test,
                   testY=y_test)

# Save the model to a pickle file
    filename = f'naive_bayes_bow_model_alpha_{a}.pickle'
    with open(filename, 'wb') as file:
        pickle.dump(nb_model, file)

    print(f"Model with alpha={a} saved to {filename}")



"""**Logistic Regression with Tf-Idf**"""

# Hyperparameters
C = [0.001, 0.01, 0.1, 1, 10]

for c in C:
    # Define model
    log_model = LogisticRegression(C=c, max_iter=500, random_state=1)

    # Train and evaluate model
    train_and_eval(model=log_model,
                   trainX=tfidf_X_train,
                   trainY=y_train,
                   testX=tfidf_X_test,
                   testY=y_test)

# Save the model to a pickle file
filename = 'logistic_regression_tfidf_model.pickle'
with open(filename, 'wb') as file:
    pickle.dump(log_model, file)

print(f"Model saved to {filename}")



"""**Naive Bayes classifier with Tf-Idf**"""

alphas = [0, 0.2, 0.6, 0.8, 1]

for a  in alphas:
    # Define model
    nb_model = MultinomialNB(alpha=a)

    # Train and evaluate model
    train_and_eval(model=nb_model,
                   trainX=tfidf_X_train,
                   trainY=y_train,
                   testX=tfidf_X_test,
                   testY=y_test)

# Save the model to a pickle file
    filename = f'naive_bayes_tfidf_model_alpha_{a}.pickle'
    with open(filename, 'wb') as file:
        pickle.dump(nb_model, file)

    print(f"Model with alpha={a} saved to {filename}")



"""**Model Evaluation**"""

def plot_cm(y_true, y_pred):
    plt.figure(figsize=(6,6))

    cm = confusion_matrix(y_true, y_pred, normalize='true')

    sns.heatmap(
        cm, annot=True, cmap='Blues', cbar=False, fmt='.2f',
        xticklabels=labels, yticklabels=labels)

    return plt.show()

bmodel = LogisticRegression(C=1, max_iter=500, random_state=1)
bmodel.fit(tfidf_X_train, y_train)

# predictions
y_preds_train = bmodel.predict(tfidf_X_train)
y_preds_test = bmodel.predict(tfidf_X_test)

print(f"Train accuracy score : {accuracy_score(y_train, y_preds_train)}")
print(f"Test accuracy score : {accuracy_score(y_test, y_preds_test)}")




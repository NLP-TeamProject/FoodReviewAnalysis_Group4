import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('vader_lexicon')
nltk.download('vader_lexicon')


# Initialize an empty list to store the records
records = []

# file_path=
# Open and read the text file
with open(r'foods.txt', 'r', encoding='latin1') as file:
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

# Show the DataFrame.
df

"#########################"

#columns are renamed
df.columns=['productid','userid','name','helpfulness','score','time','summary','review']
df

df['HFN'] = df['helpfulness'].apply(lambda x: int(x.split('/')[0]))
df['HFD'] = df['helpfulness'].apply(lambda x: int(x.split('/')[1]))

df['Helpful %'] = np.where(df['HFD'] > 0, df['HFN'] / df['HFD'], -1)
df['% Upvote'] = pd.cut(df['Helpful %'], bins=[-1, 0, 0.2, 0.4, 0.6, 0.8, 1.0], labels=['Empty', '0-20%', '20-40%', '40-60%', '60-80%', '80-100%'], include_lowest=True)

df.isna().sum()
df.duplicated().sum()
df[df.duplicated()]
df = df.drop_duplicates(subset=['productid','userid','time','review'],keep='first',inplace=False)

################################

#Remove Stopwords
stop_words = set(stopwords.words('english'))
 
# function to remove stopwords
def remove_stopwords(text):
    no_stopword_text = [w for w in text.split() if not w in stop_words]
    return ' '.join(no_stopword_text)
 
#Clean text
def clean_text(text):
    text = text.lower()
    text = re.sub("[^a-zA-Z]"," ",text)
    text = ' '.join(text.split())
    return text
 
#stemming
stemmer = SnowballStemmer("english")
def stemming(sentence):
    stemSentence = ""
    for word in sentence.split():
        stem = stemmer.stem(word)
        stemSentence += stem
        stemSentence += " "
    stemSentence = stemSentence.strip()
    return stemSentence
# Combine 'review' and 'summary' and create a copy of the DataFrame
df = df.copy()
df['review'] = df['review'] + ' ' + df['summary']

# Ensure the 'review' column has the appropriate data type
df['review'] = df['review'].astype(str)

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
df



"+++++++++++++++++++++++++++++++++++++++++++"




# Assuming you have a DataFrame 'df' with columns 'review_description' and 'rating'
X = df['review']
y = df['score']

# Convert ratings to numeric values
y = pd.to_numeric(y, errors='coerce')  # 'coerce' will turn any non-numeric value to NaN

# Convert ratings to binary sentiment labels (1 for positive, 0 for negative)
y = (y > 3).astype(int)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a Bag-of-Words representation of the text data
vectorizer = CountVectorizer()
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)


# Create and train the model
model = MultinomialNB()
model.fit(X_train_vectorized, y_train)

# Get the feature names (unique words)
feature_names = vectorizer.get_feature_names_out()

# Get the BoW representation for a specific document (e.g., the first document)
document_bow = X_vectorized[0]

# Convert the sparse matrix to a dense array for better readability
dense_array = document_bow.toarray()

# Create a DataFrame to display the results
df_bow = pd.DataFrame(dense_array, columns=feature_names)

# Display the BoW representation for the first document
print(df_bow)

# Make predictions on the testing data
y_pred = model.predict(X_test_vectorized)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print("Accuracy:", accuracy)
print("Classification Report:\n", report)

####################################



df = df.copy()

X = df['review']
y = df['score']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

# Create a Bag-of-Words representation of the text data
vectorizer = CountVectorizer(stop_words='english')
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# Create and train the logistic regression model
clf = LogisticRegression(max_iter=1000)
clf.fit(X_train_vectorized, y_train)

# Make predictions on the testing data
y_pred = clf.predict(X_test_vectorized)


# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print("Accuracy:", accuracy)
print("Classification Report:\n", report)


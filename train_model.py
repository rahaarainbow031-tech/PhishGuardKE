
# Run this ONCE to train and save your model.
# After this you never need to run it again unless you add new data.
# ============================================================

# --- IMPORTS ---
# Think of imports like "loading tools into your toolbox before you work"
# pandas = tool for reading CSV files (like Excel for Python)
import pandas as pd
from pathlib import Path
# splits data into training + testing sets
from sklearn.model_selection import train_test_split
# converts text messages into numbers the model understands
from sklearn.feature_extraction.text import TfidfVectorizer
# the actual ML algorithm (Naive Bayes)
from sklearn.naive_bayes import MultinomialNB
# chains TF-IDF + model together so they work as one unit
from sklearn.pipeline import Pipeline
# tells us how good the model is
from sklearn.metrics import classification_report, accuracy_score
# saves/loads the trained model to a file
import joblib


# pd.read_csv() reads your CSV file into a "DataFrame" (think: a Python table)
print("Loading data...")

data_path = Path("data/messages.csv")
df = pd.read_csv(data_path, skipinitialspace=True)
# remove any leading/trailing whitespace from column names
df.columns = df.columns.str.strip()

# normalize labels to numeric values: 1 = phishing, 0 = legit
label_map = {"spam": 1, "1": 1, "0": 0}
df["label"] = df["label"].astype(str).str.strip().map(label_map)
# drop rows with missing or invalid labels or missing messages
df = df.dropna(subset=["message", "label"])
df["label"] = df["label"].astype(int)

# Quick sanity check - print first 3 rows so you can see what was loaded
print(f"\nLoaded {len(df)} messages")
print(f"Fraud messages:  {df['label'].sum()}")
print(f"Legit messages:  {(df['label'] == 0).sum()}")
print("\nSample data:")
print(df.head(3))

# So we split: 80% for training, 20% for testing
# X = the messages (input), y = the labels (what we want to predict)

X = df["message"]

y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,      # 20% goes to testing
    # random_state=42 means the split is the same every time you run it (reproducible)
    random_state=42
)
print(
    f"\nTraining on {len(X_train)} messages, testing on {len(X_test)} messages")


# Stage 2 - MultinomialNB: takes those numbers and decides fraud or legit
#   Naive Bayes asks: "given these word patterns, which category is more likely?"

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        # learns single words AND two-word phrases ("send KES", "claim prize")
        ngram_range=(1, 2),
        # only uses the 500 most important words/phrases (keeps it fast)
        max_features=500,
        lowercase=True       # treats "WON" and "won" as the same word
    )),
    ("classifier", MultinomialNB(
        # smoothing - stops the model from being overconfident. 0.1 works well for short texts
        alpha=0.1
    ))
])


# .fit() is where the actual learning happens
# The model reads every training message + its label and learns the patterns
print("\nTraining model...")
model.fit(X_train, y_train)
print("Training complete!")


# Now we use the 20% of data the model has NEVER seen before
y_predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, y_predictions)
print(f"\nModel accuracy: {accuracy * 100:.1f}%")
print("\nDetailed report:")
print(classification_report(y_test, y_predictions,
      target_names=["Legit", "Phishing"]))

# What the report means:
# precision = when model says "phishing", how often is it right?
# recall    = out of all actual phishing messages, how many did the model catch?
# f1-score  = balance between precision and recall (higher = better)


# --- STEP 6: SAVE THE MODEL ---
# joblib.dump() saves the trained model to a file
# Now your Streamlit app can load this file instead of retraining every time
model_dir = Path("model")
model_dir.mkdir(parents=True, exist_ok=True)
joblib.dump(model, model_dir / "phishing_model.pkl")
print(f"\nModel saved to {model_dir / 'phishing_model.pkl'}")
print("\nDone! You can now run the Streamlit app.")


# --- BONUS: QUICK MANUAL TEST ---
# Let's manually test a few messages so you can SEE it working
print("\n--- Manual tests ---")
test_messages = [
    "Confirmed. KES 500 sent to John 0712XXXXXX. Balance: KES 2000.",
    "CONGRATULATIONS! You WON KES 50000! Send KES 200 to claim your prize NOW!",
    "URGENT: Send KES 100 to 0799XXXXXX to reactivate your suspended account.",
]

for msg in test_messages:
    # [0] because predict returns a list, we want the first item
    prediction = model.predict([msg])[0]
    # returns [prob_legit, prob_fraud]
    probability = model.predict_proba([msg])[0]
    # probability of fraud as a percentage
    fraud_confidence = probability[1] * 100

    result = "PHISHING" if prediction == 1 else "LEGIT"
    print(f"\nMessage: {msg[:60]}...")
    print(f"Result:  {result} ({fraud_confidence:.0f}% fraud confidence)")

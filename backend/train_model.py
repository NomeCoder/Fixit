import pandas as pd
import pickle

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

data = {
    "text": [
        # pothole
        "Huge pothole on road",
        "Road broken near market",
        "Deep hole in road",
        "Road surface damaged",
        "Crater on street",

        # garbage
        "Garbage overflowing",
        "Trash everywhere",
        "Waste not collected",
        "Dustbin not cleaned",
        "Garbage lying on road",

        # water
        "Water leakage from pipe",
        "Pipeline burst",
        "Drain water flooding",
        "Water overflowing",
        "Leak in water line",

        # electricity
        "Streetlight not working",
        "Electric pole damaged",
        "Power outage",
        "No electricity",
        "Street lights off",

        # police
        "Mobile stolen",
        "Bike theft reported",
        "Phone snatched",
        "Robbery happened",
        "Vehicle stolen",

        # traffic
        "Heavy traffic jam",
        "Traffic signal broken",
        "Road blocked",
        "Traffic congestion",
        "Vehicles stuck",

        # noise
        "Loud music at night",
        "Noise pollution",
        "DJ playing loudly",
        "Very loud speakers",
        "Sound disturbance",

        # animals
        "Stray dogs attacking",
        "Cow blocking road",
        "Animals roaming freely",
        "Dog bite incident",
        "Stray cattle issue"
    ],

    "label": [
        "pothole","pothole","pothole","pothole","pothole",
        "garbage","garbage","garbage","garbage","garbage",
        "water","water","water","water","water",
        "electricity","electricity","electricity","electricity","electricity",
        "police","police","police","police","police",
        "traffic","traffic","traffic","traffic","traffic",
        "noise","noise","noise","noise","noise",
        "animals","animals","animals","animals","animals"
    ]
}

df = pd.DataFrame(data)

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1,3),
            analyzer="word",
            max_features=10000
        )
    ),
    (
        "clf",
        LogisticRegression(
            max_iter=5000,
            C=3,
            random_state=42
        )
    )
])

model.fit(df["text"], df["label"])

with open("ai_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model trained!")

# Test
while True:
    text = input("\nEnter complaint: ")

    probs = model.predict_proba([text])[0]
    pred = model.predict([text])[0]
    confidence = max(probs)

    print(f"Category: {pred}")
    print(f"Confidence: {confidence:.2%}")

    if confidence < 0.40:
        print("Low confidence - ask user for clarification.")
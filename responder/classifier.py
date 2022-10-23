from flair.data import Sentence
from flair.models import TextClassifier

from secret import CLASSIFIER_PATH


def classify(content) -> str:
    classifier = TextClassifier.load(CLASSIFIER_PATH)
    sentence = Sentence(content)
    classifier.predict(sentence)

    label = sentence.get_label("topic")
    print(f"Classifier result: {label.value} ({label.score})")
    return label.value.upper()

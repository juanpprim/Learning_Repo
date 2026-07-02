"""Toy training script used by the CI quality gate in tests/test_model.py."""
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def train():
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=0
    )
    model = LogisticRegression(max_iter=200).fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    return model, accuracy


if __name__ == "__main__":
    _, accuracy = train()
    print(f"accuracy={accuracy:.4f}")

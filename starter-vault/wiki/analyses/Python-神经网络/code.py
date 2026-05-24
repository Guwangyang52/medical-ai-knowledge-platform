from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def make_dataset(n: int = 160, seed: int = 42) -> list[tuple[list[float], int]]:
    rng = random.Random(seed)
    rows: list[tuple[list[float], int]] = []
    for _ in range(n):
        x1 = rng.uniform(-2.0, 2.0)
        x2 = rng.uniform(-2.0, 2.0)
        noise = rng.uniform(-0.30, 0.30)
        label = 1 if (x1 * x1 + x2 + noise) > 1.0 else 0
        rows.append(([x1, x2], label))
    return rows


def split_dataset(rows: list[tuple[list[float], int]], test_ratio: float = 0.30) -> tuple[list, list]:
    split_at = int(len(rows) * (1 - test_ratio))
    return rows[:split_at], rows[split_at:]


def train_mlp(rows: list[tuple[list[float], int]], epochs: int = 250, learning_rate: float = 0.08) -> tuple[dict, list[float]]:
    rng = random.Random(7)
    hidden_size = 4
    weights_input_hidden = [[rng.uniform(-0.5, 0.5) for _ in range(2)] for _ in range(hidden_size)]
    bias_hidden = [0.0 for _ in range(hidden_size)]
    weights_hidden_output = [rng.uniform(-0.5, 0.5) for _ in range(hidden_size)]
    bias_output = 0.0
    losses: list[float] = []

    for _ in range(epochs):
        total_loss = 0.0
        for features, label in rows:
            hidden_raw = [
                sum(weight * value for weight, value in zip(weights, features)) + bias
                for weights, bias in zip(weights_input_hidden, bias_hidden)
            ]
            hidden = [sigmoid(value) for value in hidden_raw]
            output_raw = sum(weight * value for weight, value in zip(weights_hidden_output, hidden)) + bias_output
            predicted = sigmoid(output_raw)

            error = predicted - label
            total_loss += error * error
            grad_output = error * predicted * (1 - predicted)

            old_output_weights = weights_hidden_output[:]
            for index in range(hidden_size):
                weights_hidden_output[index] -= learning_rate * grad_output * hidden[index]
            bias_output -= learning_rate * grad_output

            for hidden_index in range(hidden_size):
                grad_hidden = grad_output * old_output_weights[hidden_index] * hidden[hidden_index] * (1 - hidden[hidden_index])
                for feature_index in range(2):
                    weights_input_hidden[hidden_index][feature_index] -= learning_rate * grad_hidden * features[feature_index]
                bias_hidden[hidden_index] -= learning_rate * grad_hidden

        losses.append(total_loss / len(rows))

    model = {
        "weights_input_hidden": weights_input_hidden,
        "bias_hidden": bias_hidden,
        "weights_hidden_output": weights_hidden_output,
        "bias_output": bias_output,
    }
    return model, losses


def predict_one(model: dict, features: list[float]) -> int:
    hidden = [
        sigmoid(sum(weight * value for weight, value in zip(weights, features)) + bias)
        for weights, bias in zip(model["weights_input_hidden"], model["bias_hidden"])
    ]
    output = sigmoid(sum(weight * value for weight, value in zip(model["weights_hidden_output"], hidden)) + model["bias_output"])
    return 1 if output >= 0.5 else 0


def evaluate(model: dict, rows: list[tuple[list[float], int]]) -> dict:
    matrix = [[0, 0], [0, 0]]
    correct = 0
    for features, label in rows:
        predicted = predict_one(model, features)
        matrix[label][predicted] += 1
        correct += int(predicted == label)
    return {
        "accuracy": correct / len(rows),
        "confusion_matrix": matrix,
    }


def write_confusion_matrix(path: Path, matrix: list[list[int]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["actual\\predicted", "0", "1"])
        for index, row in enumerate(matrix):
            writer.writerow([index, *row])


def write_losses(path: Path, losses: list[float]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["epoch", "loss"])
        for index, loss in enumerate(losses, start=1):
            writer.writerow([index, loss])


def main() -> int:
    task_dir = Path.cwd()
    output_dir = task_dir / "output"
    output_dir.mkdir(exist_ok=True)

    rows = make_dataset()
    train_rows, test_rows = split_dataset(rows)
    model, losses = train_mlp(train_rows)
    result = evaluate(model, test_rows)

    metrics = {
        "dataset": "synthetic_binary_classification",
        "n_train": len(train_rows),
        "n_test": len(test_rows),
        "hidden_layer_sizes": [4],
        "epochs": len(losses),
        "final_loss": losses[-1],
        **result,
    }
    (output_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    write_confusion_matrix(output_dir / "confusion_matrix.csv", result["confusion_matrix"])
    write_losses(output_dir / "training_loss.csv", losses)

    print(f"Accuracy: {result['accuracy']:.3f}")
    print("Outputs written to output/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

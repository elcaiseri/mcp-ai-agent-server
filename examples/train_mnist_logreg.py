"""
Train a multinomial logistic regression on a random subset of MNIST.

Usage:
    python examples/train_mnist_logreg.py --n-samples 2000 --test-size 0.2 --max-iter 200

Requirements:
    pip install scikit-learn joblib

This script:
- downloads MNIST via sklearn.datasets.fetch_openml
- selects a random subset of specified size
- normalizes pixel values to [0,1]
- splits into train/test
- trains LogisticRegression (multinomial)
- prints accuracy and classification report
- saves the trained model to a pickle using joblib
"""
from __future__ import annotations
import argparse
import time
from pathlib import Path

import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train multinomial logistic regression on MNIST subset")
    p.add_argument("--n-samples", type=int, default=2000, help="number of total samples to use (train+test)")
    p.add_argument("--test-size", type=float, default=0.2, help="fraction of subset reserved for testing")
    p.add_argument("--random-state", type=int, default=42, help="random seed")
    p.add_argument("--C", type=float, default=1.0, help="inverse regularization strength for LogisticRegression")
    p.add_argument("--max-iter", type=int, default=200, help="max iterations for solver")
    p.add_argument("--output", type=Path, default=Path("mnist_logreg.pkl"), help="where to save the trained model")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    rng = np.random.RandomState(args.random_state)

    print("Fetching MNIST (this may download data on first run)...")
    t0 = time.time()
    X, y = fetch_openml("mnist_784", version=1, return_X_y=True, as_frame=False)
    print(f"Fetched MNIST: {X.shape[0]} samples, {X.shape[1]} features in {time.time()-t0:.1f}s")

    # Convert labels to integers
    y = y.astype(int)

    n_total = X.shape[0]
    n_samples = min(args.n_samples, n_total)
    if n_samples < n_total:
        idx = rng.choice(n_total, size=n_samples, replace=False)
        X_sub = X[idx]
        y_sub = y[idx]
        print(f"Selected random subset: {n_samples} samples")
    else:
        X_sub = X
        y_sub = y
        print(f"Using full dataset: {n_samples} samples")

    # Normalize pixel values from [0,255] to [0,1]
    X_sub = X_sub.astype(np.float32) / 255.0

    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X_sub, y_sub, test_size=args.test_size, random_state=args.random_state, stratify=y_sub
    )
    print(f"Train samples: {X_train.shape[0]}, Test samples: {X_test.shape[0]}")

    # Train logistic regression (multinomial)
    print("Training LogisticRegression (multinomial)...")
    model = LogisticRegression(
        solver="saga",
        multi_class="multinomial",
        penalty="l2",
        C=args.C,
        max_iter=args.max_iter,
        n_jobs=-1,
        verbose=0,
    )
    t0 = time.time()
    model.fit(X_train, y_train)
    elapsed = time.time() - t0
    print(f"Training completed in {elapsed:.1f}s")

    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test accuracy: {acc:.4f}")
    print("Classification report:\n", classification_report(y_test, y_pred))

    # Save model
    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "meta": {"n_samples": n_samples, "test_size": args.test_size}}, args.output)
    print(f"Saved trained model to {args.output}")


if __name__ == "__main__":
    main()

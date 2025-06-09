#!/usr/bin/env python3

"""Command-line quiz app with a richer UI and more features."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import random
from pathlib import Path
from typing import Iterable, List, Tuple

from rich.console import Console
from rich.prompt import Prompt


Question = Tuple[str, str]

logger = logging.getLogger(__name__)


def load_questions(
    path: Path | str,
    *,
    category: str | None = None,
    difficulty: str | None = None,
) -> List[Question]:
    """Load questions from JSON/CSV file or a remote URL."""

    if isinstance(path, str) and path.startswith(("http://", "https://")):
        try:
            import requests

            logger.info("Fetching questions from %s", path)
            resp = requests.get(path, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # pragma: no cover - network failure
            raise RuntimeError(f"Failed to fetch questions: {exc}") from exc
    else:
        path = Path(path)
        if path.suffix == ".csv":
            with path.open("r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                data = list(reader)
        else:
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)

    questions = []
    for item in data:
        if category is not None and item.get("category") != category:
            continue
        if difficulty is not None and item.get("difficulty") != difficulty:
            continue
        questions.append((item["question"], item["answer"]))

    return questions


def load_high_scores(path: Path) -> List[dict]:
    """Return a list of recorded high scores."""
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError:
            return []

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "scores" in data:
            return data["scores"]
        if "high_score" in data:
            return [{"user": "", "score": int(data["high_score"])}]
    return []


def load_high_score(path: Path) -> int:
    """Return the best high score stored in *path*."""
    scores = load_high_scores(path)
    if not scores:
        return 0
    return max(s["score"] for s in scores)


def save_high_score(path: Path, name: str, score: int) -> None:
    """Record *name* and *score* in the ranking."""
    scores = load_high_scores(path)
    scores.append({"user": name, "score": score})
    scores.sort(key=lambda s: s["score"], reverse=True)
    scores = scores[:5]
    with path.open("w", encoding="utf-8") as fh:
        json.dump({"scores": scores}, fh, ensure_ascii=False, indent=2)


def ask_questions(
    questions: Iterable[Question], console: Console
) -> tuple[int, list[dict]]:
    """Return the score and per-question results for *questions*."""
    score = 0
    results: list[dict] = []
    for question, answer in questions:
        user_answer = Prompt.ask(question)
        correct = user_answer.strip().lower() == answer.lower()
        if correct:
            console.print("Correct!", style="bold green")
            score += 1
        else:
            console.print(
                f"Incorrect. The correct answer is {answer}.",
                style="bold red",
            )
        results.append(
            {
                "question": question,
                "answer": answer,
                "user_answer": user_answer,
                "correct": correct,
            }
        )
    return score, results


def export_results(path: Path, results: list[dict]) -> None:
    """Export quiz *results* to a CSV file."""
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["question", "answer", "user_answer", "correct"]
        )
        writer.writeheader()
        writer.writerows(results)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Quiz application")
    parser.add_argument(
        "-f", "--file", default="questions.json", help="Path to questions file"
    )
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=None,
        help="Number of questions to ask",
    )
    parser.add_argument(
        "-c",
        "--category",
        default=None,
        help="Only ask questions from the given category",
    )
    parser.add_argument(
        "-d",
        "--difficulty",
        default=None,
        help="Only ask questions with the given difficulty",
    )
    parser.add_argument(
        "-s",
        "--shuffle",
        action="store_true",
        help="Ask questions in random order",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="User name for high score",
    )
    parser.add_argument(
        "--export-csv",
        dest="export_csv",
        default=None,
        help="Export results to the specified CSV file",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO)

    console = Console()
    questions = load_questions(
        Path(args.file), category=args.category, difficulty=args.difficulty
    )
    if args.num is not None:
        questions = questions[: args.num]
    if args.shuffle:
        random.shuffle(questions)

    name = args.name or Prompt.ask("Your name")

    score, results = ask_questions(questions, console)

    console.rule("Quiz Complete")
    console.print(
        f"You got {score}/{len(questions)} correct.", style="bold blue"
    )

    high_score_path = Path("highscore.json")
    save_high_score(high_score_path, name, score)
    best = load_high_score(high_score_path)
    console.print(f"High Score: {best}", style="bold magenta")

    if args.export_csv:
        export_results(Path(args.export_csv), results)


if __name__ == "__main__":
    main()

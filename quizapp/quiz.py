#!/usr/bin/env python3

"""Command-line quiz app with a richer UI and more features."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List, Tuple

from rich.console import Console
from rich.prompt import Prompt


Question = Tuple[str, str]


def load_questions(path: Path, *, category: str | None = None) -> List[Question]:
    """Load questions from a JSON file."""
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    questions = [
        (item["question"], item["answer"])
        for item in data
        if category is None or item.get("category") == category
    ]
    return questions


def load_high_score(path: Path) -> int:
    """Return the current high score stored in *path*."""
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError:
            return 0
    return int(data.get("high_score", 0))


def save_high_score(path: Path, score: int) -> None:
    """Save *score* to *path* if it is higher than the stored score."""
    current = load_high_score(path)
    if score > current:
        with path.open("w", encoding="utf-8") as fh:
            json.dump({"high_score": score}, fh)


def ask_questions(questions: Iterable[Question], console: Console) -> int:
    """Iterate over *questions* and return the number answered correctly."""
    score = 0
    for question, answer in questions:
        user_answer = Prompt.ask(question)
        if user_answer.strip().lower() == answer.lower():
            console.print("Correct!", style="bold green")
            score += 1
        else:
            console.print(
                f"Incorrect. The correct answer is {answer}.",
                style="bold red",
            )
    return score


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Quiz application")
    parser.add_argument(
        "-f", "--file", default="questions.json", help="Path to questions file"
    )
    parser.add_argument(
        "-n", "--num", type=int, default=None, help="Number of questions to ask"
    )
    parser.add_argument(
        "-c",
        "--category",
        default=None,
        help="Only ask questions from the given category",
    )
    args = parser.parse_args(argv)

    console = Console()
    questions = load_questions(Path(args.file), category=args.category)
    if args.num is not None:
        questions = questions[: args.num]

    score = ask_questions(questions, console)

    console.rule("Quiz Complete")
    console.print(
        f"You got {score}/{len(questions)} correct.", style="bold blue"
    )

    high_score_path = Path("highscore.json")
    save_high_score(high_score_path, score)
    best = load_high_score(high_score_path)
    console.print(f"High Score: {best}", style="bold magenta")


if __name__ == "__main__":
    main()

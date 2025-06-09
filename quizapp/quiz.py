#!/usr/bin/env python3

"""Command-line quiz app with a richer UI."""

from typing import List, Tuple

from rich.console import Console
from rich.prompt import Prompt

QUESTIONS: List[Tuple[str, str]] = [
    ("What is the capital of France?", "Paris"),
    ("What is 2 + 2?", "4"),
    ("Who wrote '1984'?", "George Orwell"),
]


def main() -> None:
    console = Console()
    score = 0
    for question, answer in QUESTIONS:
        user_answer = Prompt.ask(question)
        if user_answer.strip().lower() == answer.lower():
            console.print("Correct!", style="bold green")
            score += 1
        else:
            console.print(
                f"Incorrect. The correct answer is {answer}.",
                style="bold red",
            )
    console.rule("Quiz Complete")
    console.print(
        f"You got {score}/{len(QUESTIONS)} correct.", style="bold blue"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

"""Feature-rich command-line quiz application."""

import argparse
import json
import random
from dataclasses import dataclass
from typing import List

QUESTIONS_FILE = "questions.json"
SCORES_FILE = "highscores.json"


@dataclass
class Question:
    question: str
    answer: str


class Quiz:
    def __init__(self, questions: List[Question]):
        self.questions = questions

    @classmethod
    def from_file(cls, path: str) -> "Quiz":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        questions = [Question(**item) for item in data]
        return cls(questions)

    def ask(self, num_questions: int | None = None) -> int:
        q_list = self.questions[:]
        random.shuffle(q_list)
        if num_questions is not None:
            q_list = q_list[:num_questions]
        score = 0
        for q in q_list:
            user_answer = input(q.question + " ")
            if user_answer.strip().lower() == q.answer.lower():
                print("Correct!")
                score += 1
            else:
                print(f"Incorrect. The correct answer is {q.answer}.")
        return score


def save_score(name: str, score: int, total: int, path: str = SCORES_FILE) -> None:
    entry = {"name": name, "score": score, "total": total}
    try:
        with open(path, "r", encoding="utf-8") as f:
            scores = json.load(f)
    except FileNotFoundError:
        scores = []
    scores.append(entry)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)


def show_scores(path: str = SCORES_FILE) -> None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            scores = json.load(f)
    except FileNotFoundError:
        print("No high scores yet.")
        return
    for entry in scores:
        print(f"{entry['name']}: {entry['score']}/{entry['total']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quiz application")
    parser.add_argument("-f", "--file", default=QUESTIONS_FILE,
                        help="Path to questions JSON file")
    parser.add_argument("-n", "--num", type=int,
                        help="Number of questions to ask")
    parser.add_argument("--show-scores", action="store_true",
                        help="Display high scores and exit")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.show_scores:
        show_scores()
        return
    quiz = Quiz.from_file(args.file)
    score = quiz.ask(args.num)
    total = args.num if args.num is not None else len(quiz.questions)
    print(f"You got {score}/{total} correct.")
    name = input("Enter your name for the high scores: ").strip()
    if name:
        save_score(name, score, total)


if __name__ == "__main__":
    main()

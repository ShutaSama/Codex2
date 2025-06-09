#!/usr/bin/env python3

"""Simple command-line quiz app."""

QUESTIONS = [
    ("What is the capital of France?", "Paris"),
    ("What is 2 + 2?", "4"),
    ("Who wrote '1984'?", "George Orwell"),
]


def main() -> None:
    score = 0
    for question, answer in QUESTIONS:
        user_answer = input(question + " ")
        if user_answer.strip().lower() == answer.lower():
            print("Correct!")
            score += 1
        else:
            print(f"Incorrect. The correct answer is {answer}.")
    print(f"You got {score}/{len(QUESTIONS)} correct.")


if __name__ == "__main__":
    main()

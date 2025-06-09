import json
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Provide minimal stubs for the rich library used in the application


class DummyConsole:
    def __init__(self):
        self.messages = []

    def print(self, *args, **kwargs):
        self.messages.append((args, kwargs))

    def rule(self, *args, **kwargs):
        self.messages.append(("rule", args, kwargs))


console_stub = types.SimpleNamespace(Console=DummyConsole)


class DummyPrompt:
    answers: list[str] = []

    @classmethod
    def ask(cls, _question):
        return cls.answers.pop(0)


prompt_stub = types.SimpleNamespace(Prompt=DummyPrompt)
sys.modules.setdefault("rich", types.ModuleType("rich"))
sys.modules.setdefault("rich.console", console_stub)
sys.modules.setdefault("rich.prompt", prompt_stub)

import quizapp.quiz as qz  # noqa: E402


def test_load_questions(tmp_path: Path) -> None:
    data = [
        {"question": "Q1", "answer": "A1", "category": "Cat"},
        {"question": "Q2", "answer": "A2", "category": "Other"},
    ]
    p = tmp_path / "questions.json"
    p.write_text(json.dumps(data))
    questions = qz.load_questions(p, category="Cat")
    assert questions == [("Q1", "A1")]


def test_high_score(tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"
    assert qz.load_high_score(path) == 0
    qz.save_high_score(path, "A", 3)
    assert qz.load_high_score(path) == 3
    # lower score should not overwrite
    qz.save_high_score(path, "B", 1)
    assert qz.load_high_score(path) == 3


def test_ask_questions() -> None:
    console = qz.Console()
    DummyPrompt.answers = ["A1", "wrong"]
    questions = [("Q1", "A1"), ("Q2", "A2")]
    score, results = qz.ask_questions(questions, console)
    assert score == 1
    assert results[0]["correct"] is True
    assert results[1]["correct"] is False


def test_main(tmp_path: Path, monkeypatch) -> None:
    data = [
        {"question": "Q1", "answer": "A1"},
        {"question": "Q2", "answer": "A2"},
    ]
    qfile = tmp_path / "q.json"
    qfile.write_text(json.dumps(data))
    hs_path = tmp_path / "highscore.json"

    def fake_path(name):
        return tmp_path / name

    monkeypatch.setattr(qz, "Path", lambda p="": fake_path(p))
    DummyPrompt.answers = ["Tester", "A1", "A2"]
    console = qz.Console()
    monkeypatch.setattr(qz, "Console", lambda: console)

    qz.main(["-f", str(qfile)])
    assert hs_path.exists()
    scores = qz.load_high_scores(hs_path)
    assert scores[0]["user"] == "Tester"

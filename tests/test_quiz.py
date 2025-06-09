import json
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Provide minimal stubs for the rich library used in the application
console_stub = types.SimpleNamespace(Console=object)
prompt_stub = types.SimpleNamespace(Prompt=object)
sys.modules.setdefault("rich", types.ModuleType("rich"))
sys.modules.setdefault("rich.console", console_stub)
sys.modules.setdefault("rich.prompt", prompt_stub)

import quizapp.quiz as qz


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
    qz.save_high_score(path, 3)
    assert qz.load_high_score(path) == 3
    # lower score should not overwrite
    qz.save_high_score(path, 1)
    assert qz.load_high_score(path) == 3

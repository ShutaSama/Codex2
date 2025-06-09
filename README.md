# Codex2

[![CI](https://github.com/example/codex2/actions/workflows/ci.yml/badge.svg)](https://github.com/example/codex2/actions/workflows/ci.yml)

Codex2 is a simple command-line quiz application. It now uses the
[Rich](https://github.com/Textualize/rich) library to provide colored output
and a nicer interface.

## Usage
First install the dependencies:

```bash
pip install -r requirements.txt
```

Then run `python -m quizapp.quiz` to start the quiz.

Questions are loaded from `questions.json` by default. You can supply a
different file or limit the number of questions with command line options:

```bash
python -m quizapp.quiz -f my_questions.json -n 5
```

After completing a quiz the highest score is stored in `highscore.json`.

To run the test suite:

```bash
pytest
```

### Docker
You can also run the quiz in a Docker container:

```bash
docker build -t codex2 .
docker run -it codex2
```

## Future Plans
- Add more questions


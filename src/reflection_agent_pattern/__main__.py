from .models import ScriptedCritic, ScriptedGenerator
from .reflection import ReflectionAgent


def main() -> None:
    result = ReflectionAgent(ScriptedGenerator(), ScriptedCritic()).run(
        "Write an accuracy-critical architecture summary"
    )
    print(result.answer)
    print(f"attempts={len(result.attempts)}")


if __name__ == "__main__":
    main()


from typing import Iterable


def choose_option(prompt: str, options: Iterable[str]) -> str:
    opts = list(options)
    for idx, opt in enumerate(opts, 1):
        print(f"{idx}. {opt}")
    while True:
        choice = input(prompt)
        if choice.isdigit() and 1 <= int(choice) <= len(opts):
            return opts[int(choice) - 1]
        print("Invalid selection")

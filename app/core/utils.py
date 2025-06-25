import re


def sort_tags_numerically(tag_names: list[str]) -> list[str]:
    def sort_key(name: str) -> tuple[int | str, ...]:
        parts = re.split(r"(\d+)", name)
        return tuple(int(part) if part.isdigit() else part for part in parts)

    return sorted(tag_names, key=sort_key)

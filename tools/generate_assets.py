from __future__ import annotations

from pathlib import Path

Palette = dict[str, tuple[int, int, int]]


def write_ppm(path: Path, pixels: list[list[tuple[int, int, int]]]) -> None:
    h = len(pixels)
    w = len(pixels[0])
    with path.open("w", encoding="utf-8") as f:
        f.write(f"P3\n{w} {h}\n255\n")
        for row in pixels:
            f.write(" ".join(f"{r} {g} {b}" for (r, g, b) in row) + "\n")


def sprite_from_pattern(pattern: list[str], palette: Palette) -> list[list[tuple[int, int, int]]]:
    return [[palette[ch] for ch in row] for row in pattern]


def main() -> None:
    out = Path("assets/generated")
    out.mkdir(parents=True, exist_ok=True)

    palette = {
        ".": (20, 20, 28),
        "A": (89, 178, 255),
        "B": (255, 122, 89),
        "W": (235, 235, 245),
        "Y": (250, 206, 84),
        "G": (56, 194, 118),
    }

    scout = [
        "........",
        "...WW...",
        "..WAAW..",
        "..WAAW..",
        "..WAAW..",
        "...WW...",
        "..W..W..",
        "........",
    ]
    bruiser = [
        "........",
        "..BBBB..",
        ".BWWWWB.",
        ".BWYYWB.",
        ".BWWWWB.",
        "..BGGB..",
        "..B..B..",
        "........",
    ]
    tile = [
        "GGGGGGGG",
        "G......G",
        "G..YY..G",
        "G..YY..G",
        "G..YY..G",
        "G..YY..G",
        "G......G",
        "GGGGGGGG",
    ]

    write_ppm(out / "unit_scout.ppm", sprite_from_pattern(scout, palette))
    write_ppm(out / "unit_bruiser.ppm", sprite_from_pattern(bruiser, palette))
    write_ppm(out / "control_point.ppm", sprite_from_pattern(tile, palette))
    print(f"generated assets in {out}")


if __name__ == "__main__":
    main()

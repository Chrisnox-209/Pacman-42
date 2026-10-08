from pydantic import BaseModel, field_validator
from pathlib import Path
from src.utils import Color
import json
import argparse


class ConfigPathError(Exception):
    """
    Exception raised for errors related to output file paths.
    """
    pass


def check_argument() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
    )
    args: argparse.Namespace = parser.parse_args()
    return str(args.config)


class LevelConfig(BaseModel):
    width: int
    height: int

    @field_validator("width")
    @classmethod
    def check_width(cls, value: int) -> int:
        if value < 10:
            raise ValueError(f"\n{Color.BLUE.value}[INFO]"
                             f"{Color.RST.value} Width must be >= 10")

        if value > 40:
            raise ValueError(f"\n{Color.BLUE.value}[INFO]"
                             f"{Color.RST.value} Width must be <= 40")

        return value

    @field_validator("height")
    @classmethod
    def check_height(cls, value: int) -> int:
        if value < 10:
            raise ValueError(f"\n{Color.BLUE.value}[INFO]"
                             f"{Color.RST.value} Height must be >= 10")

        if value > 20:
            raise ValueError(f"\n{Color.BLUE.value}[INFO]"
                             f"{Color.RST.value} Height must be <= 20")

        return value


class ParseConfig(BaseModel):
    highscore_filename: Path
    levels: list[LevelConfig]
    lives: int
    speed_player: int
    speed_ghosts: int
    pacgum: int
    super_pacgums: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    seed: int
    level_max_time: int

    @field_validator("highscore_filename")
    @classmethod
    def check_extension(cls, value: Path) -> Path:
        if value.suffix.lower() != ".json":
            raise ValueError(f"\n{Color.BLUE.value}[INFO]"
                             f"{Color.RST.value} The extension must "
                             "be .json")
        return value

    @field_validator("lives")
    @classmethod
    def check_live(cls, value: int) -> int:
        if value < 1:
            raise ValueError(f"\n{Color.BLUE.value}[INFO]"
                             f"{Color.RST.value} Lives must be equal"
                             "to or greater than 1")
        return value

    @field_validator("pacgum")
    @classmethod
    def check_pacgum(cls, value: int) -> int:
        if value < 10 or value > 100:
            raise ValueError(f"\n{Color.BLUE.value}[INFO]"
                             f"{Color.RST.value} The pack gum must be"
                             "equal to or greater than 10")
        return value

    @field_validator("super_pacgums")
    @classmethod
    def check_super_pacgums(cls, value: int) -> int:
        if value < 4:
            raise ValueError(f"\n{Color.BLUE.value}[INFO]"
                             f"{Color.RST.value} The super packgums must be"
                             "equal to or greater than 4")
        return value

    @field_validator("levels")
    @classmethod
    def check_levels(
        cls,
        value: list[LevelConfig],
    ) -> list[LevelConfig]:
        if len(value) != 10:
            raise ValueError(f"\n{Color.BLUE.value}[INFO]"
                             f"{Color.RST.value} Exactly "
                             "10 levels are required")
        return value

    @field_validator(
        "points_per_pacgum",
        "points_per_super_pacgum",
        "points_per_ghost",
    )
    @classmethod
    def check_points(cls, value: int) -> int:
        if value < 1:
            raise ValueError(f"\n{Color.BLUE.value}[INFO]"
                             f"{Color.RST.value} The points must be"
                             "equal to or greater than 1")
        return value

    @field_validator("level_max_time")
    @classmethod
    def check_time(cls, value: int) -> int:
        if value < 15:
            raise ValueError(f"\n{Color.BLUE.value}[INFO]"
                             f"{Color.RST.value} The time must be"
                             "equal to or greater than 15")
        return value

    @field_validator(
        "speed_player",
        "speed_ghosts",
    )
    @classmethod
    def check_speed(cls, value: int) -> int:
        if value < 1 or value > 100:
            raise ValueError(f"\n{Color.BLUE.value}[INFO]"
                             f"{Color.RST.value} The speed must be between "
                             "1 and 100")
        return value


def json_to_data(file: str) -> ParseConfig:
    try:
        with open(file, "r", encoding="utf-8") as content:
            json_data: object = json.load(content)
            return ParseConfig.model_validate(json_data)
    except FileNotFoundError:
        raise ValueError(f'The file "{Color.YELLOW.value}{file}'
                         f'{Color.RST.value}" could not be found.')
    except json.JSONDecodeError:
        raise ValueError(f'The file "{Color.YELLOW.value}{file}'
                         f'"{Color.RST.value}" is not valid JSON.')

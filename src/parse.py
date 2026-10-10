from pathlib import Path
from typing import Any
import json

from pydantic import (BaseModel, Field,
                      ValidationError, ValidationInfo,
                      field_validator)

from src.utils import Color


class ConfigPathError(Exception):
    """
    Exception raised for errors related to output file paths.
    """
    pass


class ParseScore(BaseModel):
    name_player: str
    score: int

    @field_validator("name_player")
    @classmethod
    def check_player(cls, value: str) -> str:
        if len(value) > 10 or len(value) < 1:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} The player's name is "
                "too long must be <= 10"
            )

        for c in value:
            if not c.isalnum() and c != " ":
                raise ValueError(
                    f"\n{Color.BLUE.value}[INFO]"
                    f"{Color.RST.value} Player name error "
                    "(only alphanumeric characters and spaces allowed)"
                )

        return value

    @field_validator("score")
    @classmethod
    def check_score(cls, value: int) -> int:
        if value < 0:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} Score must be >= 0"
            )

        return value


class ParseHighScore(BaseModel):
    highscore: list[ParseScore]

    @field_validator("highscore")
    @classmethod
    def check_highscores(
        cls,
        value: list[ParseScore],
    ) -> list[ParseScore]:
        if len(value) > 10:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} Exactly "
                "10 hightscores are required"
            )

        return value


class LevelConfig(BaseModel):
    width: int
    height: int

    @field_validator("width")
    @classmethod
    def check_width(cls, value: int) -> int:
        if value < 10:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} Width must be >= 10"
            )

        if value > 40:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} Width must be <= 40"
            )

        return value

    @field_validator("height")
    @classmethod
    def check_height(cls, value: int) -> int:
        if value < 10:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} Height must be >= 10"
            )

        if value > 20:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} Height must be <= 20"
            )

        return value


def default_levels() -> list[LevelConfig]:
    return [
        LevelConfig(width=20, height=20),
        LevelConfig(width=22, height=20),
        LevelConfig(width=24, height=20),
        LevelConfig(width=26, height=20),
        LevelConfig(width=28, height=20),
        LevelConfig(width=30, height=20),
        LevelConfig(width=32, height=20),
        LevelConfig(width=34, height=20),
        LevelConfig(width=36, height=20),
        LevelConfig(width=40, height=20),
    ]


class ParseConfig(BaseModel):
    highscore_filename: Path = Path("scores.json")
    levels: list[LevelConfig] = Field(default_factory=default_levels)
    lives: int = 3
    speed_player: int = 10
    speed_ghosts: int = 9
    pacgum: int = 100
    super_pacgums: int = 4
    points_per_pacgum: int = 1
    points_per_super_pacgum: int = 10
    points_per_ghost: int = 15
    seed: int = 42
    level_max_time: int = 90
    perfect: bool = False

    @field_validator("highscore_filename", mode="before")
    @classmethod
    def check_extension(cls, value: Any) -> Path:
        if not isinstance(value, (str, Path)):
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}(highscore_filename: {value})"
                f"{Color.RST.value} Invalid highscore filename\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}highscore_filename = scores.json"
            )
            return Path("scores.json")

        path: Path = Path(value)

        if path.suffix.lower() != ".json":
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}(highscore_filename: {value})"
                f"{Color.RST.value} The extension must be .json\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}highscore_filename = scores.json"
            )
            return Path("scores.json")

        return path

    @field_validator("lives", mode="before")
    @classmethod
    def check_live(cls, value: Any) -> int:
        if type(value) is not int:
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}(lives: {value})"
                f"{Color.RST.value} Lives must be an integer\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}Live = 3"
            )
            return 3

        if value < 1:
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}(lives: {value})"
                f"{Color.RST.value} Lives must be equal "
                "to or greater than 1\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}Live = 3"
            )
            return 3

        return value

    @field_validator("pacgum", mode="before")
    @classmethod
    def check_pacgum(cls, value: Any) -> int:
        if type(value) is not int or value < 10 or value > 100:
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}(pacgum: {value})"
                f"{Color.RST.value} Pacgum must be an integer "
                "between 10 and 100\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}pacgum = 100"
            )
            return 100

        return value

    @field_validator("super_pacgums", mode="before")
    @classmethod
    def check_super_pacgums(cls, value: Any) -> int:
        if type(value) is not int or value < 4:
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}(super_pacgums: {value})"
                f"{Color.RST.value} Super pacgums must be an integer "
                "equal to or greater than 4\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}super_pacgums = 4"
            )
            return 4

        return value

    @field_validator("levels", mode="before")
    @classmethod
    def check_levels(cls, value: Any) -> list[LevelConfig]:
        if type(value) is not list or len(value) < 10:
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}(levels: invalid)"
                f"{Color.RST.value} At least 10 levels are required\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}Default levels loaded"
            )
            return default_levels()

        try:
            levels: list[LevelConfig] = [
                LevelConfig.model_validate(level)
                for level in value
            ]
        except ValidationError:
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}(levels: invalid)"
                f"{Color.RST.value} Invalid level configuration\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}Default levels loaded"
            )
            return default_levels()

        return levels

    @field_validator(
        "points_per_pacgum",
        "points_per_super_pacgum",
        "points_per_ghost",
        mode="before",
    )
    @classmethod
    def check_points(
        cls,
        value: Any,
        info: ValidationInfo,
    ) -> int:
        defaults: dict[str, int] = {
            "points_per_pacgum": 1,
            "points_per_super_pacgum": 10,
            "points_per_ghost": 15,
        }

        default: int = defaults[info.field_name]

        if type(value) is not int or value < 1:
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}({info.field_name}: {value})"
                f"{Color.RST.value} Points must be an integer "
                "equal to or greater than 1\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}{info.field_name} = {default}"
            )
            return default

        return value

    @field_validator("level_max_time", mode="before")
    @classmethod
    def check_time(cls, value: Any) -> int:
        if type(value) is not int or value < 15:
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}(level_max_time: {value})"
                f"{Color.RST.value} Time must be an integer "
                "equal to or greater than 15\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}level_max_time = 90"
            )
            return 90

        return value

    @field_validator(
        "speed_player",
        "speed_ghosts",
        mode="before",
    )
    @classmethod
    def check_speed(
        cls,
        value: Any,
        info: ValidationInfo,
    ) -> int:
        defaults: dict[str, int] = {
            "speed_player": 10,
            "speed_ghosts": 9,
        }

        default: int = defaults[info.field_name]

        if type(value) is not int or value < 1 or value > 100:
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}({info.field_name}: {value})"
                f"{Color.RST.value} Speed must be an integer "
                "between 1 and 100\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}{info.field_name} = {default}"
            )
            return default

        return value

    @field_validator("seed", mode="before")
    @classmethod
    def check_seed(cls, value: Any) -> int:
        if type(value) is not int:
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}(seed: {value})"
                f"{Color.RST.value} Seed must be an integer\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}seed = 42"
            )
            return 42

        return value

    @field_validator("perfect", mode="before")
    @classmethod
    def check_perfect(cls, value: Any) -> bool:
        if value is not False:
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}(perfect: {value})"
                f"{Color.RST.value} Perfect must be False\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}perfect = False"
            )
            return False

        return value


def json_to_data(file: str) -> ParseConfig:
    try:
        with open(file, "r", encoding="utf-8") as content:
            json_content: str = ""

            for line in content:
                if not line.lstrip().startswith("#"):
                    json_content = json_content + line

            json_data: object = json.loads(json_content)
            return ParseConfig.model_validate(json_data)

    except FileNotFoundError:
        print(
            f"\n{Color.ORANGE.value}[WARN] "
            f"{Color.RED.value}(config: {file})"
            f"{Color.RST.value} The configuration file could not be found\n"
            f"{Color.MAGENTA.value}[Default value] "
            f"{Color.GREEN.value}Default configuration loaded"
        )
        return ParseConfig()

    except json.JSONDecodeError:
        print(
            f"\n{Color.ORANGE.value}[WARN] "
            f"{Color.RED.value}(config: {file})"
            f"{Color.RST.value} The configuration file is not valid JSON\n"
            f"{Color.MAGENTA.value}[Default value] "
            f"{Color.GREEN.value}Default configuration loaded"
        )
        return ParseConfig()

    except ValidationError:
        print(
            f"\n{Color.ORANGE.value}[WARN] "
            f"{Color.RED.value}(config: {file})"
            f"{Color.RST.value} Invalid configuration\n"
            f"{Color.MAGENTA.value}[Default value] "
            f"{Color.GREEN.value}Default configuration loaded"
        )
        return ParseConfig()


def highscore_to_data(file: Path) -> ParseHighScore:
    try:
        with open(file, "r", encoding="utf8") as content:
            score_data: object = json.load(content)
            return ParseHighScore.model_validate(score_data)

    except FileNotFoundError:
        print(
            f"\n{Color.ORANGE.value}[WARN] "
            f"{Color.RED.value}(highscore_filename: {file})"
            f"{Color.RST.value} The highscore file could not be found\n"
            f"{Color.MAGENTA.value}[Default value] "
            f"{Color.GREEN.value}Empty highscore list loaded"
        )
        return ParseHighScore(highscore=[])

    except json.JSONDecodeError:
        print(
            f"\n{Color.ORANGE.value}[WARN] "
            f"{Color.RED.value}(highscore_filename: {file})"
            f"{Color.RST.value} The highscore file is not valid JSON\n"
            f"{Color.MAGENTA.value}[Default value] "
            f"{Color.GREEN.value}Empty highscore list loaded"
        )
        return ParseHighScore(highscore=[])

    except ValidationError:
        print(
            f"\n{Color.ORANGE.value}[WARN] "
            f"{Color.RED.value}(highscore_filename: {file})"
            f"{Color.RST.value} Invalid highscore data\n"
            f"{Color.MAGENTA.value}[Default value] "
            f"{Color.GREEN.value}Empty highscore list loaded"
        )
        return ParseHighScore(highscore=[])
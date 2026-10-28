"""Validate configuration and load or save highscore data."""

from pathlib import Path
from typing import Any
import json

from pydantic import (BaseModel, Field,
                      ValidationError, ValidationInfo,
                      field_validator)

from src.common.utils import Color


class ConfigPathError(Exception):
    """Represent an invalid configuration output path."""

    pass


class ParseScore(BaseModel):
    """Validate a player name and a nonnegative score."""

    name_player: str
    score: int

    @field_validator("name_player")
    @classmethod
    def check_player(cls, value: str) -> str:
        """Validate a name of one to ten alphanumeric or space characters."""
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
        """Reject negative scores and return the validated value."""
        if value < 0:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} Score must be >= 0"
            )

        return value


class ParseHighScore(BaseModel):
    """Validate a collection containing at most ten score records."""

    highscore: list[ParseScore]

    @field_validator("highscore")
    @classmethod
    def check_highscores(
        cls,
        value: list[ParseScore],
    ) -> list[ParseScore]:
        """Reject collections containing more than ten score records."""
        if len(value) > 10:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} Exactly "
                "10 hightscores are required"
            )

        return value


def save_highscore(
    file: Path,
    scores: ParseHighScore,
    name: str,
    score: int,
) -> bool:
    """Save the ten best scores without overwriting on write failure."""
    temporary = file.with_name(file.name + ".tmp")
    try:
        entry = ParseScore(name_player=name.strip(), score=score)
        best_scores = sorted(
            scores.highscore + [entry],
            key=lambda item: item.score,
            reverse=True,
        )[:10]
        updated = ParseHighScore(highscore=best_scores)
        temporary.write_text(
            updated.model_dump_json(indent=4), encoding="utf-8"
        )
        temporary.replace(file)
    except (OSError, ValidationError) as error:
        print(f"Unable to save highscore: {error}")
        return False
    scores.highscore = best_scores
    return True


class LevelConfig(BaseModel):
    """Validate maze dimensions and frightened duration for a level."""

    width: int
    height: int
    escape_time: int
    level_max_time: int

    @field_validator("width")
    @classmethod
    def check_width(cls, value: int) -> int:
        """Validate a maze width between 10 and 43 cells."""
        if value < 10:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} Width must be >= 10"
            )

        if value > 43:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} Width must be <= 40"
            )

        return value

    @field_validator("height")
    @classmethod
    def check_height(cls, value: int) -> int:
        """Validate a maze height between 10 and 20 cells."""
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

    @field_validator("escape_time")
    @classmethod
    def check_escape_time(cls, value: int) -> int:
        """Validate frightened duration between zero and ten seconds."""
        if value < 0:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} escape_time must be <= 0"
            )

        if value > 10:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} escape_time must be >= 10"
            )

        return value

    @field_validator("level_max_time")
    @classmethod
    def check_level_max_time(cls, value: int) -> int:
        """Validate frightened duration between zero and ten seconds."""
        if value < 90:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} level_max_time must be <= 90"
            )

        if value > 180:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} level_max_time must be >= 180"
            )

        return value


def default_levels() -> list[LevelConfig]:
    """Return the ten default level configurations."""
    return [LevelConfig(width=20, height=20, escape_time=6, level_max_time=90),
            LevelConfig(width=22, height=20, escape_time=5, level_max_time=90),
            LevelConfig(width=24, height=20, escape_time=4, level_max_time=90),
            LevelConfig(width=26, height=20, escape_time=3, level_max_time=90),
            LevelConfig(width=28, height=20, escape_time=2, level_max_time=90),
            LevelConfig(width=30, height=20, escape_time=5, level_max_time=90),
            LevelConfig(width=32, height=20, escape_time=2, level_max_time=90),
            LevelConfig(width=34, height=20, escape_time=2, level_max_time=90),
            LevelConfig(width=36, height=20, escape_time=1, level_max_time=90),
            LevelConfig(width=40, height=20, escape_time=0,
                        level_max_time=90),]


class ParseConfig(BaseModel):
    """Validate game settings and supply fallback values."""

    highscore_filename: Path = Path("scores.json")
    levels: list[LevelConfig] = Field(default_factory=default_levels)
    lives: int = 3
    speed_player: int = 100
    speed_ghosts: int = 90
    time_respawn_ghost: int = 3
    pacgum: int = 100
    points_per_pacgum: int = 1
    points_per_super_pacgum: int = 10
    points_per_ghost: int = 15
    seed: int = 42
    perfect: bool = False

    @field_validator("highscore_filename", mode="before")
    @classmethod
    def check_extension(cls, value: Any) -> Path:
        """Return a JSON file path, falling back to scores.json."""
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
        """Return a valid starting life count or the default value."""
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
        """Validate the pellet percentage or return the default value."""
        if type(value) is not int or value < 1 or value > 100:
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

    @field_validator("levels", mode="before")
    @classmethod
    def check_levels(cls, value: Any) -> list[LevelConfig]:
        """Validate at least ten levels or return the default sequence."""
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
        """Validate positive points or use the default for the field."""
        defaults: dict[str, int] = {
            "points_per_pacgum": 1,
            "points_per_super_pacgum": 10,
            "points_per_ghost": 15,
        }

        assert info.field_name is not None
        default_points: int = defaults[info.field_name]

        if type(value) is not int or value < 1:
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}({info.field_name}: {value})"
                f"{Color.RST.value} Points must be an integer "
                "equal to or greater than 1\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}{info.field_name} = {default_points}"
            )
            return default_points

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
        """Validate movement speed or use the default for the field."""
        defaults: dict[str, int] = {
            "speed_player": 100,
            "speed_ghosts": 90,
        }

        assert info.field_name is not None
        default_speed: int = defaults[info.field_name]

        if type(value) is not int or value < 1 or value > 100:
            print(
                f"\n{Color.ORANGE.value}[WARN] "
                f"{Color.RED.value}({info.field_name}: {value})"
                f"{Color.RST.value} Speed must be an integer "
                "between 1 and 100 percent\n"
                f"{Color.MAGENTA.value}[Default value] "
                f"{Color.GREEN.value}{info.field_name} = {default_speed}"
            )
            return default_speed

        return value

    @field_validator("time_respawn_ghost", mode="before")
    @classmethod
    def check_escape_time(cls, value: int) -> int:
        """Validate ghost respawn delay between zero and five seconds."""
        if type(value) is not int or value < 0:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} time_respawn_ghost must be <= 0"
            )

        if type(value) is not int or value > 5:
            raise ValueError(
                f"\n{Color.BLUE.value}[INFO]"
                f"{Color.RST.value} time_respawn_ghost must be >= 5"
            )

        return value

    @field_validator("seed", mode="before")
    @classmethod
    def check_seed(cls, value: Any) -> int:
        """Return an integer seed or the default value of 42."""
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
        """Ensure imperfect maze generation by returning False."""
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
    """Read a commented JSON configuration with validation fallbacks."""
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


def highscore_to_data(
    file: Path,
    create_if_missing: bool = False,
) -> ParseHighScore:
    """Load scores, optionally creating a missing file without a warning."""
    if create_if_missing:
        try:
            with file.open("x", encoding="utf-8") as content:
                content.write(
                    ParseHighScore(highscore=[]).model_dump_json(indent=4)
                )
        except FileExistsError:
            pass
        except OSError as error:
            print(f"Unable to initialize highscores: {error}")
            return ParseHighScore(highscore=[])

    try:
        with open(file, "r", encoding="utf8") as content:

            text: str = content.read()
            if not text.strip():
                return ParseHighScore(highscore=[])

            score_data: object = json.loads(text)
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

    except (OSError, UnicodeError) as error:
        print(f"Unable to load highscores: {error}")
        return ParseHighScore(highscore=[])

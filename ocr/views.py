import re
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from difflib import SequenceMatcher
from enum import Enum
from math import sqrt
from typing import Iterator, List, NamedTuple, Optional

import cv2 as cv
import numpy as np
import pytesseract
from django.contrib.staticfiles import finders
from django.core.files.uploadedfile import UploadedFile
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from PIL import Image, ImageDraw
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class BoundingBox(NamedTuple):
    left: int
    top: int
    right: int
    bottom: int


class Word(NamedTuple):
    level: int
    page_num: int
    block_num: int
    par_num: int
    line_num: int
    word_num: int
    left: int
    top: int
    width: int
    height: int
    conf: Decimal
    text: str

    @property
    def bounding_box(self):
        return (
            self.left,
            self.top,
            self.left + self.width,
            self.top + self.height,
        )

    def crop(self, image: Image.Image) -> Image.Image:
        return image.crop(self.bounding_box)

    def __str__(self):
        return f"[{self.page_num}:{self.block_num}:{self.par_num}:{self.line_num}:{self.word_num}] {self.bounding_box}: {self.text}"


class Line(NamedTuple):
    page_num: int
    block_num: int
    par_num: int
    line_num: int
    words: List[Word]

    @property
    def text(self):
        return " ".join(unit.text for unit in self.words)

    @property
    def bounding_box(self):
        return (
            min(unit.left for unit in self.words),
            min(unit.top for unit in self.words),
            max(unit.left + unit.width for unit in self.words),
            max(unit.top + unit.height for unit in self.words),
        )

    @property
    def weighted_avg_conf(self):
        return sum(unit.conf for unit in self.words) / len(self.words)

    @property
    def avg_conf_by_length(self):
        return sum(unit.conf * len(unit.text) for unit in self.words) / len(
            self.words * len(self.text)
        )

    def crop(self, image: Image.Image) -> Image.Image:
        return image.crop(self.bounding_box)

    def __str__(self):
        return f"[{self.page_num}:{self.block_num}:{self.par_num}:{self.line_num}] {self.bounding_box}: {self.text}"


@dataclass
class FoundTarget:
    left_line: Optional[Line] = None
    left_image: Optional[Image.Image] = None
    right_image: Optional[Image.Image] = None
    found_value: Optional[str] = None


class SearchTerms(Enum):
    DISTANCE_TRAVELED = "Distance"
    POKEMON_CAUGHT = "Pokémon"
    POKESTOPS_SPUN = "PokéStops"
    TOTAL_XP = "Total"


class ActivityViewOCR(APIView):
    parser_classes = [FileUploadParser]
    # authentication_classes = [TokenAuthentication, OAuth2Authentication]
    # permission_classes = [IsAdminUser]
    authentication_classes = []
    permission_classes = []

    def process_words(self, d: dict) -> Iterator[Word]:
        for i in range(len(d["level"])):
            if isinstance(d["text"][i], str) and d["text"][i].strip():
                yield Word(
                    level=d["level"][i],
                    page_num=d["page_num"][i],
                    block_num=d["block_num"][i],
                    par_num=d["par_num"][i],
                    line_num=d["line_num"][i],
                    word_num=d["word_num"][i],
                    left=d["left"][i],
                    top=d["top"][i],
                    width=d["width"][i],
                    height=d["height"][i],
                    conf=Decimal(d["conf"][i]),
                    text=d["text"][i],
                )

    def process_lines(self, words: Iterator[Word]) -> Iterator[Line]:
        lines = defaultdict(list)
        for word in words:
            lines[(word.page_num, word.block_num, word.par_num, word.line_num)].append(word)

        for key, line in lines.items():
            yield Line(*key, words=line)

    @staticmethod
    def pillow_to_cv(image: Image.Image) -> np.ndarray[int, np.dtype[np.generic]]:
        return cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)

    def detect_close_button(self, image: Image.Image) -> BoundingBox:
        img = self.pillow_to_cv(image)
        template_path = finders.find("img/btn_close_normal_dark.png")
        template = self.pillow_to_cv(Image.open(template_path))

        w, h, *_ = template.shape

        method = cv.TM_SQDIFF_NORMED
        # Apply template Matching

        res = cv.matchTemplate(img, template, method)
        _, _, min_loc, _ = cv.minMaxLoc(res)
        top_left = min_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        return BoundingBox(
            left=top_left[0], top=top_left[1], right=bottom_right[0], bottom=bottom_right[1]
        )

    @staticmethod
    def get_distance_between_two_pixels(p1: np.ndarray, p2: np.ndarray) -> float:
        return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def cover_close_button(self, image: Image.Image, close_location: BoundingBox) -> None:
        middle_pixel = np.array(
            [
                (close_location.left + close_location.right) // 2,
                (close_location.top + close_location.bottom) // 2,
            ]
        )
        top_left_pixel = np.array([close_location.left, close_location.top])

        radius = self.get_distance_between_two_pixels(middle_pixel, top_left_pixel)

        new_bounding_box = BoundingBox(
            left=middle_pixel[0] - radius,
            top=middle_pixel[1] - radius,
            right=middle_pixel[0] + radius,
            bottom=middle_pixel[1] + radius,
        )

        draw = ImageDraw.Draw(image)
        draw.ellipse(
            [
                (new_bounding_box.left, new_bounding_box.top),
                (new_bounding_box.right, new_bounding_box.bottom),
            ],
            fill="white",
            outline="white",
        )

    def process_km_text(self, s: str) -> Decimal:
        if s is None:
            return None

        # Distance is in the form of "69,023.2" or "69.023,2". We need to convert it to "69023.2"
        return Decimal(self.strip_non_digits(s)) / 10

    @staticmethod
    def strip_non_digits(s: str) -> int:
        if s is None:
            return None
        return int(re.sub("[^0-9]", "", s))

    def get_stats_from_activity_section(self, image: Image.Image) -> dict:
        image_left = image.crop((0, 0, image.width // 2, image.height))
        image_right = image.crop((image.width // 2, 0, image.width, image.height))

        left_data = pytesseract.image_to_data(
            image_left.convert("RGB"),
            output_type=pytesseract.Output.DICT,
        )

        left_lines = list(self.process_lines(self.process_words(left_data)))

        target_words = iter(
            [
                SearchTerms.DISTANCE_TRAVELED,
                SearchTerms.POKEMON_CAUGHT,
                SearchTerms.POKESTOPS_SPUN,
                SearchTerms.TOTAL_XP,
            ]
        )
        target_word = next(target_words)

        found_targets: dict[str, FoundTarget] = defaultdict(FoundTarget)

        while True:
            if target_word is None:
                break
            for found_target in left_lines:
                if target_word in found_targets:
                    break
                for word in found_target.words:
                    similarity_index = SequenceMatcher(
                        None,
                        word.text,
                        target_word.value,
                    ).ratio()
                    if similarity_index > 0.5:
                        found_targets[target_word].left_line = found_target
                        found_targets[target_word].left_image = found_target.crop(image_left)
                        break

            target_word = next(target_words, None)

        for found_target in found_targets.values():
            line = found_target.left_line
            line_height = line.bounding_box[3] - line.bounding_box[1]
            padding = line_height // 3
            top = line.bounding_box[1] - padding
            bottom = line.bounding_box[3] + padding
            left = 64
            right = image_right.width - 24

            found_target.right_image = image_right.convert("RGB").crop((left, top, right, bottom))
            found_target.found_value = pytesseract.image_to_string(
                found_target.right_image
            ).strip()

        print(found_targets)
        return {
            "total_xp": self.strip_non_digits(
                found_targets[SearchTerms.TOTAL_XP].found_value,
            ),
            "travel_km": self.process_km_text(
                found_targets[SearchTerms.DISTANCE_TRAVELED].found_value,
            ),
            "capture_total": self.strip_non_digits(
                found_targets[SearchTerms.POKEMON_CAUGHT].found_value,
            ),
            "pokestops_visited": self.strip_non_digits(
                found_targets[SearchTerms.POKESTOPS_SPUN].found_value,
            ),
        }

    def put(self, request: Request):
        file_object: UploadedFile = request.data["file"]
        Image.open(file_object).verify()

        image = Image.open(file_object)

        self.cover_close_button(image, self.detect_close_button(image))

        stats = self.get_stats_from_activity_section(image)

        return Response(data=stats, status=200)

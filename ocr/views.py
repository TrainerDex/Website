import re
from collections import defaultdict
from decimal import Decimal
from difflib import SequenceMatcher
from enum import Enum
from typing import Iterator, List, NamedTuple

import pytesseract
from django.core.files.uploadedfile import UploadedFile
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from PIL import Image
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


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

    def crop(self, image: Image.Image) -> Image.Image:
        return image.crop(self.bounding_box)

    def __str__(self):
        return f"[{self.page_num}:{self.block_num}:{self.par_num}:{self.line_num}] {self.bounding_box}: {self.text}"


class SearchPattern(Enum):
    NONE = 0
    KEY = 1
    VALUE = 2


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

    def put(self, request: Request):
        file_object: UploadedFile = request.data["file"]
        Image.open(file_object).verify()

        image = Image.open(file_object)
        image_rgb = image.convert("RGB")
        data = pytesseract.image_to_data(image_rgb, output_type=pytesseract.Output.DICT)

        blocks = self.process_lines(self.process_words(data))

        stats = {}
        target_words = iter(["Distance", "Pokémon", "PokéStops", "Total"])
        target_word = next(target_words)
        search_pattern = SearchPattern.KEY

        for block in blocks:
            if search_pattern == SearchPattern.NONE:
                try:
                    target_word = next(target_words)
                except StopIteration:
                    break
                else:
                    search_pattern = SearchPattern.KEY

            for unit in block.words:
                if search_pattern == SearchPattern.KEY:
                    similarity_index = SequenceMatcher(
                        None,
                        unit.text,
                        target_word,
                    ).ratio()
                    if similarity_index > 0.5:
                        search_pattern = SearchPattern.VALUE

                if search_pattern == SearchPattern.VALUE:
                    if (line := re.sub(r"[^0-9]", "", unit.text)).strip():
                        if target_word == "Distance":
                            # Distance is in the form of "69,023.2" or "69.023,2". We need to convert it to "69023.2"
                            separators = re.sub("[0-9]", "", unit.text)
                            for sep in separators[:-1]:
                                line = unit.text.replace(sep, "")
                            if separators:
                                line = line.replace(separators[-1], ".")
                            stats[target_word] = Decimal(line)
                        else:
                            stats[target_word] = int(line)

                        search_pattern = SearchPattern.NONE

        return Response(data=stats, status=200)

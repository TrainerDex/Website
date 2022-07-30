import re
from collections import defaultdict
from decimal import Decimal
from difflib import SequenceMatcher
from enum import Enum
from typing import List, NamedTuple

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


class Unit(NamedTuple):
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


class Block(NamedTuple):
    page_num: int
    block_num: int
    par_num: int
    line_num: int
    units: List[Unit]

    @property
    def text(self):
        return " ".join(unit.text for unit in self.units)

    @property
    def bounding_box(self):
        return (
            min(unit.left for unit in self.units),
            min(unit.top for unit in self.units),
            max(unit.left + unit.width for unit in self.units),
            max(unit.top + unit.height for unit in self.units),
        )

    def crop(self, image: Image.Image) -> Image.Image:
        return image.crop(self.bounding_box)


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

    def put(self, request: Request):
        file_object: UploadedFile = request.data["file"]
        Image.open(file_object).verify()

        image_rgb = Image.open(file_object).convert("RGB")
        data = pytesseract.image_to_data(image_rgb, output_type=pytesseract.Output.DICT)

        units = [
            Unit(
                level=data["level"][i],
                page_num=data["page_num"][i],
                block_num=data["block_num"][i],
                par_num=data["par_num"][i],
                line_num=data["line_num"][i],
                word_num=data["word_num"][i],
                left=data["left"][i],
                top=data["top"][i],
                width=data["width"][i],
                height=data["height"][i],
                conf=Decimal(data["conf"][i]),
                text=data["text"][i],
            )
            for i in range(len(data["level"]))
        ]
        block_dict = defaultdict(list)
        for unit in units:
            if unit.text.strip():
                block_dict[(unit.page_num, unit.block_num, unit.par_num, unit.line_num)].append(
                    unit
                )
        del units
        blocks = [Block(*key, units=units) for key, units in block_dict.items()]

        stats = {}
        target_words = iter(["Distance", "Pokémon", "PokéStops", "Total"])
        target_word = next(target_words)
        print("Looking for:", target_word)
        search_pattern = SearchPattern.KEY

        for block in blocks:
            if search_pattern == SearchPattern.NONE:
                try:
                    target_word = next(target_words)
                except StopIteration:
                    break
                else:
                    search_pattern = SearchPattern.KEY

            for unit in block.units:
                if search_pattern == SearchPattern.KEY:
                    similarity_index = SequenceMatcher(
                        None,
                        unit.text,
                        target_word,
                    ).ratio()
                    if similarity_index > 0.5:
                        print(f"{unit.text} is similar to {target_word} ({similarity_index})")
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

                        print(f"{target_word} = {line}")
                        search_pattern = SearchPattern.NONE

        return Response(data=stats, status=204)

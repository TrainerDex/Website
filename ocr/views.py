import re
from collections import defaultdict
from decimal import Decimal
from difflib import SequenceMatcher
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

        image_left = image.crop((0, 0, image.width // 2, image.height))
        image_right = image.crop((image.width // 2, 0, image.width, image.height))

        left_data = pytesseract.image_to_data(
            image_left.convert("RGB"),
            output_type=pytesseract.Output.DICT,
        )

        left_lines = list(self.process_lines(self.process_words(left_data)))

        stats = {}
        target_words = iter(["Distance", "Pokémon", "PokéStops", "Total"])
        target_word = next(target_words)

        found_targets: dict[str, Line] = {}

        while True:
            if target_word is None:
                break
            # print("Searching for", target_word)
            for line in left_lines:
                if target_word in found_targets:
                    break
                # print("Processing line:", line)
                for word in line.words:
                    similarity_index = SequenceMatcher(
                        None,
                        word.text,
                        target_word,
                    ).ratio()
                    if similarity_index > 0.5:
                        # print(f"Found {target_word} at {line}")
                        found_targets[target_word] = line
                        if target_word == "Total":
                            print(line)
                            for word in line.words:
                                print(word)
                                word.crop(image_left).show()

                                if word.text == "q":
                                    image.crop(
                                        (
                                            word.left,
                                            word.top,
                                            word.width + (image.width // 2),
                                            word.top + word.height,
                                        )
                                    ).show()
                        break
            target_word = next(target_words, None)

        # right_data = pytesseract.image_to_data(
        #     image_right.convert("RGB"),
        #     output_type=pytesseract.Output.DICT,
        # )
        # right_lines = self.process_lines(self.process_words(left_data))

        new_stat_images: dict[str, Image.Image] = {}
        new_stat_images_str: dict[str, str] = {}

        for target, line in found_targets.items():
            # Crop image to the same vertile space as the line, but the width is the full image width, except the left 64 pixels, to cut out the rubbish, and the right 24 pixels to cut out the border
            line_height = line.bounding_box[3] - line.bounding_box[1]
            padding = 0  # (line_height // image_right.height) ** 0.05
            top = line.bounding_box[1] - padding
            bottom = line.bounding_box[3] + padding
            left = 64
            right = image_right.width - 24

            new_stat_images[target] = image_right.convert("RGB").crop((left, top, right, bottom))
            # new_stat_images[target].show()
            new_stat_images_str[target] = pytesseract.image_to_string(
                new_stat_images[target]
            ).strip()

        print(new_stat_images_str)

        return Response(data=new_stat_images_str, status=200)


# if search_pattern == SearchPattern.VALUE:
#     if (line := re.sub(r"[^0-9]", "", word.text)).strip():
#         if target_word == "Distance":
#             # Distance is in the form of "69,023.2" or "69.023,2". We need to convert it to "69023.2"
#             separators = re.sub("[0-9]", "", word.text)
#             for sep in separators[:-1]:
#                 line = word.text.replace(sep, "")
#             if separators:
#                 line = line.replace(separators[-1], ".")
#             stats[target_word] = Decimal(line)
#         else:
#             stats[target_word] = int(line)

#         search_pattern = SearchPattern.NONE

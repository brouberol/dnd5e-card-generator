import os
import subprocess
import tempfile
from pathlib import Path

from .const import BACKGROUNDS_DIR, NUM_WATERCOLORS, WATERCOLORS_DIR
from .models import MagicSchool


class ImageMagick:
    def __init__(self):
        self.intermediary_files: list[Path] = []

    def __del__(self):
        for f_path in self.intermediary_files:
            try:
                os.unlink(f_path)
            except FileNotFoundError:
                pass

    @staticmethod
    def image_size(image_path: Path):
        cmd = ["identify", "-ping", "-format", "%w %h", image_path]
        cmd_out = subprocess.run(cmd, capture_output=True).stdout
        return map(int, cmd_out.split())

    def resize(self, image_path: Path, result_image_path: Path, resize_factor: str):
        cmd = ["magick", image_path, "-resize", resize_factor, result_image_path]
        self.intermediary_files.append(result_image_path)
        subprocess.run(cmd, capture_output=True)

    def blend(
        self,
        frontground_image_path: Path,
        background_image_path: Path,
        geometry: str,
    ) -> Path:
        with tempfile.NamedTemporaryFile(
            suffix=".png", delete=False, delete_on_close=False
        ) as tmpfile:
            cmd = [
                "convert",
                "-geometry",
                geometry,
                str(background_image_path),
                str(frontground_image_path),
                "-compose",
                "multiply",
                "-composite",
                tmpfile.name,
            ]
            subprocess.run(cmd, capture_output=True)
            self.intermediary_files.append(Path(tmpfile.name))
        return Path(tmpfile.name)

    def to_gray(self, image_path: Path, output_file: Path):
        cmd = [
            "magick",
            image_path,
            "-set",
            "colorspace",
            "Gray",
            "-negate",
            "-background",
            "white",
            "-alpha",
            "shape",
            output_file,
        ]
        subprocess.run(cmd, capture_output=True)
        return output_file

    def compose_magic_school_logo_and_watercolor(
        self, magic_school: MagicSchool
    ) -> Path:
        magic_school_name = magic_school.value
        watercolor_version = (
            list(MagicSchool._member_map_.keys()).index(magic_school_name)
            % NUM_WATERCOLORS
        ) + 1
        watercolor_file_path = WATERCOLORS_DIR / f"watercolor{watercolor_version}.png"
        watercolor_height, watercolor_width = self.image_size(watercolor_file_path)
        resized_magic_school_symbol = Path(
            tempfile.NamedTemporaryFile(
                suffix=".png", delete=False, delete_on_close=False
            ).name
        )
        self.resize(
            image_path=magic_school.symbol_file_path,
            result_image_path=resized_magic_school_symbol,
            resize_factor=f"{watercolor_height}x{watercolor_width}",
        )
        self.resize(
            image_path=resized_magic_school_symbol,
            result_image_path=resized_magic_school_symbol,
            resize_factor="80%",
        )
        resized_magic_school_symbol_height, resized_magic_school_symbol_width = (
            self.image_size(resized_magic_school_symbol)
        )
        geometry_x = int(watercolor_height / 2 - resized_magic_school_symbol_height / 2)
        geometry_y = int(watercolor_width / 2 - resized_magic_school_symbol_width / 2)
        geometry = f"+{geometry_x}+{geometry_y}"
        blended_file = self.blend(
            frontground_image_path=resized_magic_school_symbol,
            background_image_path=watercolor_file_path,
            geometry=geometry,
        )
        final_file = BACKGROUNDS_DIR / f"{magic_school_name}.png"

        self.to_gray(blended_file, final_file)


def main():
    im = ImageMagick()
    for magic_school in MagicSchool:
        im.compose_magic_school_logo_and_watercolor(magic_school)

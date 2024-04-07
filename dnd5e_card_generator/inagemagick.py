import base64
import subprocess
import tempfile
from pathlib import Path

from .const import IMAGES_DIR, NUM_WATERCOLORS
from .models import MagicSchool


class ImageMagick:
    @staticmethod
    def image_size(image_path: Path):
        cmd = ["identify", "-ping", "-format", "%w %h", image_path]
        cmd_out = subprocess.run(cmd, capture_output=True).stdout
        return map(int, cmd_out.split())

    @staticmethod
    def resize(image_path: Path, result_image_path: Path, resize_factor: str):
        cmd = ["magick", image_path, "-resize", resize_factor, result_image_path]
        subprocess.run(cmd, capture_output=True)

    @staticmethod
    def blend(
        frontground_image_path: Path,
        background_image_path: Path,
        geometry: str,
        color: str,
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
                "-colorspace",
                "gray",
                "+level-colors",
                f'"{color}",',
                tmpfile.name,
            ]
            subprocess.run(cmd, capture_output=True)
        return Path(tmpfile.name)

    @staticmethod
    def compose_magic_school_logo_and_watercolor(
        magic_school: MagicSchool, color: str
    ) -> Path:
        magic_school_name = magic_school.value
        watercolor_version = (
            list(MagicSchool._member_map_.keys()).index(magic_school_name)
            % NUM_WATERCOLORS
        ) + 1
        watercolor_file_path = IMAGES_DIR / f"watercolor{watercolor_version}.png"
        watercolor_height, watercolor_width = ImageMagick.image_size(
            watercolor_file_path
        )
        resized_magic_school_symbol = Path(
            tempfile.NamedTemporaryFile(
                suffix=".png", delete=False, delete_on_close=False
            ).name
        )
        ImageMagick.resize(
            image_path=magic_school.symbol_file_path,
            result_image_path=resized_magic_school_symbol,
            resize_factor=f"{watercolor_height}x{watercolor_width}",
        )
        ImageMagick.resize(
            image_path=resized_magic_school_symbol,
            result_image_path=resized_magic_school_symbol,
            resize_factor="80%",
        )
        resized_magic_school_symbol_height, resized_magic_school_symbol_width = (
            ImageMagick.image_size(resized_magic_school_symbol)
        )
        geometry_x = int(watercolor_height / 2 - resized_magic_school_symbol_height / 2)
        geometry_y = int(watercolor_width / 2 - resized_magic_school_symbol_width / 2)
        geometry = f"+{geometry_x}+{geometry_y}"
        result_file = ImageMagick.blend(
            frontground_image_path=resized_magic_school_symbol,
            background_image_path=watercolor_file_path,
            geometry=geometry,
            color=color,
        )
        with open(result_file, "br") as blended_symbol_f:
            return base64.b64encode(blended_symbol_f.read()).decode("utf-8")

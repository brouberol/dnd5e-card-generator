from colorways import gradient_palette, hex2rgb, rgb2hex


def generate_palette(
    colors_hex: list[str], steps: int
) -> list[tuple[float, float, float]]:
    colors_rgb = [hex2rgb(color) for color in colors_hex]
    palette = gradient_palette(colors_rgb, steps)
    return [rgb2hex(col) for col in palette]

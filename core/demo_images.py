"""Procedural "photos" for the demo data: no downloads, no copyrighted material.

Every scene is drawn with Pillow at 2x resolution and scaled down for smooth
edges. `render(scene, seed, **options)` returns a ready-to-save ContentFile.
"""

import io
import math
import random

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFilter

SIZE = 640
SS = 2  # supersampling factor
W = SIZE * SS


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(top, bottom):
    img = Image.new("RGB", (W, W))
    draw = ImageDraw.Draw(img)
    for y in range(W):
        draw.line([(0, y), (W, y)], fill=lerp(top, bottom, y / (W - 1)))
    return img


def glow(img, center, radius, color, strength=0.9, blur=None):
    """Soft light blob (sun, moon, nebula) composited over `img`."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    x, y = center
    ImageDraw.Draw(layer).ellipse([x - radius, y - radius, x + radius, y + radius], fill=color + (int(255 * strength),))
    layer = layer.filter(ImageFilter.GaussianBlur(blur or radius * 0.6))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def ridge(rng, baseline, amplitude, sharp=True):
    """Polyline of a mountain-like ridge across the whole width."""
    phases = [rng.uniform(0, 6.28) for _ in range(3)]
    freqs = [rng.uniform(0.003, 0.006), rng.uniform(0.009, 0.014), rng.uniform(0.02, 0.03)]
    points = []
    for x in range(0, W + 8, 8):
        s = sum(w * (abs(math.sin(x * f / SS * 2 + p)) if sharp else math.sin(x * f / SS * 2 + p))
                for w, f, p in zip((0.55, 0.3, 0.15), freqs, phases))
        points.append((x, baseline - amplitude * s))
    return points


def fill_below(draw, points, bottom, color):
    draw.polygon(points + [(W, bottom), (0, bottom)], fill=color)


def finish(img):
    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, "JPEG", quality=90)
    return buffer.getvalue()


# --------------------------------------------------------------------------- scenes
PALETTES_SUNSET = [
    ((255, 150, 70), (110, 55, 140)),
    ((255, 200, 120), (225, 95, 110)),
    ((250, 130, 100), (50, 45, 115)),
    ((255, 225, 150), (120, 160, 210)),
]


def sunset_mountains(rng, reflection=False, palette=None):
    top, bottom = PALETTES_SUNSET[palette if palette is not None else rng.randrange(len(PALETTES_SUNSET))]
    img = gradient(bottom, top)  # dark sky above, warm glow at the horizon
    horizon = W // 2 if reflection else int(W * 0.72)
    img = glow(img, (rng.randint(W // 4, 3 * W // 4), int(horizon * 0.8)), 170 * SS // 2, (255, 245, 200), 0.95)
    draw = ImageDraw.Draw(img)
    haze = lerp(top, bottom, 0.4)
    for i in range(4):
        t = i / 3
        color = lerp(haze, (18, 18, 40), 0.25 + 0.75 * t)
        base = horizon - (3 - i) * 28 * SS // 2
        fill_below(draw, ridge(rng, base, (90 + 40 * (3 - i)) * SS // 2), horizon if reflection else W, color)
    if reflection:
        top_half = img.crop((0, 0, W, horizon))
        mirrored = top_half.transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(5))
        mirrored = Image.blend(mirrored, Image.new("RGB", mirrored.size, (15, 25, 50)), 0.35)
        img.paste(mirrored.crop((0, 0, W, W - horizon)), (0, horizon))
        draw = ImageDraw.Draw(img)
        for _ in range(60):  # ripples
            y = rng.randint(horizon + 10, W - 10)
            x = rng.randint(0, W)
            draw.line([(x, y), (x + rng.randint(30, 120), y)], fill=(255, 255, 255), width=2)
    return img


def forest(rng, mood="mist"):
    sky = {"mist": ((205, 228, 218), (246, 244, 225)), "dusk": ((60, 80, 110), (240, 170, 120))}[mood]
    img = gradient(*sky)
    img = glow(img, (rng.randint(W // 3, 2 * W // 3), int(W * 0.35)), 150 * SS // 2, (255, 250, 220), 0.8)
    for layer in range(5):
        draw = ImageDraw.Draw(img)
        base = int(W * (0.5 + 0.1 * layer))
        color = lerp((140, 175, 160) if mood == "mist" else (90, 100, 120), (12, 38, 30), layer / 4)
        for _ in range(26 + layer * 6):
            x = rng.randint(-20, W + 20)
            h = rng.randint(110, 230) * SS // 2 * (1 + layer * 0.35)
            w = h * 0.38
            top_y = base - h
            for k in range(4):  # stacked triangles = a pine
                ty = top_y + k * h * 0.2
                tw = w * (0.45 + 0.18 * k)
                draw.polygon([(x, ty), (x - tw, ty + h * 0.34), (x + tw, ty + h * 0.34)], fill=color)
            draw.rectangle([x - 5, base - h * 0.1, x + 5, base + 40], fill=color)
        draw.rectangle([0, base, W, W], fill=color)
        if layer < 4:  # mist between the layers
            fog = Image.new("RGBA", img.size, (0, 0, 0, 0))
            fd = ImageDraw.Draw(fog)
            for y in range(base - 140, base + 40):
                a = int(90 * (1 - abs(y - base + 50) / 90)) if abs(y - base + 50) < 90 else 0
                fd.line([(0, y), (W, y)], fill=(235, 240, 235, max(a, 0)))
            img = Image.alpha_composite(img.convert("RGBA"), fog).convert("RGB")
    return img


def city(rng, mode="night"):
    sky = {"night": ((8, 12, 38), (70, 45, 100)), "dusk": ((70, 50, 120), (255, 150, 90)), "dawn": ((40, 70, 130), (255, 205, 150))}[mode]
    img = gradient(*sky)
    draw = ImageDraw.Draw(img)
    if mode == "night":
        for _ in range(140):
            x, y = rng.randint(0, W), rng.randint(0, int(W * 0.5))
            r = rng.choice([1, 1, 2, 3])
            draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 240))
    img = glow(img, (rng.randint(W // 5, 4 * W // 5), int(W * 0.22)), 55 * SS // 2, (255, 250, 225), 1.0, blur=40)
    for layer, (shade, hmin, hmax) in enumerate([(0.45, 160, 300), (0.25, 120, 360), (0.0, 80, 330)]):
        draw = ImageDraw.Draw(img)
        color = lerp(sky[1], (12, 14, 28), 0.55 + 0.45 * layer / 2)
        x = -rng.randint(0, 60)
        while x < W:
            bw = rng.randint(55, 140) * SS // 2
            bh = rng.randint(hmin, hmax) * SS // 2 * 1.3
            draw.rectangle([x, W - bh, x + bw, W], fill=color)
            if rng.random() < 0.3:  # antenna
                draw.line([(x + bw // 2, W - bh), (x + bw // 2, W - bh - 40)], fill=color, width=4)
            if layer == 2:  # lit windows
                for wy in range(int(W - bh) + 18, W - 10, 26 * SS // 2):
                    for wx in range(x + 12, x + bw - 14, 20 * SS // 2):
                        if rng.random() < 0.45:
                            draw.rectangle([wx, wy, wx + 8, wy + 12], fill=(255, 215, 120))
            x += bw + rng.randint(0, 8)
    return img


def waves(rng, time="day"):
    sky = {"day": ((120, 190, 235), (235, 245, 250)), "sunset": ((90, 70, 140), (255, 170, 110))}[time]
    img = gradient(*sky)
    horizon = int(W * 0.38)
    img = glow(img, (rng.randint(W // 4, 3 * W // 4), horizon - 20), 120 * SS // 2, (255, 245, 210), 0.9)
    draw = ImageDraw.Draw(img)
    sea_far, sea_near = ((70, 150, 190), (6, 55, 105)) if time == "day" else ((200, 110, 110), (25, 25, 70))
    bands = 9
    for i in range(bands):
        t = i / (bands - 1)
        base = horizon + t * (W - horizon) * 0.95
        amp = 8 + 34 * t
        freq = 0.012 - 0.006 * t
        phase = rng.uniform(0, 6.28)
        pts = [(x, base + amp * math.sin(x * freq + phase)) for x in range(0, W + 10, 10)]
        draw.polygon(pts + [(W, W), (0, W)], fill=lerp(sea_far, sea_near, t))
        draw.line(pts, fill=lerp((255, 255, 255), sea_far, 0.35 if time == "day" else 0.6), width=3 + int(t * 4))
    return img


def space(rng, ring=True):
    img = gradient((4, 4, 22), (45, 12, 70))
    for color, n in (((120, 60, 200), 3), ((40, 120, 220), 3), ((220, 70, 150), 2)):
        for _ in range(n):
            img = glow(img, (rng.randint(0, W), rng.randint(0, W)), rng.randint(120, 260), color, 0.35, blur=110)
    draw = ImageDraw.Draw(img)
    for _ in range(420):
        x, y = rng.randint(0, W), rng.randint(0, W)
        r = rng.choice([1, 1, 1, 2, 2, 3])
        c = rng.randint(170, 255)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(c, c, 255 if rng.random() < 0.5 else c))
    cx, cy, r = rng.randint(W // 3, 2 * W // 3), rng.randint(W // 3, 2 * W // 3), rng.randint(130, 190) * SS // 2 * 1.4
    base = rng.choice([(230, 160, 90), (120, 170, 230), (190, 110, 170)])
    if ring:
        draw.ellipse([cx - r * 1.7, cy - r * 0.45, cx + r * 1.7, cy + r * 0.45], outline=(230, 215, 190), width=10)
    for i in range(int(r), 0, -2):  # sphere shading, light from the top-left
        t = 1 - i / r
        off = r * 0.35 * t
        draw.ellipse([cx - i - off, cy - i - off, cx + i - off, cy + i - off], fill=lerp(lerp(base, (0, 0, 20), 0.65), lerp(base, (255, 255, 255), 0.35), t))
    if ring:
        draw.arc([cx - r * 1.7, cy - r * 0.45, cx + r * 1.7, cy + r * 0.45], 0, 180, fill=(240, 228, 205), width=10)
    return img


def wood(rng):
    img = Image.new("RGB", (W, W), (166, 118, 76))
    draw = ImageDraw.Draw(img)
    x = 0
    while x < W:
        w = rng.randint(120, 220)
        tone = lerp((150, 104, 66), (190, 140, 92), rng.random())
        draw.rectangle([x, 0, x + w, W], fill=tone)
        for _ in range(26):
            gx = x + rng.randint(4, w - 4)
            draw.line([(gx, 0), (gx + rng.randint(-8, 8), W)], fill=lerp(tone, (90, 60, 35), 0.35), width=2)
        draw.line([(x, 0), (x, W)], fill=(80, 52, 30), width=4)
        x += w
    return img


def shadowed_disc(img, center, radius, color, rim=None):
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    x, y = center
    ImageDraw.Draw(shadow).ellipse([x - radius + 14, y - radius + 22, x + radius + 14, y + radius + 22], fill=(0, 0, 0, 120))
    img = Image.alpha_composite(img.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(18))).convert("RGB")
    d = ImageDraw.Draw(img)
    d.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)
    if rim:
        d.ellipse([x - radius * 0.86, y - radius * 0.86, x + radius * 0.86, y + radius * 0.86], outline=rim, width=6)
    return img


def flatlay(rng, dish="pasta"):
    img = wood(rng)
    c = W // 2
    img = shadowed_disc(img, (c, c), 420, (246, 244, 238), rim=(222, 218, 208))
    d = ImageDraw.Draw(img)
    if dish == "pasta":
        for i in range(14):  # spaghetti swirl
            r = 250 - i * 14
            d.ellipse([c - r, c - r, c + r, c + r], outline=lerp((240, 205, 110), (220, 170, 70), i / 14), width=14)
        d.ellipse([c - 90, c - 90, c + 90, c + 90], fill=(200, 50, 40))
        for _ in range(9):
            x, y = c + rng.randint(-60, 60), c + rng.randint(-60, 60)
            d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=(60, 140, 60))
    elif dish == "salad":
        for _ in range(60):
            x, y = c + rng.randint(-270, 270), c + rng.randint(-270, 270)
            if math.hypot(x - c, y - c) > 280:
                continue
            r = rng.randint(30, 60)
            d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=lerp((60, 150, 60), (150, 200, 80), rng.random()))
        for _ in range(14):
            x, y = c + rng.randint(-220, 220), c + rng.randint(-220, 220)
            d.ellipse([x - 24, y - 24, x + 24, y + 24], fill=(215, 45, 45))
        for _ in range(8):
            x, y = c + rng.randint(-200, 200), c + rng.randint(-200, 200)
            d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(250, 235, 120))
    else:  # pizza
        d.ellipse([c - 300, c - 300, c + 300, c + 300], fill=(222, 170, 95))
        d.ellipse([c - 270, c - 270, c + 270, c + 270], fill=(210, 60, 45))
        d.ellipse([c - 250, c - 250, c + 250, c + 250], fill=(245, 215, 120))
        for _ in range(16):
            x, y = c + rng.randint(-200, 200), c + rng.randint(-200, 200)
            if math.hypot(x - c, y - c) < 230:
                d.ellipse([x - 34, y - 34, x + 34, y + 34], fill=(190, 40, 40))
        for _ in range(12):
            x, y = c + rng.randint(-200, 200), c + rng.randint(-200, 200)
            if math.hypot(x - c, y - c) < 230:
                d.ellipse([x - 14, y - 22, x + 14, y + 22], fill=(50, 130, 55))
        for a in range(0, 360, 60):
            d.line([(c, c), (c + 300 * math.cos(math.radians(a)), c + 300 * math.sin(math.radians(a)))], fill=(150, 90, 40), width=5)
    return img


def coffee(rng):
    img = Image.new("RGB", (W, W), (225, 222, 216))
    d = ImageDraw.Draw(img)
    for _ in range(40):  # marble veins
        x, y = rng.randint(0, W), rng.randint(0, W)
        d.line([(x, y), (x + rng.randint(-200, 200), y + rng.randint(-200, 200))], fill=(200, 198, 195), width=rng.randint(1, 4))
    c = W // 2
    img = shadowed_disc(img, (c, c), 400, (250, 250, 250), rim=(228, 228, 228))
    img = shadowed_disc(img, (c, c), 260, (255, 255, 255), rim=(225, 225, 225))
    d = ImageDraw.Draw(img)
    d.ellipse([c - 215, c - 215, c + 215, c + 215], fill=(96, 58, 36))
    for i, (r, off) in enumerate([(165, 0), (130, 12), (95, 22), (62, 30), (30, 36)]):  # latte-art rings
        d.ellipse([c - r, c - r - off, c + r, c + r - off], fill=(244, 228, 205) if i % 2 == 0 else (150, 96, 62))
    d.rectangle([c + 250, c - 24, c + 400, c + 24], fill=(255, 255, 255), outline=(225, 225, 225), width=5)
    return img


def bauhaus(rng):
    colors = [(222, 52, 38), (245, 197, 48), (36, 84, 168), (24, 24, 24), (240, 232, 214)]
    img = Image.new("RGB", (W, W), (240, 232, 214))
    d = ImageDraw.Draw(img)
    n = 3
    cell = W // n
    for gy in range(n):
        for gx in range(n):
            x0, y0 = gx * cell, gy * cell
            x1, y1 = x0 + cell, y0 + cell
            bg, fg = rng.sample(colors, 2)
            d.rectangle([x0, y0, x1, y1], fill=bg)
            shape = rng.choice(["circle", "half", "quarter", "tri", "stripes", "ring"])
            if shape == "circle":
                d.ellipse([x0 + 30, y0 + 30, x1 - 30, y1 - 30], fill=fg)
            elif shape == "half":
                d.pieslice([x0 + 20, y0 + 20, x1 - 20, y1 + cell - 20], 180, 360, fill=fg)
            elif shape == "quarter":
                d.pieslice([x0 - cell, y0 - cell, x1, y1], 0, 90, fill=fg)
            elif shape == "tri":
                d.polygon([(x0 + 20, y1 - 20), (x1 - 20, y1 - 20), (x0 + cell // 2, y0 + 20)], fill=fg)
            elif shape == "stripes":
                for k in range(0, cell, 36):
                    d.rectangle([x0, y0 + k, x1, y0 + k + 18], fill=fg)
            else:
                d.ellipse([x0 + 20, y0 + 20, x1 - 20, y1 - 20], outline=fg, width=36)
    return img


def garden(rng, palette="spring"):
    img = gradient((70, 130, 70), (24, 80, 52))
    d = ImageDraw.Draw(img)
    for _ in range(60):  # leaves
        x, y = rng.randint(0, W), rng.randint(0, W)
        a, b = rng.randint(30, 70), rng.randint(14, 26)
        d.ellipse([x - a, y - b, x + a, y + b], fill=lerp((40, 110, 60), (110, 170, 80), rng.random()))
    petals = {"spring": [(250, 190, 205), (255, 255, 255), (200, 160, 235)], "summer": [(255, 215, 60), (255, 140, 60), (255, 90, 90)]}[palette]
    for _ in range(14):
        x, y, r = rng.randint(60, W - 60), rng.randint(60, W - 60), rng.randint(40, 90)
        color = rng.choice(petals)
        for k in range(8):
            a = k * math.pi / 4
            px, py = x + r * 0.8 * math.cos(a), y + r * 0.8 * math.sin(a)
            d.ellipse([px - r * 0.55, py - r * 0.55, px + r * 0.55, py + r * 0.55], fill=color, outline=lerp(color, (0, 0, 0), 0.15), width=2)
        d.ellipse([x - r * 0.4, y - r * 0.4, x + r * 0.4, y + r * 0.4], fill=(250, 200, 40))
    return img


SCENES = {
    "sunset": sunset_mountains,
    "forest": forest,
    "city": city,
    "waves": waves,
    "space": space,
    "flatlay": flatlay,
    "coffee": coffee,
    "bauhaus": bauhaus,
    "garden": garden,
}


def render(scene, seed, **options):
    """Draw `scene` and return it as a ContentFile (JPEG)."""
    rng = random.Random(seed)
    img = SCENES[scene](rng, **options)
    return ContentFile(finish(img), name=f"{scene}-{seed}.jpg")


def avatar(colors, seed=0):
    """Neutral head-and-shoulders avatar on a gradient."""
    top, bottom, figure = colors
    size = 320
    img = Image.new("RGB", (size, size))
    d = ImageDraw.Draw(img)
    for y in range(size):
        d.line([(0, y), (size, y)], fill=lerp(top, bottom, y / (size - 1)))
    d.ellipse([size * 0.2, size * 0.78, size * 0.8, size * 1.5], fill=figure)
    d.ellipse([size * 0.34, size * 0.22, size * 0.66, size * 0.6], fill=figure)
    buffer = io.BytesIO()
    img.save(buffer, "JPEG", quality=90)
    return ContentFile(buffer.getvalue(), name=f"avatar-{seed}.jpg")

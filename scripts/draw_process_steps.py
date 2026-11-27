"""Draw process cross-sections in one coordinate system for both readers."""

from process_steps import MATERIALS

INK = "#243b4b"
PAPER = "#f4f8fa"


def color(key):
    return MATERIALS[key][1]


def rect(x, y, width, height, fill, motion=""):
    return (f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'fill="{fill}" rx="2" class="{motion}"/>')


def path(d, stroke, width=3, fill="none", motion="", dash=""):
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round" '
            f'class="{motion}" stroke-dasharray="{dash or "none"}"/>')


def dot(x, y, radius, fill, motion=""):
    return f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{fill}" class="{motion}"/>'


def down(x, y1, y2, stroke, motion="travel"):
    return path(f"M{x} {y1}V{y2}m-6-7 6 7 6-7", stroke, motion=motion)


def measure(x1, x2, y):
    return path(
        f"M{x1} {y}H{x2}m-8-5 8 5-8 5 M{x1 + 8} {y - 5}l-8 5 8 5",
        INK, 2, motion="reveal",
    )


def heat(y):
    return "".join(
        path(f"M{x} {y}c-11-8 11-14 0-22s11-14 0-22", "#ba572f", motion="heat")
        for x in (190, 230, 270, 310)
    )


def silicon(top=160):
    return rect(67, top, 366, 56, color("silicon"))


def mask(y):
    return (
        rect(67, y, 132, 24, color("resist"))
        + rect(301, y, 132, 24, color("resist"))
    )


def lithography(step):
    parts = [silicon(), rect(67, 130, 366, 30, color("film"))]
    if 1 <= step <= 5:
        parts.append(rect(67, 106, 366, 24, color("resist"), "spread" if step == 1 else ""))
    if step in (2, 5):
        parts.append(heat(87))
    if step in (3, 4):
        parts.extend([rect(109, 36, 90, 12, INK), rect(301, 36, 90, 12, INK)])
    if step == 3:
        for x in (132, 367):
            parts.append(path(f"M{x} 30V193m-9-17h18", "#913c4d", 2, motion="reveal", dash="5 6"))
    if step in (4, 5):
        parts.append(rect(199, 106, 102, 24, color("exposed"), "reveal" if step == 4 else ""))
    if step == 4:
        parts.extend(down(x, 53, 98, "#a66b16") for x in (214, 238, 262, 286))
    if step in (6, 7):
        parts.append(mask(106))
    if step == 6:
        parts.extend([dot(224, 82, 5, color("resist"), "lift"),
                      dot(248, 72, 6, color("resist"), "lift"),
                      dot(276, 84, 4, color("resist"), "lift")])
    if step == 7:
        parts.append(measure(199, 301, 89))
    return "".join(parts)


def etching(step):
    parts = [silicon()]
    if step == 0:
        parts.append(rect(67, 130, 366, 30, color("film")))
    else:
        parts.extend([rect(67, 130, 132, 30, color("film")),
                      rect(301, 130, 132, 30, color("film"))])
        if step == 1:
            parts.append(rect(199, 145, 102, 15, color("film")))
    if step < 3:
        parts.append(mask(106))
    if step in (1, 2):
        parts.extend(down(x, 62, 123 if step == 1 else 148, "#146c75") for x in (224, 250, 276))
    if step == 2:
        parts.append(path("M199 160H301", INK, 2, motion="reveal", dash="5 5"))
    if step == 3:
        parts.extend(dot(x, y, 5, color("resist"), "lift") for x, y in ((115, 86), (157, 76), (352, 84), (385, 72)))
    if step == 4:
        parts.extend([measure(199, 301, 111),
                      path("M199 117V167 M301 117V167", INK, 1.6, dash="3 4")])
    return "".join(parts)


def implantation(step):
    parts = [silicon()]
    if step < 3:
        parts.append(mask(136))
    teal = color("dopant")
    if step == 1:
        paths = ("M84 66Q166 66 205 47T345 34",
                 "M84 66H379", "M84 66Q166 66 205 85T345 99")
        for stroke, route in zip(("#b86150", teal, "#67659a"), paths):
            parts.append(path(route, stroke, 4, motion="reveal"))
        parts.append(rect(350, 52, 25, 28, "none"))
        parts.append(path("M350 53H380V80H350Z", INK, 2))
    if step == 2:
        parts.extend(down(x, 68, 178, teal) for x in (213, 237, 263, 287))
    if step >= 2:
        points = [(207, 178), (218, 190), (224, 181), (233, 197), (238, 186),
                  (251, 176), (253, 188), (256, 199), (268, 181), (272, 190),
                  (282, 199), (284, 179), (296, 188)]
        if step >= 4:
            points = [(x, 176 + (y - 176) // 8 * 8) for x, y in points]
        parts.extend(dot(x, y, 4.3, teal, "reveal" if step in (2, 4) else "") for x, y in points)
    if step == 4:
        parts.append(heat(137))
    if step == 5:
        parts.append(path("M122 92l27 29 34 39 M165 92l27 29 34 39 M335 92l-27 29-34 39 M378 92l-27 29-34 39",
                          INK, 3, motion="travel"))
    return "".join(parts)


def cmp(step):
    green = color("dielectric")
    if step == 1:
        return "".join([
            rect(105, 45, 275, 48, INK),
            rect(144, 94, 198, 22, color("silicon")),
            rect(144, 117, 198, 13, green),
            rect(65, 130, 358, 30, color("pad")),
            rect(65, 160, 358, 28, color("silicon")),
            down(243, 13, 40, INK),
            path("M415 63l-48 49", INK, 6),
            *(dot(x, y, 5, color("slurry"), "travel") for x, y in ((347, 126), (364, 125), (333, 129))),
            path("M100 156H393m-11-5 11 5-11 5", "#fff", 2),
        ])
    parts = [silicon(), rect(67, 132, 366, 28, green),
             path("M59 132H441", INK, 2, dash="6 6")]
    if step in (0, 2):
        depth = 55 if step == 0 else 23
        for x, width in ((98, 130), (307, 89)):
            parts.append(rect(x, 132 - depth, width, depth, green, "reveal" if step == 2 else ""))
    if step == 2:
        parts.extend(down(x, 55, 94, "#146c75") for x in (127, 190, 330, 370))
    if step == 4:
        for x in (124, 250, 376):
            parts.extend([path(f"M{x} 96v30", INK, 2, motion="travel"), dot(x, 132, 4, INK)])
    return "".join(parts)


def copper(step):
    parts = [silicon(166), rect(145, 150, 203, 16, color("copper")),
             rect(67, 150, 78, 16, color("dielectric")),
             rect(348, 150, 85, 16, color("dielectric")),
             rect(67, 67, 366, 83, color("dielectric"))]
    if step == 0:
        return "".join(parts)
    hole = "M151 67H349V103H271V150H229V103H151Z"
    boundary = "M151 67V103H229V150H271V103H349V67"
    parts.append(path(hole, "none", 0, PAPER))
    if step >= 2:
        parts.append(path(boundary, color("barrier"), 7, motion="trace" if step == 2 else ""))
    if step >= 3:
        parts.append(path("M156 67V98H234V145H266V98H344V67", color("seed"), 4,
                          motion="trace" if step == 3 else ""))
    if step >= 4:
        parts.append(path("M159 67H341V96H263V143H237V96H159Z", "none", 0,
                          color("copper"), motion="fill-up" if step == 4 else ""))
    if step in (4, 5):
        parts.append(rect(67, 52, 366, 15, color("copper"), "spread" if step == 4 else ""))
    if step == 5:
        parts.append(heat(50))
    if step == 6:
        parts.append(rect(67, 61, 366, 6, PAPER))
        parts.append(path("M61 67H439", INK, 1.6, dash="6 5", motion="reveal"))
    if step == 7:
        parts.append(rect(67, 55, 366, 12, color("cap"), "spread"))
    return "".join(parts)


DRAW = {"lithography": lithography, "etching": etching,
        "implantation": implantation, "cmp": cmp, "copper": copper}


def svg(process, index):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 240" aria-hidden="true">'
        + rect(0, 0, 500, 240, PAPER) + DRAW[process](index) + "</svg>"
    )

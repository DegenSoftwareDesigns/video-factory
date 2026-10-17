#!/usr/bin/env python3
"""Rebuild the known SVG brand assets from brand.json and source/mascot.svg.

Run with Python 3.12; no third-party packages, network calls, or AI models required.
Generated files in assets/ are overwritten. Source artwork and documents are kept.
"""
import copy
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)


def element(parent, tag, attrs=None, text=None):
    node = ET.SubElement(parent, f"{{{NS}}}{tag}", {key: str(value) for key, value in (attrs or {}).items()})
    node.text = text
    return node


def canvas(width, height, title, definitions=None):
    svg = ET.Element(f"{{{NS}}}svg", {"viewBox": f"0 0 {width} {height}", "role": "img", "aria-label": title})
    element(svg, "title", text=title)
    if definitions is not None:
        svg.append(copy.deepcopy(definitions))
    return svg


def write_asset(name, svg):
    path = ROOT / "assets" / name
    path.parent.mkdir(exist_ok=True)
    ET.indent(svg, space="  ")
    path.write_text(ET.tostring(svg, encoding="unicode") + "\n", encoding="utf-8")
    print(path.relative_to(ROOT))


def main():
    config = json.loads((ROOT / "brand.json").read_text(encoding="utf-8"))
    palette = config["palette"]
    source = ET.parse(ROOT / "source/mascot.svg").getroot()
    for node in source.iter():
        for attribute in ("fill", "stroke"):
            token = node.get(f"data-{attribute}")
            if token:
                node.set(attribute, palette[token])
    definitions = source.find(f"{{{NS}}}defs")
    if definitions is None:
        raise ValueError("Source artwork must contain reusable SVG definitions")
    mascot = config["mascot_name"]
    name = config["name"]
    primary = canvas(256, 256, f"{mascot}: primary approved artwork", definitions)
    element(primary, "use", {"href": "#front", "width": 256, "height": 256})
    write_asset("mascot.svg", primary)
    mark = canvas(256, 256, f"{name}: standalone symbol", definitions)
    element(mark, "use", {"href": "#mark", "width": 256, "height": 256})
    write_asset("mark.svg", mark)
    logo = canvas(760, 180, f"{name}: horizontal logo", definitions)
    element(logo, "use", {"href": "#mark", "width": 180, "height": 180})
    element(logo, "text", {"x": 183, "y": 126, "fill": palette["ink"], "font-family": config["typography"]["display"],
                           "font-size": min(98, 760 / max(len(name), 1)), "font-weight": 900, "letter-spacing": -5}, name)
    write_asset("logo.svg", logo)

    sheets = [
        ("turnaround.svg", "Turnaround", [("front", "01 / FRONT"), ("three-quarter", "02 / THREE-QUARTER"), ("side", "03 / SIDE"), ("back", "04 / BACK")]),
        ("expressions.svg", "Expressions", [("front", "01 / NEUTRAL"), ("happy", "02 / HAPPY"), ("focused", "03 / FOCUSED"), ("surprised", "04 / SURPRISED")]),
        ("poses.svg", "Poses", [("front", "01 / STAND"), ("wave", "02 / WAVE"), ("run", "03 / RUN")]),
    ]
    for filename, title, views in sheets:
        width, height = len(views) * 280 + 48, 400
        svg = canvas(width, height, f"{mascot}: {title.lower()} reference sheet", definitions)
        element(svg, "rect", {"width": width, "height": height, "fill": palette["paper"]})
        element(svg, "text", {"x": 32, "y": 41, "fill": palette["ink"], "font-family": config["typography"]["label"], "font-size": 17}, f"{name} / {mascot.upper()} / {title.upper()}")
        for index, (view, label) in enumerate(views):
            x = 24 + index * 280
            element(svg, "line", {"x1": x + 10, "x2": x + 250, "y1": 299, "y2": 299, "stroke": palette["line"]})
            element(svg, "use", {"href": f"#{view}", "x": x, "y": 62, "width": 256, "height": 256})
            element(svg, "text", {"x": x + 128, "y": 350, "text-anchor": "middle", "fill": palette["ink"],
                                  "font-family": config["typography"]["label"], "font-size": 15}, label)
        write_asset(filename, svg)

    background = canvas(1080, 1440, f"{name}: paper and spark background")
    element(background, "rect", {"width": 1080, "height": 1440, "fill": palette["paper"]})
    element(background, "circle", {"cx": 940, "cy": 220, "r": 430, "fill": palette["sun"]})
    element(background, "circle", {"cx": 100, "cy": 1410, "r": 290, "fill": palette["mint"]})
    write_asset("background.svg", background)


if __name__ == "__main__":
    main()

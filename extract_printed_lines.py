import os
import csv
import xml.etree.ElementTree as ET
from typing import Tuple, List

from PIL import Image


PAGE_NS = {"pc": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}

# Output folder for cropped machine-printed text lines
OUT_DIR = "GRPOLY_printed_lines"
CSV_NAME = "printed_lines.csv"


def parse_points(points_str: str) -> Tuple[int, int, int, int]:
    """
    Convert PAGE-style polygon string:
      \"x1,y1 x2,y2 ...\"
    into a bounding box (xmin, ymin, xmax, ymax).
    """
    pts: List[Tuple[int, int]] = []
    for p in points_str.split():
        try:
            x_str, y_str = p.split(",")
            pts.append((int(x_str), int(y_str)))
        except ValueError:
            # Skip malformed point
            continue

    if not pts:
        raise ValueError("No valid points in string: ...")

    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]
    return min(xs), min(ys), max(xs), max(ys)


def extract_lines_for_page(
    xml_path: str,
    image_root: str,
    subset_prefix: str,
    writer: csv.writer,
) -> None:
    """
    Given a PAGE XML file and its corresponding page image, crop all TextLine
    regions, save them as PNGs, and write (filename, text) rows to CSV.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    page = root.find("pc:Page", PAGE_NS)
    if page is None:
        return

    image_filename = page.get("imageFilename")
    if not image_filename:
        return

    image_path = os.path.join(image_root, image_filename)
    if not os.path.exists(image_path):
        print(f"[WARN] Image not found for {xml_path}: {image_path}")
        return

    image = Image.open(image_path).convert("RGB")
    base = os.path.splitext(os.path.basename(image_filename))[0]

    for text_line in page.findall(".//pc:TextLine", PAGE_NS):
        line_id = text_line.get("id") or "line"

        coords_el = text_line.find("pc:Coords", PAGE_NS)
        if coords_el is None:
            continue

        points = coords_el.get("points")
        if not points:
            continue

        try:
            x_min, y_min, x_max, y_max = parse_points(points)
        except ValueError as e:
            print(f"[WARN] Skipping line {line_id} in {xml_path}: {e}")
            continue

        # Crop the line region (add +1 to include max index)
        crop = image.crop((x_min, y_min, x_max + 1, y_max + 1))

        # Prefer line-level TextEquiv if present
        text_equiv = text_line.find("pc:TextEquiv/pc:Unicode", PAGE_NS)
        if text_equiv is not None and text_equiv.text and text_equiv.text.strip():
            text = text_equiv.text.strip()
        else:
            # Fallback: concatenate word-level Unicode strings
            words: List[str] = []
            for word_el in text_line.findall("pc:Word", PAGE_NS):
                u_el = word_el.find("pc:TextEquiv/pc:Unicode", PAGE_NS)
                if u_el is not None and u_el.text:
                    w = u_el.text.strip()
                    if w:
                        words.append(w)
            text = " ".join(words)

        if not text:
            # No usable text for this line
            continue

        out_name = f"{subset_prefix}_{base}_{line_id}.png"
        out_path = os.path.join(OUT_DIR, out_name)
        os.makedirs(OUT_DIR, exist_ok=True)
        crop.save(out_path)

        writer.writerow([out_name, text])


def main():
    """
    Extract machine-printed line images and texts from GRPOLY PAGE XML.

    Creates:
      - GRPOLY_printed_lines/ (cropped PNGs)
      - GRPOLY_printed_lines/printed_lines.csv (filename,text)
    """
    subsets = [
        ("MPA", "GRPOLY_Dataset/GRPOLY-DB-MachinePrinted-A"),
        ("MPB1", "GRPOLY_Dataset/GRPOLY-DB-MachinePrinted-B1"),
        ("MPB2", "GRPOLY_Dataset/GRPOLY-DB-MachinePrinted-B2"),
        ("MPB3", "GRPOLY_Dataset/GRPOLY-DB-MachinePrinted-B3"),
        ("MPB4", "GRPOLY_Dataset/GRPOLY-DB-MachinePrinted-B4"),
        ("MPC", "GRPOLY_Dataset/GRPOLY-DB-MachinePrinted-C"),
    ]

    os.makedirs(OUT_DIR, exist_ok=True)
    csv_path = os.path.join(OUT_DIR, CSV_NAME)

    total_lines = 0

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "text"])

        for prefix, root_dir in subsets:
            if not os.path.isdir(root_dir):
                print(f"[WARN] Skipping missing subset dir: {root_dir}")
                continue

            for fname in os.listdir(root_dir):
                if not fname.lower().endswith(".xml"):
                    continue
                xml_path = os.path.join(root_dir, fname)
                before = total_lines
                extract_lines_for_page(xml_path, root_dir, prefix, writer)
                # We don't know exactly how many lines per file; count by file size change later if needed.
                # For now, just continue.

    print(f" Finished extracting machine-printed lines into '{OUT_DIR}'.")
    print(f"   CSV written to: {csv_path}")


if __name__ == "__main__":
    main()



"""
Extract line-level images and text from GRPOLY handwritten dataset

"""

from xml.etree import ElementTree as ET
from pathlib import Path
import cv2
import numpy as np
import csv

PAGE_NS = {'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}

def parse_polygon_coords(coords_str):
    """Parse polygon coordinates and return bounding box (x_min, y_min, x_max, y_max)"""
    points = []
    coords_list = coords_str.strip().split()
    for point in coords_list:
        x, y = map(int, point.split(','))
        points.append((x, y))
    
    if not points:
        return None
    
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))


pages_handwritten = Path('GRPOLY_Dataset/GRPOLY-DB-Handwritten')
out = Path("GRPOLY_Dataset/GRPOLY-DB-Handwritten/lines")
out.mkdir(exist_ok=True)
manifest_path = Path("GRPOLY_Dataset/manifest.csv")

# Create manifest file using csv module for proper escaping
with open(manifest_path, 'w', encoding='utf-8', newline='') as manifest_file:
    csv_writer = csv.writer(manifest_file, quoting=csv.QUOTE_MINIMAL) # QUOTE_MINIMAL is used to escape special characters
    csv_writer.writerow(['image_filename', 'line_text'])  # CSV header
    
    # Process each page
    for xml_page in pages_handwritten.glob('*.xml'):
        tree = ET.parse(xml_page)
        root = tree.getroot()
        
        # Image file has same name as XML but with .JPG extension
        image_path = xml_page.with_suffix('.jpg')
        if not image_path.exists():
            print(f"Image not found for {xml_page.name}")
            continue
        
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Could not load image: {image_path}")
            continue
        
        # Process each TextLine
        for line_elem in root.findall('.//ns:TextLine', PAGE_NS):
            line_id = line_elem.get('id', 'unknown') # 
            
            # Get TextLine coordinates
            coords_elem = line_elem.find('ns:Coords', PAGE_NS)
            if coords_elem is None:
                continue
            
            coords_str = coords_elem.get('points', '')
            if not coords_str:
                continue
            
            bbox = parse_polygon_coords(coords_str)
            if bbox is None:
                continue
            
            words = []
            for word_elem in line_elem.findall('.//ns:Word', PAGE_NS):
                text_equiv = word_elem.find('ns:TextEquiv/ns:Unicode', PAGE_NS)
                if text_equiv is not None and text_equiv.text:
                    words.append(text_equiv.text.strip())
            
            if not words:
                continue
            # Concatenate all Words
            line_text = ' '.join(words)
            
            # Extract line image using bounding box
            x_min, y_min, x_max, y_max = bbox
            padding = 5 # padding is the amount of padding to add to the bounding box
            h, w = image.shape[:2]
            x_min = max(0, x_min - padding)
            y_min = max(0, y_min - padding)
            x_max = min(w, x_max + padding)
            y_max = min(h, y_max + padding)
            
            line_image = image[y_min:y_max, x_min:x_max]
            
            if line_image.size == 0:
                continue
            
            # Save line image
            output_filename = f"{xml_page.stem}_{line_id}.png"
            output_path = out / output_filename
            cv2.imwrite(str(output_path), line_image)
            
            # Write to manifest using csv.writer for proper escaping
            csv_writer.writerow([output_filename, line_text])
            
            print(f"Extracted: {output_filename} -> {line_text[:50]}...")

print(f"\nDone! Line images saved to: {out}")
print(f"Manifest saved to: {manifest_path}")



"""
Extract complete vocabulary from machine-printed Greek dataset
"""
import unicodedata
from xml.etree import ElementTree as ET
from pathlib import Path
import json

PAGE_NS = {'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}

# Directories with machine-printed data
machine_dirs = [
    'GRPOLY_Dataset/GRPOLY-DB-MachinePrinted-A',
    'GRPOLY_Dataset/GRPOLY-DB-MachinePrinted-B1',
    'GRPOLY_Dataset/GRPOLY-DB-MachinePrinted-B2',
    'GRPOLY_Dataset/GRPOLY-DB-MachinePrinted-B3',
    'GRPOLY_Dataset/GRPOLY-DB-MachinePrinted-B4',
    'GRPOLY_Dataset/GRPOLY-DB-MachinePrinted-C',
]

vocab = set()
word_count = 0


for dir_path in machine_dirs:
    dir_path = Path(dir_path) # go through each machine printed
    
    xml_files = list[Path](dir_path.glob('*.xml'))   
    for xml_file in xml_files:# go through each xml or page
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Find all text within xml page 
            
            for unicode_elem in root.findall('.//ns:Unicode', PAGE_NS):
                if unicode_elem.text:
                    text = unicode_elem.text.strip()
                    vocab.update(text) # update  
                    word_count += 1
        
        except Exception as e:
            print(f"Error processing {xml_file.name}: {e}")
            continue
vocab = sorted(list(vocab)) 

# ------------------------------------------------------------

# Check what's in your vocab
english_chars = []
greek_chars = []
other_chars = []

for char in vocab:
    try:
        name = unicodedata.name(char)
        if 'LATIN' in name:
            english_chars.append(char)
        elif 'GREEK' in name:
            greek_chars.append(char)
        else:
            other_chars.append(char)
    except:
        other_chars.append(char)

print(f"English/Latin: {len(english_chars)} - {english_chars}")
print(f"Greek: {len(greek_chars)} - {greek_chars}")
print(f"Other: {len(other_chars)} - {other_chars}")

#---

# Save vocabulary to JSON
vocab_data = {
    'vocab': greek_chars,
    'vocab_size': len(greek_chars),
    'char_to_idx': {char: idx+1 for idx, char in enumerate(greek_chars)},  # 0 reserved for CTC blank
}
vocab_data['char_to_idx'][''] = 0  # CTC blank token

with open('vocabulary.json', 'w', encoding='utf-8') as f:
    json.dump(vocab_data, f, ensure_ascii=False, indent=2)

# ------------------------------------------------------------

# Load your existing vocabulary
with open('vocabulary.json', 'r', encoding='utf-8') as f:
    vocab_data = json.load(f)

# Create TrOCR-compatible vocabulary with special tokens
trocr_vocab = {
    '<pad>': 0,
    '<s>': 1,      # Start token
    '</s>': 2,     # End token  
    '<unk>': 3,    # Unknown
}

# Add your Greek characters (offset by 4 for special tokens)
char_to_idx = vocab_data['char_to_idx']
for char, idx in char_to_idx.items():
    if char:  # Skip empty string
        trocr_vocab[char] = idx + 4  # Offset for special tokens

# Create reverse mapping
idx_to_char = {v: k for k, v in trocr_vocab.items()}

print(f"Original vocab size: {vocab_data['vocab_size']}")
print(f"TrOCR vocab size (with special tokens): {len(trocr_vocab)}")

# Save TrOCR vocabulary
with open('trocr_vocab.json', 'w', encoding='utf-8') as f:
    json.dump({
        'char_to_idx': trocr_vocab,
        'idx_to_char': idx_to_char,
        'vocab_size': len(trocr_vocab)
    }, f, ensure_ascii=False, indent=2)

print("✓ Saved trocr_vocab.json")
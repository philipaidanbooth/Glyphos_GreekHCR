#!/usr/bin/env python3
"""Update vocabulary to include all characters from handwritten dataset"""
import pandas as pd
import json

# Load existing vocabulary
with open('trocr_vocab.json', 'r', encoding='utf-8') as f:
    vocab_data = json.load(f)

existing_chars = set(vocab_data['char_to_idx'].keys())
# Keep special tokens
special_tokens = {'<pad>', '<s>', '</s>', '<unk>'}
existing_greek_chars = existing_chars - special_tokens

# Load handwritten dataset to get all characters
train_df = pd.read_csv('train_split.csv')
test_df = pd.read_csv('test_split.csv')
all_text = ''.join(train_df.iloc[:, 1].astype(str)) + ''.join(test_df.iloc[:, 1].astype(str))
all_chars_in_data = set(all_text)

# Combine existing vocab with characters from data
all_chars = existing_greek_chars | all_chars_in_data

# Sort characters: special tokens first, then Greek, then others
special_tokens_list = ['<pad>', '<s>', '</s>', '<unk>']
greek_chars = sorted([c for c in all_chars if ord(c) >= 0x0370])  # Greek Unicode range
other_chars = sorted([c for c in all_chars if ord(c) < 0x0370 and c not in special_tokens])

# Create new vocabulary
new_char_to_idx = {}
new_idx_to_char = {}

# Add special tokens
for idx, token in enumerate(special_tokens_list):
    new_char_to_idx[token] = idx
    new_idx_to_char[idx] = token

# Add all other characters
current_idx = len(special_tokens_list)
for char in greek_chars + other_chars:
    new_char_to_idx[char] = current_idx
    new_idx_to_char[current_idx] = char
    current_idx += 1

# Create updated vocab data
updated_vocab = {
    'char_to_idx': new_char_to_idx,
    'idx_to_char': {str(k): v for k, v in new_idx_to_char.items()},
    'vocab_size': len(new_char_to_idx)
}

# Save updated vocabulary
with open('trocr_vocab.json', 'w', encoding='utf-8') as f:
    json.dump(updated_vocab, f, ensure_ascii=False, indent=2)

print(f"✓ Updated vocabulary!")
print(f"  Old size: {vocab_data['vocab_size']}")
print(f"  New size: {updated_vocab['vocab_size']}")
print(f"  Added: {updated_vocab['vocab_size'] - vocab_data['vocab_size']} characters")
print(f"\n  Special tokens: {len(special_tokens_list)}")
print(f"  Greek characters: {len(greek_chars)}")
print(f"  Other characters (punctuation, Latin, digits): {len(other_chars)}")
print(f"\n✓ Saved to trocr_vocab.json")







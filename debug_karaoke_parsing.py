#!/usr/bin/env python3
"""
Debug script to test karaoke timing parsing from ASS
"""

import sys
import os
import re

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from subtitle_creator.models import WordTiming, ValidationError

def parse_karaoke_timing(text: str) -> list:
    """Parse karaoke timing tags from ASS text."""
    words = []
    current_time = 0.0
    
    print(f"Parsing karaoke from: '{text}'")
    
    # Find all karaoke tags {\kXX} where XX is centiseconds
    parts = re.split(r'\{\\k(\d+)\}', text)
    print(f"Split into parts: {parts}")
    
    for i in range(1, len(parts), 2):  # Every odd index has timing
        if i + 1 < len(parts):
            duration_cs = int(parts[i])  # Duration in centiseconds
            word_text = parts[i + 1].strip()
            
            print(f"  Part {i}: duration={duration_cs}cs, text='{word_text}'")
            
            if word_text:  # Skip empty words
                duration_s = duration_cs / 100.0  # Convert to seconds
                
                try:
                    word = WordTiming(
                        word=word_text,
                        start_time=current_time,
                        end_time=current_time + duration_s
                    )
                    words.append(word)
                    print(f"    -> Added word: '{word.word}' ({word.start_time:.2f}-{word.end_time:.2f})")
                    current_time += duration_s
                except ValidationError as e:
                    print(f"    -> Validation error: {e}")
                    continue
    
    return words

def clean_ass_text(text: str) -> str:
    """Remove ASS formatting tags from text."""
    # Remove karaoke tags
    text = re.sub(r'\{\\k\d+\}', '', text)
    
    # Remove other ASS tags
    text = re.sub(r'\{[^}]*\}', '', text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def test_karaoke_parsing():
    """Test karaoke parsing with real ASS data."""
    print("Testing karaoke parsing...")
    print("=" * 50)
    
    # Real ASS line from the file
    ass_text = r"{\k107}Under {\k58}the {\k39}glow {\k64}of {\k16}the {\k55}silver {\k58}moon, {\k16}I {\k35}find {\k41}my {\k74}heart {\k35}in {\k10}a {\k41}tender {\k58}tune."
    
    print(f"Original ASS text: {ass_text}")
    
    # Parse karaoke timing
    words = parse_karaoke_timing(ass_text)
    
    # Clean text
    clean_text = clean_ass_text(ass_text)
    print(f"Clean text: '{clean_text}'")
    
    # Check word reconstruction
    if words:
        word_text = ' '.join(word.word for word in words)
        print(f"Word reconstruction: '{word_text}'")
        
        # Normalize for comparison
        normalized_clean = re.sub(r'\s+', ' ', clean_text.strip())
        normalized_words = re.sub(r'\s+', ' ', word_text.strip())
        
        print(f"Normalized clean: '{normalized_clean}'")
        print(f"Normalized words: '{normalized_words}'")
        print(f"Match: {normalized_clean == normalized_words}")
        
        if normalized_clean != normalized_words:
            print("MISMATCH DETECTED!")
            print(f"Clean length: {len(normalized_clean)}")
            print(f"Words length: {len(normalized_words)}")
            
            # Character by character comparison
            for i, (c1, c2) in enumerate(zip(normalized_clean, normalized_words)):
                if c1 != c2:
                    print(f"  Difference at position {i}: '{c1}' vs '{c2}'")
                    break
    
    return words, clean_text

if __name__ == "__main__":
    test_karaoke_parsing()
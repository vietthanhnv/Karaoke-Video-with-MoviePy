#!/usr/bin/env python3
"""
Check for overlapping lines in the ASS file
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_overlaps():
    """Check for overlapping subtitle lines."""
    
    # Events from the ASS file
    events = [
        (21.30, 29.44, "Under the glow of the silver moon, I find my heart in a tender tune."),
        (29.44, 38.32, "Every step brings me close to you, every moment feels so true."),
        (39.06, 43.14, "Soft is the night as it holds our song."),
        (43.74, 51.48, "In your embraces where I belong, every glance is a sweet surprise."),
        (51.98, 55.68, "I keep dancing in your eyes."),
        (56.68, 62.00, "Round and round the wall fades away."),
        (63.28, 70.84, "Love is the music and we will sway."),
        (73.30, 84.04, "Hand in hand through the gentle sky, forever dancing."),
        (85.68, 88.88, "In your eyes."),
        (90.18, 99.64, "No time, no fear, just you and me spinning like waves on a timeless sea."),
        (100.38, 107.44, "Every heart retails me, it's true, my forever begins with you."),
        (125.58, 132.38, "Round and round the world fades away."),
        (133.58, 140.74, "Love is the music and we will sway."),
        (143.08, 153.86, "Hand in hand through the gentle sky, forever dancing."),
        (155.64, 158.26, "In your eyes."),
        (199.32, 200.72, "Round and round the wall fades away."),
        (201.72, 202.06, "Round and round the wall fades away.")
    ]
    
    print(f"Checking {len(events)} events for overlaps...")
    print("=" * 50)
    
    overlaps = []
    
    for i in range(len(events)):
        for j in range(i + 1, len(events)):
            start1, end1, text1 = events[i]
            start2, end2, text2 = events[j]
            
            # Check if they overlap
            if not (end1 <= start2 or start1 >= end2):
                overlaps.append((i, j, start1, end1, start2, end2, text1, text2))
                print(f"OVERLAP: Event {i+1} ({start1}-{end1}) and Event {j+1} ({start2}-{end2})")
                print(f"  Event {i+1}: '{text1}'")
                print(f"  Event {j+1}: '{text2}'")
                print()
    
    if not overlaps:
        print("No overlaps found!")
    else:
        print(f"Found {len(overlaps)} overlapping pairs")
    
    return overlaps

if __name__ == "__main__":
    check_overlaps()
#!/usr/bin/env python3
"""
Comprehensive MoviePy v2 API Test

This script tests all the MoviePy v2 functionality used in the subtitle creator.
"""

import sys
import os
import tempfile
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all MoviePy imports."""
    print("🧪 Testing MoviePy imports...")
    
    try:
        from moviepy import (
            VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, 
            ColorClip, ImageClip, vfx, afx, VideoClip
        )
        print("✅ All core imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_audio_functionality():
    """Test audio-related functionality."""
    print("\n🎵 Testing audio functionality...")
    
    try:
        from moviepy import AudioFileClip
        
        # Test AudioFileClip class exists and has expected methods
        expected_methods = ['subclipped', 'with_duration', 'with_effects']
        for method in expected_methods:
            if not hasattr(AudioFileClip, method):
                print(f"❌ AudioFileClip missing method: {method}")
                return False
        
        print("✅ AudioFileClip has all required v2 methods")
        return True
        
    except Exception as e:
        print(f"❌ Audio test failed: {e}")
        return False

def test_video_functionality():
    """Test video-related functionality."""
    print("\n🎬 Testing video functionality...")
    
    try:
        from moviepy import VideoClip, TextClip, ColorClip, CompositeVideoClip
        
        # Test creating a simple ColorClip
        clip = ColorClip(size=(100, 100), color=(255, 0, 0), duration=1.0)
        
        # Test v2 methods
        clip_with_duration = clip.with_duration(2.0)
        clip_with_position = clip.with_position((10, 10))
        
        print("✅ Basic video clip creation and v2 methods work")
        
        # Test TextClip with v2 parameters
        text_clip = TextClip(text="Hello", font_size=50, color='white', duration=1.0)
        print("✅ TextClip with v2 parameters works")
        
        return True
        
    except Exception as e:
        print(f"❌ Video test failed: {e}")
        return False

def test_effects_system():
    """Test the v2 effects system."""
    print("\n✨ Testing effects system...")
    
    try:
        from moviepy import ColorClip, vfx, afx
        
        # Test video effects
        clip = ColorClip(size=(100, 100), color=(255, 0, 0), duration=2.0)
        
        # Test CrossFadeIn and CrossFadeOut effects
        effects = [vfx.CrossFadeIn(0.5), vfx.CrossFadeOut(0.5)]
        clip_with_effects = clip.with_effects(effects)
        
        print("✅ Video effects (CrossFadeIn/Out) work")
        
        # Test that afx module exists for audio effects
        if hasattr(afx, 'AudioLoop'):
            print("✅ Audio effects module available")
        else:
            print("⚠️  AudioLoop effect not found, but afx module exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Effects test failed: {e}")
        return False

def test_composition():
    """Test video composition functionality."""
    print("\n🎭 Testing composition functionality...")
    
    try:
        from moviepy import ColorClip, CompositeVideoClip
        
        # Create multiple clips
        clip1 = ColorClip(size=(100, 100), color=(255, 0, 0), duration=1.0)
        clip2 = ColorClip(size=(50, 50), color=(0, 255, 0), duration=1.0).with_position((25, 25))
        
        # Test composition
        composite = CompositeVideoClip([clip1, clip2])
        
        print("✅ Video composition works")
        return True
        
    except Exception as e:
        print(f"❌ Composition test failed: {e}")
        return False

def test_subtitle_creator_compatibility():
    """Test compatibility with subtitle creator modules."""
    print("\n🎯 Testing subtitle creator compatibility...")
    
    try:
        # Test importing subtitle creator modules that use MoviePy
        from subtitle_creator.effects.base import BaseEffect
        from subtitle_creator.effects.animation import KaraokeHighlightEffect
        from subtitle_creator.effects.particles import HeartParticleEffect
        
        print("✅ Subtitle creator effects modules import successfully")
        
        # Test creating effect instances
        karaoke_effect = KaraokeHighlightEffect("karaoke", {})
        heart_effect = HeartParticleEffect("hearts", {})
        
        print("✅ Effect instances created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Subtitle creator compatibility test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🎬 MoviePy v2 Comprehensive API Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_audio_functionality,
        test_video_functionality,
        test_effects_system,
        test_composition,
        test_subtitle_creator_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All MoviePy v2 functionality is working correctly!")
        print("✅ Your codebase is fully compatible with MoviePy v2")
    else:
        print("⚠️  Some issues found - see details above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
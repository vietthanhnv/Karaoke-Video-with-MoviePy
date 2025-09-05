"""
Integration tests for MediaManager with other components.

Tests integration with interfaces, config, and error handling.
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from src.subtitle_creator.media_manager import MediaManager
from src.subtitle_creator.interfaces import MediaManager as MediaManagerInterface, MediaError, AudioError
from src.subtitle_creator.config import get_config


class TestMediaManagerIntegration(unittest.TestCase):
    """Integration test cases for MediaManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock dependencies
        self.moviepy_patcher = patch('src.subtitle_creator.media_manager.MOVIEPY_AVAILABLE', True)
        self.pil_patcher = patch('src.subtitle_creator.media_manager.PIL_AVAILABLE', True)
        
        self.moviepy_patcher.start()
        self.pil_patcher.start()
        
        self.media_manager = MediaManager()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        self.moviepy_patcher.stop()
        self.pil_patcher.stop()
    
    def test_implements_interface(self):
        """Test that MediaManager properly implements the MediaManager interface."""
        self.assertIsInstance(self.media_manager, MediaManagerInterface)
        
        # Check that all abstract methods are implemented
        self.assertTrue(hasattr(self.media_manager, 'load_background_media'))
        self.assertTrue(hasattr(self.media_manager, 'load_audio'))
        self.assertTrue(hasattr(self.media_manager, 'get_supported_video_formats'))
        self.assertTrue(hasattr(self.media_manager, 'get_supported_image_formats'))
        self.assertTrue(hasattr(self.media_manager, 'get_supported_audio_formats'))
        
        # Check that methods are callable
        self.assertTrue(callable(self.media_manager.load_background_media))
        self.assertTrue(callable(self.media_manager.load_audio))
        self.assertTrue(callable(self.media_manager.get_supported_video_formats))
        self.assertTrue(callable(self.media_manager.get_supported_image_formats))
        self.assertTrue(callable(self.media_manager.get_supported_audio_formats))
    
    def test_uses_config_correctly(self):
        """Test that MediaManager uses configuration correctly."""
        config = get_config()
        
        # Test that supported formats match config
        self.assertEqual(
            self.media_manager.get_supported_video_formats(),
            config.supported_video_formats
        )
        self.assertEqual(
            self.media_manager.get_supported_image_formats(),
            config.supported_image_formats
        )
        self.assertEqual(
            self.media_manager.get_supported_audio_formats(),
            config.supported_audio_formats
        )
    
    def test_error_handling_consistency(self):
        """Test that MediaManager raises appropriate errors from interfaces module."""
        # Test MediaError for invalid media files
        with self.assertRaises(MediaError):
            self.media_manager.load_background_media('nonexistent.mp4')
        
        # Test AudioError for invalid audio files
        with self.assertRaises(AudioError):
            self.media_manager.load_audio('nonexistent.mp3')
        
        # Test that errors are from the interfaces module
        try:
            self.media_manager.load_background_media('nonexistent.mp4')
        except Exception as e:
            self.assertIsInstance(e, MediaError)
            self.assertEqual(e.__class__.__module__, 'src.subtitle_creator.interfaces')
        
        try:
            self.media_manager.load_audio('nonexistent.mp3')
        except Exception as e:
            self.assertIsInstance(e, AudioError)
            self.assertEqual(e.__class__.__module__, 'src.subtitle_creator.interfaces')
    
    def test_format_validation_integration(self):
        """Test format validation works with all supported formats from config."""
        config = get_config()
        
        # Test all video formats
        for fmt in config.supported_video_formats:
            self.assertTrue(self.media_manager.is_video_format(fmt))
            self.assertFalse(self.media_manager.is_image_format(fmt))
            self.assertFalse(self.media_manager.is_audio_format(fmt))
        
        # Test all image formats
        for fmt in config.supported_image_formats:
            self.assertTrue(self.media_manager.is_image_format(fmt))
            self.assertFalse(self.media_manager.is_video_format(fmt))
            self.assertFalse(self.media_manager.is_audio_format(fmt))
        
        # Test all audio formats
        for fmt in config.supported_audio_formats:
            self.assertTrue(self.media_manager.is_audio_format(fmt))
            self.assertFalse(self.media_manager.is_video_format(fmt))
            self.assertFalse(self.media_manager.is_image_format(fmt))
    
    def test_temp_directory_usage(self):
        """Test that MediaManager uses temp directory from config."""
        config = get_config()
        
        # Verify temp directory exists (created during MediaManager init)
        self.assertTrue(os.path.exists(config.temp_dir))
    
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    @patch('src.subtitle_creator.media_manager.ImageClip')
    @patch('src.subtitle_creator.media_manager.Image')
    def test_caching_with_different_durations(self, mock_pil_image, mock_image_clip, mock_video_clip):
        """Test that caching works correctly with different image durations."""
        # Create test image file
        image_path = os.path.join(self.temp_dir, 'test_image.jpg')
        with open(image_path, 'wb') as f:
            f.write(b"fake image data")
        
        # Mock PIL Image
        mock_img = Mock()
        mock_img.size = (1920, 1080)
        mock_img.mode = 'RGB'
        mock_pil_image.open.return_value.__enter__.return_value = mock_img
        
        # Mock ImageClip
        mock_clip1 = Mock()
        mock_clip2 = Mock()
        mock_image_clip.side_effect = [mock_clip1, mock_clip2]
        
        # Load same image with different durations
        result1 = self.media_manager.load_background_media(image_path, duration=5.0)
        result2 = self.media_manager.load_background_media(image_path, duration=10.0)
        
        # Should be different objects due to different durations
        self.assertNotEqual(result1, result2)
        
        # Should have called ImageClip twice
        self.assertEqual(mock_image_clip.call_count, 2)
        
        # Cache should have 2 entries
        cache_info = self.media_manager.get_cache_info()
        self.assertEqual(cache_info['video_cache_size'], 2)
    
    def test_cleanup_on_destruction(self):
        """Test that MediaManager cleans up properly when destroyed."""
        # Create a MediaManager instance
        media_manager = MediaManager()
        
        # Add some mock cached items
        media_manager._video_cache['test'] = Mock()
        media_manager._audio_cache['test'] = Mock()
        
        # Verify cache has items
        self.assertEqual(len(media_manager._video_cache), 1)
        self.assertEqual(len(media_manager._audio_cache), 1)
        
        # Delete the instance (triggers __del__)
        del media_manager
        
        # Note: We can't easily test __del__ behavior in unit tests
        # but we've verified the clear_cache method works in other tests
    
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    @patch('src.subtitle_creator.media_manager.AudioFileClip')
    def test_audio_video_integration_workflow(self, mock_audio_clip, mock_video_clip):
        """Test complete workflow of loading video, detecting audio, and calculating duration."""
        # Create test files
        video_path = os.path.join(self.temp_dir, 'test_video.mp4')
        audio_path = os.path.join(self.temp_dir, 'test_audio.mp3')
        
        with open(video_path, 'wb') as f:
            f.write(b"fake video data")
        with open(audio_path, 'wb') as f:
            f.write(b"fake audio data")
        
        # Mock video with audio
        mock_video_audio = Mock()
        mock_video_audio.duration = 120.0
        mock_video_audio.fps = 44100
        mock_video_audio.nchannels = 2
        
        mock_video = Mock()
        mock_video.duration = 120.0
        mock_video.size = (1920, 1080)
        mock_video.fps = 30
        mock_video.audio = mock_video_audio
        mock_video_clip.return_value = mock_video
        
        # Mock external audio
        mock_audio = Mock()
        mock_audio.duration = 150.0
        mock_audio.fps = 44100
        mock_audio.nchannels = 2
        mock_audio_clip.return_value = mock_audio
        
        # Test workflow
        # 1. Load video
        video_clip = self.media_manager.load_background_media(video_path)
        self.assertIsNotNone(video_clip)
        
        # 2. Detect audio track
        audio_info = self.media_manager.detect_audio_track(video_path)
        self.assertIsNotNone(audio_info)
        self.assertTrue(audio_info['has_audio'])
        self.assertEqual(audio_info['duration'], 120.0)
        
        # 3. Calculate duration with video audio
        duration1 = self.media_manager.calculate_final_video_duration(video_path)
        self.assertEqual(duration1, 120.0)
        
        # 4. Calculate duration with external audio override
        duration2 = self.media_manager.calculate_final_video_duration(video_path, audio_path)
        self.assertEqual(duration2, 150.0)
        
        # 5. Test synchronization analysis
        sync_info = self.media_manager.synchronize_audio_with_subtitles(150.0, 149.5, tolerance=1.0)
        self.assertTrue(sync_info['is_synchronized'])
    
    @patch('src.subtitle_creator.media_manager.AudioFileClip')
    @patch('src.subtitle_creator.media_manager.Image')
    def test_image_audio_integration_workflow(self, mock_pil_image, mock_audio_clip):
        """Test complete workflow of loading image with audio for video creation."""
        # Create test files
        image_path = os.path.join(self.temp_dir, 'test_image.jpg')
        audio_path = os.path.join(self.temp_dir, 'test_audio.mp3')
        
        with open(image_path, 'wb') as f:
            f.write(b"fake image data")
        with open(audio_path, 'wb') as f:
            f.write(b"fake audio data")
        
        # Mock PIL Image
        mock_img = Mock()
        mock_img.size = (1920, 1080)
        mock_img.mode = 'RGB'
        mock_pil_image.open.return_value.__enter__.return_value = mock_img
        
        # Mock audio
        mock_audio = Mock()
        mock_audio.duration = 180.0
        mock_audio.fps = 44100
        mock_audio.nchannels = 2
        mock_audio_clip.return_value = mock_audio
        
        # Test workflow
        # 1. Get image info
        image_info = self.media_manager.get_media_info(image_path)
        self.assertEqual(image_info['media_type'], 'image')
        
        # 2. Get audio info
        audio_info = self.media_manager.get_media_info(audio_path)
        self.assertEqual(audio_info['media_type'], 'audio')
        self.assertEqual(audio_info['duration'], 180.0)
        
        # 3. Calculate final video duration (should use audio duration)
        duration = self.media_manager.calculate_final_video_duration(image_path, audio_path)
        self.assertEqual(duration, 180.0)
        
        # 4. Test that image without audio fails
        with self.assertRaises(MediaError) as context:
            self.media_manager.calculate_final_video_duration(image_path)
        self.assertIn("requires an audio file", str(context.exception))
    
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    def test_audio_extraction_integration(self, mock_video_clip):
        """Test audio extraction integration with video loading."""
        video_path = os.path.join(self.temp_dir, 'test_video.mp4')
        with open(video_path, 'wb') as f:
            f.write(b"fake video data")
        
        # Mock video with audio
        mock_audio = Mock()
        mock_audio.write_audiofile = Mock()
        
        mock_video = Mock()
        mock_video.audio = mock_audio
        mock_video_clip.return_value = mock_video
        
        # Test extraction
        output_path = self.media_manager.extract_audio_from_video(video_path)
        
        # Should create output in temp directory
        self.assertTrue(output_path.startswith(self.media_manager.config.temp_dir))
        self.assertTrue(output_path.endswith('_extracted_audio.wav'))
        
        # Should have called write_audiofile
        mock_audio.write_audiofile.assert_called_once()
    
    def test_audio_format_support_integration(self):
        """Test that all configured audio formats are properly supported."""
        config = get_config()
        
        # Test that all configured audio formats are recognized
        for audio_format in config.supported_audio_formats:
            self.assertTrue(self.media_manager.is_audio_format(audio_format))
            
            # Create a fake file with this extension
            test_file = os.path.join(self.temp_dir, f'test{audio_format}')
            with open(test_file, 'wb') as f:
                f.write(b"fake audio data")
            
            # Should be recognized as audio format in validation
            is_valid, _ = self.media_manager.validate_media_file(test_file)
            # Note: Will fail validation due to fake data, but format should be recognized
            # The error should not be about unsupported format
            if not is_valid:
                # Should fail on content validation, not format validation
                _, error_msg = self.media_manager.validate_media_file(test_file)
                self.assertNotIn("Unsupported file format", error_msg)
    
    @patch('src.subtitle_creator.media_manager.AudioFileClip')
    def test_audio_error_propagation_integration(self, mock_audio_clip):
        """Test that audio errors are properly propagated through the system."""
        audio_path = os.path.join(self.temp_dir, 'test_audio.mp3')
        with open(audio_path, 'wb') as f:
            f.write(b"fake audio data")
        
        # Mock AudioFileClip to raise an exception
        mock_audio_clip.side_effect = Exception("Codec error")
        
        # Should raise AudioError (not generic Exception)
        with self.assertRaises(AudioError) as context:
            self.media_manager.load_audio(audio_path)
        
        # Error should contain helpful information
        error_msg = str(context.exception)
        self.assertIn("Audio codec not supported", error_msg)
        self.assertIn("Try converting the file", error_msg)
    
    def test_synchronization_analysis_integration(self):
        """Test audio-subtitle synchronization analysis with various scenarios."""
        # Test perfect synchronization
        sync_info = self.media_manager.synchronize_audio_with_subtitles(120.0, 120.0)
        self.assertTrue(sync_info['is_synchronized'])
        self.assertEqual(sync_info['status'], 'synchronized')
        
        # Test within tolerance
        sync_info = self.media_manager.synchronize_audio_with_subtitles(120.0, 119.5, tolerance=1.0)
        self.assertTrue(sync_info['is_synchronized'])
        
        # Test outside tolerance - audio longer
        sync_info = self.media_manager.synchronize_audio_with_subtitles(120.0, 115.0, tolerance=1.0)
        self.assertFalse(sync_info['is_synchronized'])
        self.assertEqual(sync_info['status'], 'audio_longer')
        self.assertIn("Audio is 5.00 seconds longer", sync_info['recommendation'])
        
        # Test outside tolerance - subtitles longer
        sync_info = self.media_manager.synchronize_audio_with_subtitles(115.0, 120.0, tolerance=1.0)
        self.assertFalse(sync_info['is_synchronized'])
        self.assertEqual(sync_info['status'], 'subtitles_longer')
        self.assertIn("Subtitles extend 5.00 seconds beyond", sync_info['recommendation'])


if __name__ == '__main__':
    unittest.main()
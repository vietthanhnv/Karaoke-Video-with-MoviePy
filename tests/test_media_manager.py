"""
Unit tests for MediaManager class.

Tests media format detection, validation, loading, and conversion functionality.
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import the module under test
from src.subtitle_creator.media_manager import MediaManager
from src.subtitle_creator.interfaces import MediaError, AudioError


class TestMediaManager(unittest.TestCase):
    """Test cases for MediaManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock MoviePy and PIL dependencies
        self.moviepy_patcher = patch('src.subtitle_creator.media_manager.MOVIEPY_AVAILABLE', True)
        self.pil_patcher = patch('src.subtitle_creator.media_manager.PIL_AVAILABLE', True)
        
        self.moviepy_patcher.start()
        self.pil_patcher.start()
        
        # Create MediaManager instance
        self.media_manager = MediaManager()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # Stop patches
        self.moviepy_patcher.stop()
        self.pil_patcher.stop()
    
    def create_temp_file(self, filename: str, content: bytes = b"test content") -> str:
        """Create a temporary file for testing."""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(content)
        return file_path
    
    def test_initialization(self):
        """Test MediaManager initialization."""
        self.assertIsInstance(self.media_manager, MediaManager)
        self.assertEqual(self.media_manager.default_image_duration, 10.0)
        self.assertEqual(self.media_manager.default_fps, 24)
        self.assertIsInstance(self.media_manager._video_cache, dict)
        self.assertIsInstance(self.media_manager._audio_cache, dict)
    
    def test_dependency_validation_missing_moviepy(self):
        """Test initialization fails when MoviePy is not available."""
        with patch('src.subtitle_creator.media_manager.MOVIEPY_AVAILABLE', False):
            with self.assertRaises(MediaError) as context:
                MediaManager()
            self.assertIn("MoviePy is not available", str(context.exception))
    
    def test_dependency_validation_missing_pil(self):
        """Test initialization fails when PIL is not available."""
        with patch('src.subtitle_creator.media_manager.PIL_AVAILABLE', False):
            with self.assertRaises(MediaError) as context:
                MediaManager()
            self.assertIn("PIL/Pillow is not available", str(context.exception))
    
    def test_supported_formats(self):
        """Test supported format detection methods."""
        # Test video formats
        self.assertTrue(self.media_manager.is_video_format('.mp4'))
        self.assertTrue(self.media_manager.is_video_format('.MP4'))
        self.assertTrue(self.media_manager.is_video_format('.avi'))
        self.assertTrue(self.media_manager.is_video_format('.mov'))
        self.assertTrue(self.media_manager.is_video_format('.mkv'))
        self.assertFalse(self.media_manager.is_video_format('.jpg'))
        
        # Test image formats
        self.assertTrue(self.media_manager.is_image_format('.jpg'))
        self.assertTrue(self.media_manager.is_image_format('.JPG'))
        self.assertTrue(self.media_manager.is_image_format('.jpeg'))
        self.assertTrue(self.media_manager.is_image_format('.png'))
        self.assertTrue(self.media_manager.is_image_format('.gif'))
        self.assertFalse(self.media_manager.is_image_format('.mp4'))
        
        # Test audio formats
        self.assertTrue(self.media_manager.is_audio_format('.mp3'))
        self.assertTrue(self.media_manager.is_audio_format('.MP3'))
        self.assertTrue(self.media_manager.is_audio_format('.wav'))
        self.assertTrue(self.media_manager.is_audio_format('.aac'))
        self.assertTrue(self.media_manager.is_audio_format('.ogg'))
        self.assertFalse(self.media_manager.is_audio_format('.jpg'))
    
    def test_get_supported_formats(self):
        """Test getting lists of supported formats."""
        video_formats = self.media_manager.get_supported_video_formats()
        self.assertIn('.mp4', video_formats)
        self.assertIn('.avi', video_formats)
        self.assertIn('.mov', video_formats)
        self.assertIn('.mkv', video_formats)
        
        image_formats = self.media_manager.get_supported_image_formats()
        self.assertIn('.jpg', image_formats)
        self.assertIn('.jpeg', image_formats)
        self.assertIn('.png', image_formats)
        self.assertIn('.gif', image_formats)
        
        audio_formats = self.media_manager.get_supported_audio_formats()
        self.assertIn('.mp3', audio_formats)
        self.assertIn('.wav', audio_formats)
        self.assertIn('.aac', audio_formats)
        self.assertIn('.ogg', audio_formats)
        
        all_formats = self.media_manager.get_all_supported_formats()
        self.assertIn('video', all_formats)
        self.assertIn('image', all_formats)
        self.assertIn('audio', all_formats)
    
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    def test_load_video_file_success(self, mock_video_clip):
        """Test successful video file loading."""
        # Create test video file
        video_path = self.create_temp_file('test_video.mp4')
        
        # Mock VideoFileClip
        mock_clip = Mock()
        mock_clip.duration = 30.0
        mock_clip.size = (1920, 1080)
        mock_video_clip.return_value = mock_clip
        
        # Test loading
        result = self.media_manager.load_background_media(video_path)
        
        self.assertEqual(result, mock_clip)
        mock_video_clip.assert_called_once_with(video_path)
    
    def test_load_video_file_not_found(self):
        """Test loading non-existent video file."""
        with self.assertRaises(MediaError) as context:
            self.media_manager.load_background_media('nonexistent.mp4')
        self.assertIn("Media file not found", str(context.exception))
    
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    def test_load_video_file_invalid_duration(self, mock_video_clip):
        """Test loading video file with invalid duration."""
        video_path = self.create_temp_file('test_video.mp4')
        
        # Mock VideoFileClip with invalid duration
        mock_clip = Mock()
        mock_clip.duration = None
        mock_clip.size = (1920, 1080)
        mock_video_clip.return_value = mock_clip
        
        with self.assertRaises(MediaError) as context:
            self.media_manager.load_background_media(video_path)
        self.assertIn("Invalid video duration", str(context.exception))
    
    @patch('src.subtitle_creator.media_manager.ImageClip')
    @patch('src.subtitle_creator.media_manager.Image')
    def test_load_image_file_success(self, mock_pil_image, mock_image_clip):
        """Test successful image file loading."""
        # Create test image file
        image_path = self.create_temp_file('test_image.jpg')
        
        # Mock PIL Image
        mock_img = Mock()
        mock_img.size = (1920, 1080)
        mock_img.mode = 'RGB'
        mock_pil_image.open.return_value.__enter__.return_value = mock_img
        
        # Mock ImageClip
        mock_clip = Mock()
        mock_image_clip.return_value = mock_clip
        
        # Test loading with default duration
        result = self.media_manager.load_background_media(image_path)
        
        self.assertEqual(result, mock_clip)
        mock_image_clip.assert_called_once_with(image_path, duration=10.0)
    
    @patch('src.subtitle_creator.media_manager.ImageClip')
    @patch('src.subtitle_creator.media_manager.Image')
    def test_load_image_file_custom_duration(self, mock_pil_image, mock_image_clip):
        """Test image file loading with custom duration."""
        image_path = self.create_temp_file('test_image.png')
        
        # Mock PIL Image
        mock_img = Mock()
        mock_img.size = (1920, 1080)
        mock_img.mode = 'RGB'
        mock_pil_image.open.return_value.__enter__.return_value = mock_img
        
        # Mock ImageClip
        mock_clip = Mock()
        mock_image_clip.return_value = mock_clip
        
        # Test loading with custom duration
        result = self.media_manager.load_background_media(image_path, duration=5.0)
        
        self.assertEqual(result, mock_clip)
        mock_image_clip.assert_called_once_with(image_path, duration=5.0)
    
    @patch('src.subtitle_creator.media_manager.Image')
    def test_load_image_file_invalid_dimensions(self, mock_pil_image):
        """Test loading image file with invalid dimensions."""
        image_path = self.create_temp_file('test_image.jpg')
        
        # Mock PIL Image with invalid dimensions
        mock_img = Mock()
        mock_img.size = (0, 0)
        mock_pil_image.open.return_value.__enter__.return_value = mock_img
        
        with self.assertRaises(MediaError) as context:
            self.media_manager.load_background_media(image_path)
        self.assertIn("Invalid image dimensions", str(context.exception))
    
    @patch('src.subtitle_creator.media_manager.AudioFileClip')
    def test_load_audio_success(self, mock_audio_clip):
        """Test successful audio file loading."""
        audio_path = self.create_temp_file('test_audio.mp3')
        
        # Mock AudioFileClip
        mock_clip = Mock()
        mock_clip.duration = 180.0
        mock_audio_clip.return_value = mock_clip
        
        result = self.media_manager.load_audio(audio_path)
        
        self.assertEqual(result, mock_clip)
        mock_audio_clip.assert_called_once_with(audio_path)
    
    def test_load_audio_not_found(self):
        """Test loading non-existent audio file."""
        with self.assertRaises(AudioError) as context:
            self.media_manager.load_audio('nonexistent.mp3')
        self.assertIn("Audio file not found", str(context.exception))
    
    @patch('src.subtitle_creator.media_manager.AudioFileClip')
    def test_load_audio_invalid_format(self, mock_audio_clip):
        """Test loading audio file with unsupported format."""
        audio_path = self.create_temp_file('test_audio.xyz')
        
        with self.assertRaises(AudioError) as context:
            self.media_manager.load_audio(audio_path)
        self.assertIn("Unsupported audio format", str(context.exception))
    
    @patch('src.subtitle_creator.media_manager.AudioFileClip')
    def test_load_audio_invalid_duration(self, mock_audio_clip):
        """Test loading audio file with invalid duration."""
        audio_path = self.create_temp_file('test_audio.mp3')
        
        # Mock AudioFileClip with invalid duration
        mock_clip = Mock()
        mock_clip.duration = None
        mock_audio_clip.return_value = mock_clip
        
        with self.assertRaises(AudioError) as context:
            self.media_manager.load_audio(audio_path)
        self.assertIn("Invalid or corrupted audio file", str(context.exception))
    
    def test_validate_media_file_not_found(self):
        """Test validation of non-existent file."""
        is_valid, error_msg = self.media_manager.validate_media_file('nonexistent.mp4')
        self.assertFalse(is_valid)
        self.assertIn("File not found", error_msg)
    
    def test_validate_media_file_unsupported_format(self):
        """Test validation of unsupported file format."""
        unsupported_path = self.create_temp_file('test.xyz')
        is_valid, error_msg = self.media_manager.validate_media_file(unsupported_path)
        self.assertFalse(is_valid)
        self.assertIn("Unsupported file format", error_msg)
    
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    def test_validate_media_file_valid_video(self, mock_video_clip):
        """Test validation of valid video file."""
        video_path = self.create_temp_file('test_video.mp4')
        
        # Mock VideoFileClip for get_media_info
        mock_clip = Mock()
        mock_clip.duration = 30.0
        mock_clip.size = (1920, 1080)
        mock_clip.fps = 30
        mock_clip.audio = None
        mock_video_clip.return_value.__enter__.return_value = mock_clip
        
        is_valid, error_msg = self.media_manager.validate_media_file(video_path)
        self.assertTrue(is_valid)
        self.assertEqual(error_msg, "File is valid")
    
    @patch('src.subtitle_creator.media_manager.ImageClip')
    @patch('src.subtitle_creator.media_manager.Image')
    def test_convert_image_to_video_success(self, mock_pil_image, mock_image_clip):
        """Test successful image to video conversion."""
        image_path = self.create_temp_file('test_image.jpg')
        output_path = os.path.join(self.temp_dir, 'output_video.mp4')
        
        # Mock PIL Image
        mock_img = Mock()
        mock_img.size = (1920, 1080)
        mock_img.mode = 'RGB'
        mock_pil_image.open.return_value.__enter__.return_value = mock_img
        
        # Mock ImageClip
        mock_clip = Mock()
        mock_clip.write_videofile = Mock()
        mock_image_clip.return_value = mock_clip
        
        result = self.media_manager.convert_image_to_video(
            image_path, duration=5.0, output_path=output_path
        )
        
        self.assertEqual(result, output_path)
        mock_clip.write_videofile.assert_called_once()
    
    def test_convert_image_to_video_invalid_duration(self):
        """Test image to video conversion with invalid duration."""
        image_path = self.create_temp_file('test_image.jpg')
        
        with self.assertRaises(MediaError) as context:
            self.media_manager.convert_image_to_video(image_path, duration=-1.0)
        self.assertIn("Duration must be positive", str(context.exception))
    
    def test_convert_image_to_video_not_found(self):
        """Test image to video conversion with non-existent file."""
        with self.assertRaises(MediaError) as context:
            self.media_manager.convert_image_to_video('nonexistent.jpg', duration=5.0)
        self.assertIn("Image file not found", str(context.exception))
    
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    def test_get_video_info(self, mock_video_clip):
        """Test getting video file information."""
        video_path = self.create_temp_file('test_video.mp4')
        
        # Mock VideoFileClip
        mock_clip = Mock()
        mock_clip.duration = 30.0
        mock_clip.size = (1920, 1080)
        mock_clip.fps = 30
        mock_clip.audio = Mock()  # Has audio
        mock_video_clip.return_value = mock_clip
        
        info = self.media_manager.get_media_info(video_path)
        
        self.assertEqual(info['media_type'], 'video')
        self.assertEqual(info['duration'], 30.0)
        self.assertEqual(info['fps'], 30)
        self.assertEqual(info['width'], 1920)
        self.assertEqual(info['height'], 1080)
        self.assertTrue(info['has_audio'])
    
    @patch('src.subtitle_creator.media_manager.Image')
    def test_get_image_info(self, mock_pil_image):
        """Test getting image file information."""
        image_path = self.create_temp_file('test_image.jpg')
        
        # Mock PIL Image
        mock_img = Mock()
        mock_img.size = (1920, 1080)
        mock_img.mode = 'RGB'
        mock_img.format = 'JPEG'
        mock_pil_image.open.return_value.__enter__.return_value = mock_img
        
        info = self.media_manager.get_media_info(image_path)
        
        self.assertEqual(info['media_type'], 'image')
        self.assertEqual(info['width'], 1920)
        self.assertEqual(info['height'], 1080)
        self.assertEqual(info['mode'], 'RGB')
        self.assertEqual(info['format'], 'JPEG')
    
    @patch('src.subtitle_creator.media_manager.AudioFileClip')
    def test_get_audio_info(self, mock_audio_clip):
        """Test getting audio file information."""
        audio_path = self.create_temp_file('test_audio.mp3')
        
        # Mock AudioFileClip
        mock_clip = Mock()
        mock_clip.duration = 180.0
        mock_clip.fps = 44100
        mock_audio_clip.return_value = mock_clip
        
        info = self.media_manager.get_media_info(audio_path)
        
        self.assertEqual(info['media_type'], 'audio')
        self.assertEqual(info['duration'], 180.0)
    
    def test_caching_functionality(self):
        """Test media caching functionality."""
        # Test cache info when empty
        cache_info = self.media_manager.get_cache_info()
        self.assertEqual(cache_info['video_cache_size'], 0)
        self.assertEqual(cache_info['audio_cache_size'], 0)
        
        # Test cache clearing
        self.media_manager.clear_cache()
        
        # Verify cache is still empty after clearing empty cache
        cache_info = self.media_manager.get_cache_info()
        self.assertEqual(cache_info['video_cache_size'], 0)
        self.assertEqual(cache_info['audio_cache_size'], 0)
    
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    def test_video_caching(self, mock_video_clip):
        """Test video file caching."""
        video_path = self.create_temp_file('test_video.mp4')
        
        # Mock VideoFileClip
        mock_clip = Mock()
        mock_clip.duration = 30.0
        mock_clip.size = (1920, 1080)
        mock_video_clip.return_value = mock_clip
        
        # Load video twice
        result1 = self.media_manager.load_background_media(video_path)
        result2 = self.media_manager.load_background_media(video_path)
        
        # Should be the same cached object
        self.assertEqual(result1, result2)
        
        # VideoFileClip should only be called once due to caching
        mock_video_clip.assert_called_once_with(video_path)
        
        # Check cache info
        cache_info = self.media_manager.get_cache_info()
        self.assertEqual(cache_info['video_cache_size'], 1)
    
    @patch('src.subtitle_creator.media_manager.AudioFileClip')
    def test_audio_caching(self, mock_audio_clip):
        """Test audio file caching."""
        audio_path = self.create_temp_file('test_audio.mp3')
        
        # Mock AudioFileClip
        mock_clip = Mock()
        mock_clip.duration = 180.0
        mock_audio_clip.return_value = mock_clip
        
        # Load audio twice
        result1 = self.media_manager.load_audio(audio_path)
        result2 = self.media_manager.load_audio(audio_path)
        
        # Should be the same cached object
        self.assertEqual(result1, result2)
        
        # AudioFileClip should only be called once due to caching
        mock_audio_clip.assert_called_once_with(audio_path)
        
        # Check cache info
        cache_info = self.media_manager.get_cache_info()
        self.assertEqual(cache_info['audio_cache_size'], 1)
    
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    def test_detect_audio_track_with_audio(self, mock_video_clip):
        """Test detecting audio track in video file that has audio."""
        video_path = self.create_temp_file('test_video.mp4')
        
        # Mock VideoFileClip with audio
        mock_audio = Mock()
        mock_audio.duration = 120.0
        mock_audio.fps = 44100
        mock_audio.nchannels = 2
        
        mock_clip = Mock()
        mock_clip.audio = mock_audio
        mock_video_clip.return_value = mock_clip
        
        result = self.media_manager.detect_audio_track(video_path)
        
        self.assertIsNotNone(result)
        self.assertTrue(result['has_audio'])
        self.assertEqual(result['duration'], 120.0)
        self.assertEqual(result['sample_rate'], 44100)
        self.assertEqual(result['channels'], 2)
    
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    def test_detect_audio_track_without_audio(self, mock_video_clip):
        """Test detecting audio track in video file that has no audio."""
        video_path = self.create_temp_file('test_video.mp4')
        
        # Mock VideoFileClip without audio
        mock_clip = Mock()
        mock_clip.audio = None
        mock_video_clip.return_value = mock_clip
        
        result = self.media_manager.detect_audio_track(video_path)
        
        self.assertIsNone(result)
    
    def test_detect_audio_track_not_found(self):
        """Test detecting audio track in non-existent video file."""
        with self.assertRaises(MediaError) as context:
            self.media_manager.detect_audio_track('nonexistent.mp4')
        self.assertIn("Video file not found", str(context.exception))
    
    def test_detect_audio_track_invalid_format(self):
        """Test detecting audio track in non-video file."""
        image_path = self.create_temp_file('test_image.jpg')
        
        with self.assertRaises(MediaError) as context:
            self.media_manager.detect_audio_track(image_path)
        self.assertIn("not a supported video format", str(context.exception))
    
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    def test_calculate_final_video_duration_video_with_audio(self, mock_video_clip):
        """Test calculating duration for video with audio track."""
        video_path = self.create_temp_file('test_video.mp4')
        
        # Mock VideoFileClip with audio
        mock_clip = Mock()
        mock_clip.duration = 30.0
        mock_clip.size = (1920, 1080)
        mock_clip.fps = 30
        mock_clip.audio = Mock()  # Has audio
        mock_video_clip.return_value = mock_clip
        
        duration = self.media_manager.calculate_final_video_duration(video_path)
        
        self.assertEqual(duration, 30.0)
    
    @patch('src.subtitle_creator.media_manager.AudioFileClip')
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    def test_calculate_final_video_duration_video_with_external_audio(self, mock_video_clip, mock_audio_clip):
        """Test calculating duration for video with external audio override."""
        video_path = self.create_temp_file('test_video.mp4')
        audio_path = self.create_temp_file('test_audio.mp3')
        
        # Mock VideoFileClip with audio
        mock_video = Mock()
        mock_video.duration = 30.0
        mock_video.size = (1920, 1080)
        mock_video.fps = 30
        mock_video.audio = Mock()  # Has audio
        mock_video_clip.return_value = mock_video
        
        # Mock AudioFileClip
        mock_audio = Mock()
        mock_audio.duration = 45.0
        mock_audio_clip.return_value = mock_audio
        
        duration = self.media_manager.calculate_final_video_duration(video_path, audio_path)
        
        self.assertEqual(duration, 45.0)  # Should use external audio duration
    
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    def test_calculate_final_video_duration_video_no_audio_no_external(self, mock_video_clip):
        """Test calculating duration for video without audio and no external audio."""
        video_path = self.create_temp_file('test_video.mp4')
        
        # Mock VideoFileClip without audio
        mock_clip = Mock()
        mock_clip.duration = 30.0
        mock_clip.size = (1920, 1080)
        mock_clip.fps = 30
        mock_clip.audio = None  # No audio
        mock_video_clip.return_value = mock_clip
        
        with self.assertRaises(MediaError) as context:
            self.media_manager.calculate_final_video_duration(video_path)
        self.assertIn("has no audio track", str(context.exception))
    
    @patch('src.subtitle_creator.media_manager.AudioFileClip')
    @patch('src.subtitle_creator.media_manager.Image')
    def test_calculate_final_video_duration_image_with_audio(self, mock_pil_image, mock_audio_clip):
        """Test calculating duration for image with audio."""
        image_path = self.create_temp_file('test_image.jpg')
        audio_path = self.create_temp_file('test_audio.mp3')
        
        # Mock PIL Image
        mock_img = Mock()
        mock_img.size = (1920, 1080)
        mock_img.mode = 'RGB'
        mock_pil_image.open.return_value.__enter__.return_value = mock_img
        
        # Mock AudioFileClip
        mock_audio = Mock()
        mock_audio.duration = 60.0
        mock_audio_clip.return_value = mock_audio
        
        duration = self.media_manager.calculate_final_video_duration(image_path, audio_path)
        
        self.assertEqual(duration, 60.0)
    
    @patch('src.subtitle_creator.media_manager.Image')
    def test_calculate_final_video_duration_image_no_audio(self, mock_pil_image):
        """Test calculating duration for image without audio."""
        image_path = self.create_temp_file('test_image.jpg')
        
        # Mock PIL Image
        mock_img = Mock()
        mock_img.size = (1920, 1080)
        mock_img.mode = 'RGB'
        mock_pil_image.open.return_value.__enter__.return_value = mock_img
        
        with self.assertRaises(MediaError) as context:
            self.media_manager.calculate_final_video_duration(image_path)
        self.assertIn("requires an audio file", str(context.exception))
    
    def test_synchronize_audio_with_subtitles_synchronized(self):
        """Test audio-subtitle synchronization when they match."""
        result = self.media_manager.synchronize_audio_with_subtitles(120.0, 119.5, tolerance=1.0)
        
        self.assertTrue(result['is_synchronized'])
        self.assertEqual(result['status'], 'synchronized')
        self.assertEqual(result['audio_duration'], 120.0)
        self.assertEqual(result['subtitle_end_time'], 119.5)
        self.assertEqual(result['time_difference'], 0.5)
    
    def test_synchronize_audio_with_subtitles_audio_longer(self):
        """Test audio-subtitle synchronization when audio is longer."""
        result = self.media_manager.synchronize_audio_with_subtitles(120.0, 115.0, tolerance=1.0)
        
        self.assertFalse(result['is_synchronized'])
        self.assertEqual(result['status'], 'audio_longer')
        self.assertEqual(result['time_difference'], 5.0)
        self.assertIn("Audio is 5.00 seconds longer", result['recommendation'])
    
    def test_synchronize_audio_with_subtitles_subtitles_longer(self):
        """Test audio-subtitle synchronization when subtitles are longer."""
        result = self.media_manager.synchronize_audio_with_subtitles(115.0, 120.0, tolerance=1.0)
        
        self.assertFalse(result['is_synchronized'])
        self.assertEqual(result['status'], 'subtitles_longer')
        self.assertEqual(result['time_difference'], 5.0)
        self.assertIn("Subtitles extend 5.00 seconds beyond", result['recommendation'])
    
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    def test_extract_audio_from_video_success(self, mock_video_clip):
        """Test successful audio extraction from video."""
        video_path = self.create_temp_file('test_video.mp4')
        output_path = os.path.join(self.temp_dir, 'extracted_audio.wav')
        
        # Mock VideoFileClip with audio
        mock_audio = Mock()
        mock_audio.write_audiofile = Mock()
        
        mock_clip = Mock()
        mock_clip.audio = mock_audio
        mock_video_clip.return_value = mock_clip
        
        result = self.media_manager.extract_audio_from_video(video_path, output_path)
        
        self.assertEqual(result, output_path)
        mock_audio.write_audiofile.assert_called_once()
    
    @patch('src.subtitle_creator.media_manager.VideoFileClip')
    def test_extract_audio_from_video_no_audio(self, mock_video_clip):
        """Test audio extraction from video without audio track."""
        video_path = self.create_temp_file('test_video.mp4')
        
        # Mock VideoFileClip without audio
        mock_clip = Mock()
        mock_clip.audio = None
        mock_video_clip.return_value = mock_clip
        
        with self.assertRaises(MediaError) as context:
            self.media_manager.extract_audio_from_video(video_path)
        self.assertIn("has no audio track to extract", str(context.exception))
    
    def test_extract_audio_from_video_not_found(self):
        """Test audio extraction from non-existent video."""
        with self.assertRaises(MediaError) as context:
            self.media_manager.extract_audio_from_video('nonexistent.mp4')
        self.assertIn("Video file not found", str(context.exception))
    
    @patch('src.subtitle_creator.media_manager.AudioFileClip')
    def test_load_audio_enhanced_error_handling_empty_file(self, mock_audio_clip):
        """Test loading empty audio file."""
        audio_path = self.create_temp_file('empty_audio.mp3', b'')  # Empty file
        
        with self.assertRaises(AudioError) as context:
            self.media_manager.load_audio(audio_path)
        self.assertIn("Audio file is empty", str(context.exception))
    
    @patch('src.subtitle_creator.media_manager.AudioFileClip')
    def test_load_audio_enhanced_error_handling_codec_error(self, mock_audio_clip):
        """Test loading audio file with codec error."""
        audio_path = self.create_temp_file('test_audio.mp3')
        
        # Mock AudioFileClip to raise codec error
        mock_audio_clip.side_effect = Exception("codec not supported")
        
        with self.assertRaises(AudioError) as context:
            self.media_manager.load_audio(audio_path)
        self.assertIn("Audio codec not supported", str(context.exception))
        self.assertIn("Try converting the file to MP3 or WAV", str(context.exception))
    
    @patch('src.subtitle_creator.media_manager.AudioFileClip')
    def test_get_enhanced_audio_info(self, mock_audio_clip):
        """Test getting enhanced audio file information."""
        audio_path = self.create_temp_file('test_audio.mp3', b'x' * 1000000)  # 1MB file
        
        # Mock AudioFileClip
        mock_clip = Mock()
        mock_clip.duration = 60.0
        mock_clip.fps = 44100
        mock_clip.nchannels = 2
        mock_audio_clip.return_value = mock_clip
        
        info = self.media_manager.get_media_info(audio_path)
        
        self.assertEqual(info['media_type'], 'audio')
        self.assertEqual(info['duration'], 60.0)
        self.assertEqual(info['sample_rate'], 44100)
        self.assertEqual(info['channels'], 2)
        self.assertEqual(info['format'], 'MP3')
        self.assertIn('estimated_bitrate_kbps', info)
        self.assertGreater(info['estimated_bitrate_kbps'], 0)


if __name__ == '__main__':
    unittest.main()
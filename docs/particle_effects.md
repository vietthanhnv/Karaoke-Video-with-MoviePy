# Particle Effects System

The particle effects system provides dynamic visual enhancements for subtitle videos using MoviePy-based particle sprites with precise timing integration.

## Overview

The particle effects system consists of:

- **Base ParticleEffect class**: Foundation for all particle-based effects
- **Concrete particle effects**: Hearts, stars, music notes, sparkles, and custom images
- **Physics simulation**: Gravity, wind forces, and realistic particle motion
- **Timing integration**: Precise synchronization with subtitle timing and MoviePy rendering
- **Effect composition**: Multiple particle effects can be layered and combined

## Available Particle Effects

### HeartParticleEffect

Creates floating heart particles perfect for romantic or love-themed content.

**Key Parameters:**

- `heart_color`: RGBA color tuple for hearts (default: deep pink)
- `heart_size`: Size of heart particles in pixels (8-64)
- `pulse_enabled`: Enable pulsing animation (default: True)
- `pulse_rate`: Pulse rate in beats per second (0.5-5.0)
- `float_pattern`: Movement pattern - 'rising', 'floating', or 'spiral'

**Example:**

```python
heart_effect = HeartParticleEffect("romantic_hearts", {
    'particle_count': 15,
    'emission_rate': 3.0,
    'heart_color': (255, 105, 180, 255),  # Hot pink
    'pulse_enabled': True,
    'float_pattern': 'rising'
})
```

### StarParticleEffect

Creates twinkling star particles for magical or celebratory content.

**Key Parameters:**

- `star_color`: RGBA color tuple for stars (default: bright yellow)
- `star_points`: Number of star points (4-8)
- `twinkle_enabled`: Enable twinkling animation (default: True)
- `twinkle_rate`: Twinkle rate in flashes per second (0.5-10.0)
- `trail_enabled`: Enable star trail effect

**Example:**

```python
star_effect = StarParticleEffect("magical_stars", {
    'particle_count': 25,
    'star_color': (255, 215, 0, 255),  # Gold
    'twinkle_enabled': True,
    'twinkle_rate': 3.0
})
```

### MusicNoteParticleEffect

Creates floating musical note particles with rhythm synchronization.

**Key Parameters:**

- `note_color`: RGBA color tuple for notes (default: blue violet)
- `note_type`: Note type - 'quarter', 'eighth', 'sixteenth', or 'mixed'
- `rhythm_sync`: Synchronize emission with musical rhythm
- `beat_duration`: Beat duration for rhythm sync in seconds
- `bounce_on_beat`: Make notes bounce on beat
- `staff_lines`: Show musical staff lines

**Example:**

```python
note_effect = MusicNoteParticleEffect("rhythm_notes", {
    'particle_count': 20,
    'rhythm_sync': True,
    'beat_duration': 0.5,  # 120 BPM
    'bounce_on_beat': True
})
```

### SparkleParticleEffect

Creates small, bright sparkle particles with rapid twinkling animations.

**Key Parameters:**

- `sparkle_size_variation`: Size variation factor (0.1-2.0)
- `flash_duration`: Duration of sparkle flash in seconds (0.05-0.5)
- `burst_mode`: Emit sparkles in bursts rather than continuously
- `burst_interval`: Interval between bursts in seconds (0.5-5.0)
- `radial_spread`: Spread sparkles radially from center

**Example:**

```python
sparkle_effect = SparkleParticleEffect("celebration_sparkles", {
    'particle_count': 40,
    'burst_mode': True,
    'burst_interval': 0.8,
    'radial_spread': True
})
```

### CustomImageParticleEffect

Allows users to use their own images as particle sprites.

**Key Parameters:**

- `image_path`: Path to custom particle image file
- `image_scale`: Scale factor for custom image (0.1-5.0)
- `color_tint`: Color tint to apply to image (RGBA)
- `preserve_aspect`: Preserve image aspect ratio when scaling
- `random_flip`: Randomly flip images horizontally
- `blend_mode`: Blend mode - 'normal', 'add', 'multiply', 'screen'

**Supported Formats:** PNG, JPG, JPEG, GIF, BMP, TIFF

**Example:**

```python
custom_effect = CustomImageParticleEffect("custom_particles", {
    'image_path': 'assets/particles/custom_sprite.png',
    'image_scale': 1.5,
    'random_flip': True
})
```

## Physics System

All particle effects support realistic physics simulation:

### Gravity

- Controls vertical acceleration of particles
- Range: -500 to 500 pixels per second squared
- Negative values make particles float upward
- Positive values make particles fall downward

### Wind Force

- Controls horizontal acceleration of particles
- Range: -200 to 200 pixels per second squared
- Negative values create leftward wind
- Positive values create rightward wind

### Velocity and Motion

- Initial velocity is randomized within specified ranges
- Particles follow realistic physics equations: `position = initial_position + velocity * time + 0.5 * acceleration * time²`
- Rotation can be applied with configurable rotation speed

## Timing Integration

Particle effects integrate precisely with subtitle timing:

### Emission Timing

- Particles are emitted at precise intervals based on `emission_rate`
- Emission starts when subtitle line begins
- Emission duration is controlled by line duration and particle count

### Particle Lifetime

- Each particle has an individual lifetime
- Fade-in and fade-out effects can be applied
- Particles automatically disappear after their lifetime expires

### Synchronization Modes

- **Continuous**: Particles emit continuously during subtitle duration
- **Burst**: Particles emit in synchronized bursts
- **Rhythm Sync**: Particles emit synchronized to musical beats (MusicNoteParticleEffect)

## Effect Composition

Multiple particle effects can be combined:

```python
# Create effect system
system = EffectSystem()

# Register particle effects
system.register_effect(HeartParticleEffect)
system.register_effect(StarParticleEffect)
system.register_effect(SparkleParticleEffect)

# Create and add effects
hearts = system.create_effect("HeartParticleEffect", {...})
stars = system.create_effect("StarParticleEffect", {...})
sparkles = system.create_effect("SparkleParticleEffect", {...})

system.add_effect(hearts)
system.add_effect(stars)
system.add_effect(sparkles)

# Apply all effects to video
result_clip = system.apply_effects(base_clip, subtitle_data)
```

## Performance Considerations

### Particle Count

- Higher particle counts create more impressive effects but require more processing
- Recommended ranges:
  - Light effects: 5-15 particles
  - Medium effects: 15-30 particles
  - Heavy effects: 30-50 particles
  - Avoid exceeding 100 particles per effect

### Emission Rate

- Controls how quickly particles are generated
- Higher rates create denser effects but use more memory
- Balance emission rate with particle lifetime to avoid memory buildup

### Physics Complexity

- Simple physics (no gravity/wind) renders faster
- Complex physics with multiple forces requires more computation
- Consider disabling physics for background effects

## Best Practices

### Romantic/Love Themes

```python
hearts = HeartParticleEffect("romantic", {
    'particle_count': 12,
    'heart_color': (255, 105, 180, 255),  # Hot pink
    'pulse_enabled': True,
    'float_pattern': 'rising',
    'gravity': -30.0  # Gentle upward float
})
```

### Celebration/Party Themes

```python
# Combine stars and sparkles
stars = StarParticleEffect("celebration_stars", {
    'particle_count': 20,
    'star_color': (255, 215, 0, 255),  # Gold
    'twinkle_enabled': True
})

sparkles = SparkleParticleEffect("celebration_sparkles", {
    'particle_count': 30,
    'burst_mode': True,
    'radial_spread': True
})
```

### Musical/Rhythm Content

```python
notes = MusicNoteParticleEffect("musical", {
    'particle_count': 16,
    'rhythm_sync': True,
    'beat_duration': 0.5,  # Match song BPM
    'bounce_on_beat': True
})
```

### Magical/Fantasy Themes

```python
stars = StarParticleEffect("magical", {
    'particle_count': 25,
    'star_color': (138, 43, 226, 255),  # Purple
    'twinkle_enabled': True,
    'trail_enabled': True
})
```

## Error Handling

The particle effects system includes comprehensive error handling:

- **Invalid parameters**: Automatically validated with clear error messages
- **Missing image files**: Custom image effects fall back to default particles
- **Physics errors**: Invalid physics values (NaN, infinity) are rejected
- **Memory management**: Particle count and lifetime are automatically limited
- **Graceful degradation**: Effects continue working even if some particles fail

## Integration with MoviePy

Particle effects are designed to work seamlessly with MoviePy:

- Uses `ImageClip` for custom particle sprites
- Integrates with `CompositeVideoClip` for layering
- Supports MoviePy's animation functions for smooth motion
- Compatible with MoviePy's timing and duration system
- Optimized for video export and preview rendering

## Future Enhancements

Planned improvements for the particle effects system:

- **3D particle effects**: Depth and perspective simulation
- **Particle collision detection**: Particles that interact with each other
- **Advanced physics**: Fluid dynamics, magnetic forces, orbital motion
- **Particle trails**: Motion blur and trail effects
- **Interactive particles**: Particles that respond to audio frequency analysis
- **Particle presets**: Pre-configured effect combinations for common themes

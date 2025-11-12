# GenBricks - Procedural LEGO Building Generator

Generate brick models in LDRAW format using procedural generation.

## Features

- **Procedural Generation**: Create buildings from simple parameters
- **LDRAW Format Output**: Generate `.ldr` files compatible with LDRAW viewers (LDView, Bricklink Studio, etc.)
- **Customizable Parameters**: Control dimensions, colors, windows, doors, and roofs
- **Randomization Support**: Add variation to building generation
- **Multiple Roof Types**: Flat, pitched, and complex roof designs
- **Architectural Styles**: Simple, detailed, and modern building designs

## Quick Start

### Basic Usage

```bash
python genbricks.py --config config.yaml
```

This generates a building based on the parameters in `config.yaml` and outputs to `building.ldr`.

### With Randomization

```bash
python genbricks.py --config config.yaml --random
```

Enables randomization for parameters that have random settings configured.

### Advanced Example

```bash
python genbricks.py --config config_advanced.yaml
```

Uses the advanced configuration with pitched roof and multi-floor design.

## Configuration Parameters

### Building Dimensions
All dimensions are in **studs** (LEGO units) unless otherwise specified.

- **length**: Building length in studs (default: 20)
- **width**: Building width in studs (default: 15)
- **height**: Building height in bricks (default: 8)

### Windows
- **window_size**: `[width, height]` in studs (default: `[2, 2]`)
- **window_spacing**: Spacing between windows in studs (default: 2)

### Doors
- **door_size**: `[width, height]` - width in studs, height in bricks (default: `[2, 3]`)
- **number_of_doors**: Total doors distributed across walls (default: 1)

### Colors
Available color names: `black`, `blue`, `green`, `red`, `dark_red`, `yellow`, `white`, `light_gray`, `dark_gray`, `brown`, `tan`, `dark_tan`

- **wall_color**: Color for walls (default: "dark_gray")
- **roof_color**: Color for roof (default: "dark_red")

### Roof Options
- **roof_type**: Type of roof - `flat`, `pitched`, or `complex` (default: "flat")

### Advanced Settings
- **num_floors**: Number of floors (default: 1)
- **floor_height**: Height per floor in bricks (default: 8)
- **architectural_style**: Building style - `simple`, `detailed`, or `modern` (default: "simple")
- **output_file**: Output filename (default: "building.ldr")

### Randomization

Enable randomization on any parameter:

```yaml
length:
  value: 20
  random:
    enabled: true
    strength: 0.2      # Variation strength (0.0-1.0)
    range: [15, 25]    # Min/max range
```

## Configuration File Format

GenBricks uses YAML configuration files. Here's a complete example:

```yaml
# Building dimensions
width: 24
length: 16
height: 8

# Window and door settings
window_size: [2, 2]
window_spacing: 4
door_size: [2, 3]
number_of_doors: 2

# Colors
wall_color: "light_gray"
roof_color: "dark_red"

# Roof configuration
roof_type: "pitched"

# Output
output_file: "my_building.ldr"
```

## LDRAW Output Format

The generated `.ldr` files follow the LDRAW format specification:
- Compatible with LDRAW-based software (LDView, Bricklink Studio, LeoCAD, etc.)
- Uses standard LEGO brick parts from the LDRAW parts library
- Optimizes brick placement for realistic construction
- Proper coordinate system and rotation matrices

### Coordinate System
- **X-axis**: Left (-) to Right (+)
- **Y-axis**: Top (-) to Bottom (+)
- **Z-axis**: Near (-) to Far (+)
- **Units**: LDraw Units (LDU), where 20 LDU = 1 stud spacing

## Examples

### Simple House
```yaml
width: 16
length: 16
height: 8
window_size: [2, 2]
window_spacing: 3
door_size: [2, 3]
number_of_doors: 1
wall_color: "white"
roof_color: "dark_red"
roof_type: "pitched"
output_file: "house.ldr"
```

### Modern Building
```yaml
width: 32
length: 24
height: 12
window_size: [2, 2]
window_spacing: 2
door_size: [2, 4]
number_of_doors: 2
wall_color: "dark_gray"
roof_color: "black"
roof_type: "flat"
architectural_style: "modern"
output_file: "modern_building.ldr"
```

### Medieval Tower
```yaml
width: 12
length: 12
height: 16
window_size: [1, 1]
window_spacing: 4
door_size: [2, 3]
number_of_doors: 1
wall_color: "dark_tan"
roof_color: "dark_gray"
roof_type: "complex"
output_file: "tower.ldr"
```

## Viewing Your Models

After generating an `.ldr` file, you can view it using:

1. **LDView** - Free LDRAW model viewer
2. **Bricklink Studio** - Advanced LEGO CAD software
3. **LeoCAD** - Cross-platform LEGO CAD application
4. **MLCAD** - Classic LDRAW editor

## Technical Details

### Brick Selection Algorithm
The generator automatically selects optimal brick sizes to fill spaces efficiently:
- Prioritizes larger bricks (1x8, 1x6, 1x4) for better stability
- Uses smaller bricks (1x3, 1x2, 1x1) to fill remaining gaps
- Properly handles openings (doors and windows)

### Wall Generation
- Distributes doors across the four walls
- Places windows at configurable spacing
- Maintains structural integrity around openings
- Proper corner connections

### Roof Generation
- **Flat**: Simple plate-based roof
- **Pitched**: Stepped layers creating a slope
- **Complex**: Advanced multi-level roof structure

## Development

### File Structure
- `genbricks.py` - Main application and building logic
- `ldraw_generator.py` - LDRAW format generation and brick placement
- `config.yaml` - Default configuration
- `config_advanced.yaml` - Advanced configuration example

### Dependencies
- Python 3.7+
- PyYAML (for configuration parsing)

## Future Enhancements

Planned features:
- More architectural elements (balconies, stairs, chimneys)
- Texture variations and patterns
- Interior generation
- Multi-building layouts
- Custom brick part support
- Integration with BrickLink catalog

## License

Open source - feel free to modify and extend!

## Contributing

Contributions welcome! Areas for improvement:
- Additional roof styles
- More building types (castles, modern skyscrapers, etc.)
- Better window and door placement algorithms
- Interior room generation
- Landscape/terrain generation

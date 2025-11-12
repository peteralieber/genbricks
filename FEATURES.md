# GenBricks - Feature Documentation

## Overview
GenBricks is a procedural LEGO building generator that creates 3D models in LDRAW format. It transforms simple YAML configuration files into fully-detailed brick models that can be viewed and edited in LDRAW-compatible software.

## Core Features

### 1. LDRAW Format Output
- **Standard Compliance**: Generates `.ldr` files following LDRAW format specification
- **Compatible Software**: Works with LDView, Bricklink Studio, LeoCAD, MLCAD
- **Optimized Brick Selection**: Automatically chooses optimal brick sizes (1x8, 1x6, 1x4, etc.)
- **Proper Coordinate System**: Uses LDRAW units (LDU) with correct 3D positioning

### 2. Parametric Building Generation
Configure every aspect of your building:
- **Dimensions**: Length, width, height (in studs and bricks)
- **Windows**: Size, spacing, automatic placement
- **Doors**: Size, quantity, distributed across walls
- **Colors**: Wall and roof colors from LDRAW palette
- **Roof Types**: Flat, pitched, or complex designs

### 3. Intelligent Wall Generation
- **Opening Management**: Proper handling of doors and windows
- **Corner Connections**: Walls correctly join at corners
- **Structural Integrity**: Bricks placed around openings maintain stability
- **Multi-wall Support**: Front, back, left, and right walls with independent configurations

### 4. Roof System
Three roof types supported:
- **Flat**: Simple plate-based roof
- **Pitched**: Stepped layers creating a sloped appearance
- **Complex**: Multi-level architectural roof (future enhancement)

### 5. Color System
Built-in LDRAW color palette:
- black, blue, green, red, dark_red
- yellow, white, light_gray, dark_gray
- brown, tan, dark_tan

### 6. Randomization Support
Add variation to procedural generation:
- **Per-Parameter**: Enable randomization for any parameter
- **Range-Based**: Define min/max ranges
- **Strength Control**: Fine-tune variation intensity (0.0-1.0)

## Technical Specifications

### LDRAW Format Details
```
Line Type 1: Part Reference
1 <color> <x> <y> <z> <a> <b> <c> <d> <e> <f> <g> <h> <i> <part.dat>
```

### Coordinate System
- **X-axis**: Left (-) to Right (+)
- **Y-axis**: Top (-) to Bottom (+)
- **Z-axis**: Near (-) to Far (+)
- **Origin**: Building centered at (0, 0, 0)

### Brick Dimensions
- Standard brick height: 24 LDU
- Plate height: 8 LDU
- Stud spacing: 20 LDU

### Supported Brick Parts
The generator uses these LDRAW parts:
- 3005.dat (1x1), 3004.dat (1x2), 3622.dat (1x3)
- 3010.dat (1x4), 3009.dat (1x6), 3008.dat (1x8)
- 3003.dat (2x2), 3002.dat (2x3), 3001.dat (2x4)

## Configuration Examples

### Minimal Configuration
```yaml
width: 16
length: 16
height: 8
output_file: "simple.ldr"
```

### Full-Featured Configuration
```yaml
# Building dimensions
width: 32
length: 24
height: 12

# Windows and doors
window_size: [2, 2]
window_spacing: 3
door_size: [2, 4]
number_of_doors: 2

# Appearance
wall_color: "tan"
roof_color: "dark_red"
roof_type: "pitched"

# Advanced
num_floors: 2
floor_height: 6
architectural_style: "detailed"
output_file: "complex_building.ldr"
```

### With Randomization
```yaml
width:
  value: 20
  random:
    enabled: true
    range: [18, 24]

length:
  value: 16
  random:
    enabled: true
    strength: 0.2
```

## Use Cases

### Architecture and Design
- **Prototyping**: Quickly iterate on building designs
- **Education**: Teach architectural concepts with LEGO
- **Visualization**: Preview building layouts before physical construction

### Game Development
- **Procedural Cities**: Generate varied buildings for game worlds
- **Asset Creation**: Create unique LEGO-style buildings
- **Level Design**: Populate environments with diverse structures

### LEGO MOC Creation
- **Planning**: Design custom buildings digitally first
- **Part Estimation**: Know brick requirements before building
- **Documentation**: Share designs in standard LDRAW format

## Architecture

### Module Structure
```
genbricks/
├── genbricks.py          # Main application, building logic
├── ldraw_generator.py    # LDRAW format generation
├── config.yaml           # Default configuration
├── config_advanced.yaml  # Advanced example
├── config_house.yaml     # House example
└── config_tower.yaml     # Tower example
```

### Key Classes
- `LegoBuildingConfig`: Configuration data structure
- `LDrawModel`: LDRAW model container
- `BuildingGenerator`: Building generation logic
- `LDrawBrick`: Individual brick representation

### Generation Pipeline
1. **Configuration Loading**: Parse YAML config
2. **Parameter Processing**: Apply randomization if enabled
3. **Logical Wall Generation**: Create wall structures with openings
4. **LDRAW Conversion**: Convert to LDRAW bricks and coordinates
5. **Roof Generation**: Add roof structure
6. **File Output**: Write LDRAW file

## Performance

### Brick Count Estimates
- Small building (16x16x8): ~120-150 bricks
- Medium building (24x24x12): ~180-220 bricks
- Large building (32x32x16): ~300-400 bricks
- Tower (10x10x20): ~150-200 bricks

### Generation Speed
- Typical building: <1 second
- Complex building with randomization: <2 seconds

## Future Enhancements

### Planned Features
- [ ] Interior room generation
- [ ] Stairs and multi-level buildings
- [ ] Balconies and architectural details
- [ ] Texture patterns on walls
- [ ] Custom brick part support
- [ ] Multi-building layouts
- [ ] Landscape/terrain integration
- [ ] BrickLink part catalog integration
- [ ] Interactive GUI

### Advanced Roof Types
- [ ] Gabled roofs
- [ ] Hip roofs
- [ ] Mansard roofs
- [ ] Dome structures

### Architectural Styles
- [ ] Medieval castles
- [ ] Modern skyscrapers
- [ ] Victorian houses
- [ ] Industrial buildings

## Limitations

### Current Constraints
- Buildings are rectangular (no complex floor plans)
- Openings are simple rectangular cutouts
- No interior walls or rooms
- Limited roof complexity
- No curved structures

### LDRAW Compatibility
- Requires LDRAW parts library for viewing
- Colors limited to standard LDRAW palette
- Some specialized LEGO parts not yet supported

## Best Practices

### Configuration Tips
1. Keep dimensions divisible by 2 for better brick alignment
2. Window spacing should be >= window width
3. Door size should fit within wall height
4. Use color names for readability

### Optimization
1. Larger bricks reduce part count
2. Simpler roofs generate faster
3. Fewer openings = more efficient brick placement

### Viewing Your Models
1. Use LDView for quick preview
2. Use Bricklink Studio for detailed editing
3. Check brick inventory before physical building

## Contributing

Areas where contributions would be valuable:
- Additional brick parts support
- More roof types
- Interior generation
- Custom architectural styles
- Performance optimizations
- Documentation improvements

## License

Open source - MIT License (to be added)

## Credits

Created by the GenBricks team
Built with Python and the LDRAW format specification

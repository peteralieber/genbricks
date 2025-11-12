# GenBricks Usage Examples

This guide shows practical examples of using GenBricks to create different types of buildings.

## Quick Start

### Generate Default Building
```bash
python genbricks.py --config config.yaml
```
Output: `building.ldr` (16x24 studs, 8 bricks high, 136 bricks)

### Generate with Randomization
```bash
python genbricks.py --config config_random.yaml --random
```
Each run creates a unique building with randomized dimensions!

## Example Configurations

### 1. Simple House
**File**: `config_house.yaml`
```bash
python genbricks.py --config config_house.yaml
```

**Features:**
- 16x20 studs
- 10 bricks high
- White walls with dark red pitched roof
- Single front door
- Windows on all sides
- Output: 128 bricks

**Use Case**: Perfect starter building, residential design

### 2. Advanced Building
**File**: `config_advanced.yaml`
```bash
python genbricks.py --config config_advanced.yaml
```

**Features:**
- 24x32 studs (larger footprint)
- 12 bricks high
- Tan walls with dark red pitched roof
- Single door
- Detailed window placement
- Output: 188 bricks

**Use Case**: Commercial building, larger structures

### 3. Tower
**File**: `config_tower.yaml`
```bash
python genbricks.py --config config_tower.yaml
```

**Features:**
- 10x10 studs (compact footprint)
- 20 bricks high (tall!)
- Dark gray walls with dark tan flat roof
- Small windows
- Single door
- Output: 173 bricks

**Use Case**: Defensive tower, vertical structure, landmark

### 4. Random Building
**File**: `config_random.yaml`
```bash
python genbricks.py --config config_random.yaml --random
```

**Features:**
- Variable dimensions (14-24 length, 16-28 width, 8-14 height)
- Tan walls with dark red pitched roof
- Random door count (1-3)
- Each generation is unique!

**Use Case**: Procedural city generation, variety in designs

## Custom Configurations

### Minimal Configuration
Create a new file `my_building.yaml`:
```yaml
width: 12
length: 12
height: 6
output_file: "my_building.ldr"
```

Run:
```bash
python genbricks.py --config my_building.yaml
```

### Full Custom Building
```yaml
# Medieval castle wall segment
width: 40
length: 8
height: 16

window_size: [1, 1]
window_spacing: 6
door_size: [2, 4]
number_of_doors: 1

wall_color: "dark_tan"
roof_color: "dark_gray"
roof_type: "flat"

output_file: "castle_wall.ldr"
```

### Modern Skyscraper Base
```yaml
# Ground floor of modern building
width: 48
length: 48
height: 8

window_size: [2, 2]
window_spacing: 2
door_size: [3, 4]
number_of_doors: 4

wall_color: "dark_gray"
roof_color: "black"
roof_type: "flat"

output_file: "skyscraper_base.ldr"
```

## Advanced Techniques

### 1. Building Variations
Generate multiple variations of the same building:
```bash
for i in {1..5}; do 
    python genbricks.py --config config_random.yaml --random
    mv random_building.ldr "building_${i}.ldr"
done
```

### 2. Different Roof Types

**Flat Roof** (modern look):
```yaml
roof_type: "flat"
roof_color: "dark_gray"
```

**Pitched Roof** (traditional look):
```yaml
roof_type: "pitched"
roof_color: "dark_red"
```

### 3. Color Schemes

**Medieval/Fantasy:**
```yaml
wall_color: "dark_tan"
roof_color: "brown"
```

**Modern/Industrial:**
```yaml
wall_color: "dark_gray"
roof_color: "black"
```

**Residential:**
```yaml
wall_color: "white"
roof_color: "dark_red"
```

**Natural/Rustic:**
```yaml
wall_color: "tan"
roof_color: "brown"
```

## Viewing Your Models

After generation, open the `.ldr` file in:

1. **LDView** (Free, cross-platform)
   - Download from ldview.sourceforge.net
   - Open your `.ldr` file
   - Navigate with mouse: rotate, zoom, pan

2. **Bricklink Studio** (Free, feature-rich)
   - Download from stud.io
   - Import `.ldr` file
   - Edit, render, generate instructions

3. **LeoCAD** (Free, cross-platform)
   - Download from leocad.org
   - Open `.ldr` file
   - Add additional parts, create scenes

## Tips and Tricks

### Optimizing Brick Count
- Use larger dimensions divisible by common brick sizes (2, 4, 6, 8)
- Simpler roofs use fewer pieces
- Fewer openings = less complex wall structure

### Creating Realistic Buildings
- Keep proportions realistic (height ~= length or width)
- Use appropriate door sizes (2-3 studs wide)
- Space windows evenly (spacing >= window width)
- Match colors to real-world buildings

### Troubleshooting

**Building looks wrong in viewer?**
- Check configuration values are positive
- Ensure dimensions are reasonable (< 100 studs)
- Verify color names are valid

**Too many/few bricks?**
- Adjust dimensions
- Change roof type (pitched uses more plates)
- Modify window/door count

**Want more variety?**
- Enable randomization in config
- Use `--random` flag
- Adjust random ranges

## Next Steps

1. Experiment with different configurations
2. Combine multiple buildings into a scene
3. Modify generated files in LDRAW editor
4. Share your creations!

## Resources

- LDRAW Official Site: ldraw.org
- LDRAW Parts Library: ldraw.org/parts/latest-parts.html
- LDView Download: ldview.sourceforge.net
- Bricklink Studio: stud.io
- LeoCAD: leocad.org

Happy building! 🧱

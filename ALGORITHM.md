# GenBricks Algorithm White Paper

## Executive Summary

GenBricks is a procedural LEGO building generation system that creates structured building models with configurable parameters. The system takes dimensional and architectural specifications as input and generates a complete building layout with walls, windows, and doors placed deterministically based on mathematical spacing algorithms.

## Purpose and Goals

**Primary Goal**: Generate procedurally defined LEGO buildings for LDraw format output, enabling automated creation of building models with architectural features.

**Design Philosophy**:
- Deterministic generation from configuration parameters
- Support for optional randomization within controlled ranges
- Extensible architecture for future feature additions
- Mathematical precision in element placement

## System Architecture

### High-Level Flow

```
Input (YAML Config) → Config Parser → Building Generator → Wall Builder → Output (Wall Lists)
```

### Component Overview

1. **Configuration System**: Parses YAML input and creates typed configuration objects
2. **Parameter Wrapper**: Wraps values with optional randomization settings
3. **Building Generator**: Orchestrates the creation of all four walls
4. **Wall Builder**: Core algorithm for placing bricks, windows, and doors
5. **Output System**: Currently console output; designed for LDraw export

---

## Input Specification

### Configuration File Format (YAML)

The system accepts configuration through YAML files with the following parameters:

#### Building Dimensions
```yaml
length: <integer>    # Building length in LDU (LEGO Design Units)
width: <integer>     # Building width in LDU
height: <integer>    # Building height in rows (default: 8)
```

#### Architectural Features
```yaml
window_size: [width, height]     # Window dimensions [w, h]
window_spacing: <integer>         # Space between windows in LDU
door_size: [width, height]        # Door dimensions [w, h]
number_of_doors: <integer>        # Total doors across all walls
primary_brick_type: <string>      # BrickLink part ID (optional)
```

#### Advanced Configuration (Extended Format)

For parameters with randomization:
```yaml
parameter_name:
  value: <base_value>
  random:
    enabled: <boolean>
    strength: <float>      # 0.0 to 1.0
    range: [min, max]      # Optional bounds
```

### Example Configurations

**Basic Configuration**:
```yaml
length: 16
width: 24
height: 8
door_size: [4, 6]
number_of_doors: 5
window_size: [3, 3]
window_spacing: 2
```

**Advanced Configuration with Randomization**:
```yaml
length:
  value: 20
  random:
    enabled: true
    strength: 0.3
    range: [15, 25]
width:
  value: 15
  random:
    enabled: true
    strength: 0.2
    range: [12, 20]
window_size: [3, 3]
door_size: [4, 6]
number_of_doors: 4
```

### Command-Line Interface

```bash
python genbricks.py [-c CONFIG] [-r]

Options:
  -c, --config CONFIG    Path to YAML configuration file
  -r, --random          Enable random generation features
```

---

## Data Structures

### Core Classes

#### `RandomSetting`
```python
@dataclass
class RandomSetting:
    enabled: bool           # Whether randomization is active
    strength: float        # Intensity of randomization (0.0-1.0)
    range: Optional[Tuple[float, float]]  # Min/max bounds
```

#### `ParamWithRandom`
```python
@dataclass
class ParamWithRandom:
    value: any                           # The actual parameter value
    random: RandomSetting                # Associated randomization settings
```

#### `LegoBuildingConfig`
```python
@dataclass
class LegoBuildingConfig:
    length: ParamWithRandom              # Building length
    width: ParamWithRandom               # Building width
    height: ParamWithRandom              # Building height
    window_size: ParamWithRandom         # Window dimensions
    window_spacing: ParamWithRandom      # Spacing between windows
    door_size: ParamWithRandom           # Door dimensions
    number_of_doors: ParamWithRandom     # Total door count
    primary_brick_type: str              # BrickLink part ID
```

---

## Core Algorithm

### Building Generation Process

#### 1. Configuration Loading and Validation

**Function**: `parse_config(config_path)` and `createLegoBuildingConfig(config)`

**Process**:
1. Load YAML configuration file
2. Parse each parameter into `ParamWithRandom` wrapper
3. Handle both simple values and complex random configurations
4. Apply default values for missing parameters
5. Validate configuration completeness

#### 2. Door Distribution Algorithm

**Function**: `generateSotBuilding(config, random)`

The system distributes doors across four walls using a ceiling division strategy:

```
total_doors = config.number_of_doors.value

1. Front wall:  ⌈total_doors / 4⌉
2. Back wall:   ⌈(total_doors - front_doors) / 3⌉
3. Left wall:   ⌈(total_doors - front_doors - back_doors) / 2⌉  
4. Right wall:  ⌈(total_doors - front_doors - back_doors - left_doors) / 2⌉
```

**Rationale**: This algorithm distributes doors across walls with each remaining wall getting approximately (remaining_doors / remaining_walls), using ceiling division to handle fractional doors. This ensures all doors are distributed even with rounding.

#### 3. Wall Building Algorithm

**Function**: `buildWall(length, height, primary_brick_type, window_size, window_spacing, door_size, num_doors)`

This is the core placement algorithm that generates each wall row by row.

##### Algorithm Parameters
- `length`: Wall length in LDU
- `height`: Wall height in rows
- `window_size`: (width, height) tuple
- `window_spacing`: Gap between windows
- `door_size`: (width, height) tuple
- `num_doors`: Number of doors for this wall

##### Constants
```python
brick_len = 2          # Standard brick length in LDU
window_base = 2        # Row where windows start appearing
door_buffer = 4        # Minimum distance from corner before first door
```

##### Row-by-Row Generation Logic

For each row `r` from 0 to `height-1`:

**Step 1: Determine What to Place**
```
place_doors = (door_spacing > 0) AND 
              (door_size.width > 0) AND 
              (door_size.height > 0) AND 
              (r < door_size.height)

place_windows = (window_size.width > 0) AND 
                (window_size.height > 0) AND 
                (r >= window_base) AND 
                (r < window_base + window_size.height)
```

**Step 2: Calculate Spacing**
```python
door_spacing = length / num_doors  (if num_doors > 0)
window_cycle = window_size.width + window_spacing
```

**Step 3: Iterate Across Wall Length**

Starting from `wall_loc = 0`, increment by element width:

```python
while wall_loc < length:
    # Calculate if a door should start at this position
    # (position after buffer, aligned with door spacing)
    door_start = place_doors and (((wall_loc - door_buffer) % door_spacing) == 0)
    
    # Priority 1: Place door if conditions are met
    if place_doors and (doors_remaining > 0) and door_start:
        place_door()
        wall_loc += door_size.width
        doors_remaining -= 1
    
    # Priority 2: Place window if aligned with window cycle
    # Window positions start at window_spacing/2 offset
    # and repeat every (window_size.width + window_spacing) units
    elif place_windows and \
         (float(wall_loc - window_spacing/2) % float(window_size.width + window_spacing) == 0):
        place_window()
        wall_loc += window_size.width
    
    # Priority 3: Fill with brick
    else:
        place_brick()
        wall_loc += brick_len
```

##### Placement Priority Rules

1. **Doors take precedence** over windows and bricks
2. **Windows take precedence** over bricks
3. **Bricks fill all remaining space**
4. **Doors only appear** in rows 0 to door_height-1
5. **Windows only appear** in rows window_base to window_base+window_height-1

##### Mathematical Placement Logic

**Door Position Calculation**:
```
door_spacing = length / num_doors  (when num_doors > 0)
door_positions = positions where (position - door_buffer) % door_spacing == 0
                 AND position >= door_buffer
                 AND doors_remaining > 0
```

The actual door positions depend on the iteration through wall_loc, checking at each brick position if it aligns with the door spacing pattern.

**Window Position Calculation**:
```
window_cycle = window_size.width + window_spacing
window_positions = positions where (position - window_spacing/2) % window_cycle == 0
```

The modulo arithmetic ensures windows repeat at regular intervals across the wall length.

---

## Output Format

### Current Output Structure

The system currently generates console output with the following structure:

#### Wall Representation

Each wall is represented as a list of rows:
```python
wall = [
    [row_0_elements],  # Bottom row
    [row_1_elements],
    ...
    [row_n_elements]   # Top row
]
```

Each element is a tuple:
```python
(element_type, position)
```

Where:
- `element_type`: "brick", "window", or "door"
- `position`: Starting position in LDU along the wall

#### Example Output

```python
[
    [('brick', 0), ('brick', 2), ('door', 4), ('brick', 8), ('brick', 10)],
    [('brick', 0), ('brick', 2), ('door', 4), ('brick', 8), ('brick', 10)],
    [('brick', 0), ('brick', 2), ('window', 4), ('brick', 7), ('brick', 9)],
    ...
]
```

### Future Output Extensions

#### Planned LDraw Export Format

The output structure is designed to facilitate LDraw file generation:

```ldraw
0 FILE building.ldr
0 Building generated by GenBricks
0 Author: GenBricks
1 <color> <x> <y> <z> <a> <b> <c> <d> <e> <f> <g> <h> <i> <part_number>
```

Each element will translate to:
- **Brick**: Standard brick part with calculated position
- **Window**: Window part or transparent brick
- **Door**: Door frame part or opening

---

## Algorithm Characteristics

### Determinism

The algorithm is **fully deterministic** when randomization is disabled:
- Same configuration always produces identical output
- Element positions are mathematically calculated
- No dependency on random number generation

### Complexity Analysis

**Time Complexity**: O(L × H × W)
- Where L = length, H = height, W = width
- Each wall cell is visited once
- Placement decisions are O(1)

**Space Complexity**: O(L × H × W)
- Output structure stores all wall elements
- Linear in the number of building elements

### Scalability Considerations

**Current Limitations**:
- No optimization for large buildings
- Full structure stored in memory
- No streaming or chunked processing

**Scalability Factors**:
- Linear scaling with building volume
- Memory usage proportional to number of elements
- Performance suitable for typical LEGO building sizes

---

## Extension Points for Future Development

### 1. Randomization System (Framework Present)

**Current State**: Infrastructure exists but not implemented  
**Implementation Path**:
- Add random number generation in `generateSotBuilding()`
- Apply `RandomSetting.strength` to parameter values
- Respect `RandomSetting.range` bounds
- Use seed for reproducibility

**Example Randomization Logic**:
```python
if param.random.enabled and random_mode:
    base_value = param.value
    strength = param.random.strength
    min_val, max_val = param.random.range
    
    # Apply randomness
    randomized_value = base_value + random.uniform(-strength, strength) * base_value
    
    # Clamp to range
    final_value = max(min_val, min(max_val, randomized_value))
```

### 2. LDraw Export System

**Required Components**:
1. LDraw file format writer
2. Part library integration (BrickLink → LDraw mapping)
3. Coordinate transformation (wall coords → 3D space)
4. Color specification system

**File Structure**:
```
genbricks/
  ├── exporters/
  │   ├── ldraw_exporter.py
  │   ├── part_library.py
  │   └── coordinate_transformer.py
```

### 3. Advanced Architectural Features

**Potential Additions**:
- Roof generation (flat, pitched, complex)
- Interior walls and rooms
- Multiple floors/stories
- Architectural styles (modern, classical, etc.)
- Textured surfaces and decorative elements
- Stairs and elevators

**Implementation Pattern**:
```python
def generateRoof(config: RoofConfig, building_config: LegoBuildingConfig):
    # Roof generation algorithm
    pass
```

### 4. Window and Door Variations

**Current Limitation**: Single window/door type per building  
**Enhancement Path**:
- Multiple window styles (arched, bay, etc.)
- Different door types (single, double, garage)
- Window patterns (regularly vs. irregularly spaced)
- Corner windows and wrap-around features

**Configuration Extension**:
```yaml
windows:
  - type: "standard"
    size: [3, 3]
    rows: [2, 3, 4]
  - type: "arched"
    size: [3, 4]
    rows: [5, 6]
```

### 5. Advanced Placement Algorithms

**Current Algorithm**: Simple linear placement  
**Enhancements**:
- Symmetry modes (centered, balanced)
- Custom placement patterns
- Architectural proportion rules (golden ratio)
- Offset/staggered brick patterns for realism

### 6. Multi-Building Scenes

**Scene Generation**:
- Multiple buildings with spacing
- Street layouts
- Building variety within scenes
- Landscape elements

### 7. Validation and Error Handling

**Current State**: Minimal validation  
**Improvements Needed**:
- Parameter range validation
- Geometric feasibility checks
- Conflict detection (overlapping elements)
- Warning system for suboptimal configurations

### 8. Performance Optimizations

**For Large Buildings**:
- Lazy evaluation of wall sections
- Streaming output generation
- Parallel wall generation
- Memory-efficient data structures

---

## Configuration Guidelines for AI-Assisted Development

### Editing Input Specification

**File**: `ALGORITHM.md` → "Input Specification" section  
**To Add New Parameters**:
1. Update YAML specification section
2. Add to `LegoBuildingConfig` dataclass
3. Update `createLegoBuildingConfig()` parser
4. Document in "Example Configurations"

**Template**:
```yaml
# In ALGORITHM.md
new_parameter: <type>    # Description

# In genbricks.py
@dataclass
class LegoBuildingConfig:
    ...
    new_parameter: ParamWithRandom = field(default_factory=lambda: ParamWithRandom(default_value))
```

### Editing Core Algorithm

**File**: `ALGORITHM.md` → "Core Algorithm" section  
**Key Functions to Modify**:
- `buildWall()`: Element placement logic
- `generateSotBuilding()`: Building-level orchestration
- Door distribution: Modify ceiling division formulas

**Testing Changes**:
```bash
# Create test configuration
echo "length: 16" > test_config.yaml
echo "width: 24" >> test_config.yaml
echo "number_of_doors: 4" >> test_config.yaml

# Run with test config
python genbricks.py -c test_config.yaml
```

### Editing Output Format

**File**: `ALGORITHM.md` → "Output Format" section  
**Current**: Console output with wall lists  
**To Extend**: Add new exporter module

**Implementation Path**:
1. Create `exporters/` directory
2. Implement exporter class with common interface
3. Call exporter from `generateSotBuilding()`
4. Update documentation with new format specification

---

## Development Workflow for AI Agents

### Task: Add New Feature

1. **Read this document** to understand system architecture
2. **Identify extension point** from "Extension Points" section
3. **Update relevant sections** of this document with new design
4. **Implement code changes** following existing patterns
5. **Test with sample configurations**
6. **Update documentation** to reflect changes

### Task: Modify Algorithm Logic

1. **Review "Core Algorithm"** section for current logic
2. **Create test configuration** that exercises the change
3. **Run baseline test** before modifications
4. **Implement changes** to algorithm
5. **Verify output** matches expected behavior
6. **Update algorithm description** in this document

### Task: Add New Parameter

1. **Update "Input Specification"** with new parameter
2. **Modify `LegoBuildingConfig`** dataclass
3. **Update parser** in `createLegoBuildingConfig()`
4. **Use parameter** in appropriate algorithm function
5. **Add example** to documentation
6. **Test** with YAML configuration

---

## Known Limitations and Issues

### Current Limitations

1. **No 3D Output**: Currently only generates abstract wall representations
2. **Simplified Geometry**: Does not account for brick interlocking patterns
3. **Single Brick Type**: Doesn't use different brick sizes for efficiency
4. **No Collision Detection**: May place elements that overlap
5. **Fixed Wall Structure**: Doesn't support openings beyond doors/windows
6. **No Interior**: Only generates exterior walls

### Potential Issues

1. **Window/Door Overlap**: If spacing parameters are poorly chosen, elements may overlap
2. **Incomplete Walls**: If dimensions aren't multiples of brick size, walls may not complete perfectly
3. **Door Distribution**: Ceiling division may result in uneven door distribution
4. **Edge Cases**: Very small buildings (< 4 LDU) may not handle correctly

### Recommendations for Robustness

1. **Add parameter validation**: Check for valid ranges and relationships
2. **Implement conflict resolution**: Detect and resolve element overlaps
3. **Add warnings**: Notify user of suboptimal configurations
4. **Geometric validation**: Ensure building is physically constructable

---

## Testing Strategy

### Manual Testing

**Basic Functionality Test**:
```bash
# Test with provided config
python genbricks.py -c config.yaml

# Test with minimal config
python genbricks.py

# Test with randomization
python genbricks.py -c config.yaml -r
```

### Configuration Test Cases

**Test Case 1: Small Building**
```yaml
length: 8
width: 8
height: 4
door_size: [2, 3]
number_of_doors: 1
```

**Test Case 2: Large Building with Windows**
```yaml
length: 32
width: 24
height: 12
window_size: [3, 3]
window_spacing: 2
door_size: [4, 6]
number_of_doors: 6
```

**Test Case 3: Edge Case - No Doors/Windows**
```yaml
length: 10
width: 10
height: 5
```

### Validation Criteria

- ✓ All walls generate without errors
- ✓ Doors are distributed across walls
- ✓ Windows appear in appropriate rows
- ✓ Bricks fill all remaining space
- ✓ No overlapping elements in output
- ✓ Wall length matches configuration

---

## Glossary

**LDU (LEGO Design Unit)**: Standard unit of measurement in LEGO digital design, where 1 LDU = 1/64 of an inch or approximately 0.4mm

**LDraw**: An open standard for LEGO CAD programs, defining file formats for LEGO digital designs

**BrickLink**: Online marketplace and database for LEGO parts with standardized part numbering

**Procedural Generation**: Algorithmic creation of content using parameters and rules rather than manual specification

**ParamWithRandom**: Wrapper structure that combines a parameter value with optional randomization settings

**Wall List**: Data structure representing a wall as a list of rows, each containing positioned elements

**Element**: Generic term for brick, window, or door component in the wall structure

**Deterministic**: Property where the same input always produces the same output (no randomness)

---

## Conclusion

GenBricks provides a foundation for procedural LEGO building generation with a clean, extensible architecture. The current implementation focuses on basic rectangular buildings with configurable dimensions and openings, with a clear path forward for expansion into more complex architectural features, randomization, and LDraw output.

The algorithm's deterministic nature and mathematical placement logic ensure predictable results while the randomization framework provides flexibility for variation. The modular design separates concerns (configuration, generation, building, output) to facilitate independent enhancement of each component.

This white paper serves as both documentation of the current system and a roadmap for future AI-assisted development, providing clear extension points and guidelines for modification.

---

## Document Version History

- **Version 1.0** (Initial Release): Initial algorithm white paper creation
  - Complete documentation of existing system
  - Analysis of code structure and goals
  - Extension points and development guidelines

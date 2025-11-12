import argparse
import yaml
from dataclasses import dataclass, field
from typing import Tuple, Optional, List
import math
import random
from ldraw_generator import (
    LDrawModel, BuildingGenerator, LDrawColor, BrickType,
    convert_wall_to_ldraw
)

@dataclass
class RandomSetting:
    enabled: bool = False
    strength: float = 0.0  # 0.0 to 1.0, how strong the randomness is applied
    range: Optional[Tuple[float, float]] = None  # (min, max) for the parameter

@dataclass
class ParamWithRandom:
    value: any
    random: RandomSetting = field(default_factory=RandomSetting)

@dataclass
class LegoBuildingConfig:
    length: ParamWithRandom = field(default_factory=lambda: ParamWithRandom(20))
    width: ParamWithRandom = field(default_factory=lambda: ParamWithRandom(15))
    height: ParamWithRandom = field(default_factory=lambda: ParamWithRandom(8))
    window_size: ParamWithRandom = field(default_factory=lambda: ParamWithRandom((2, 2)))
    window_spacing: ParamWithRandom = field(default_factory=lambda: ParamWithRandom(2))
    door_size: ParamWithRandom = field(default_factory=lambda: ParamWithRandom((2, 3)))
    number_of_doors: ParamWithRandom = field(default_factory=lambda: ParamWithRandom(1))
    primary_brick_type: str = ""  # BrickLink part id
    # Enhanced parameters
    wall_color: str = "dark_gray"  # Color name or code
    roof_type: str = "flat"  # flat, pitched, complex
    roof_color: str = "dark_red"
    num_floors: int = 1
    floor_height: int = 8  # Height per floor in bricks
    output_file: str = "building.ldr"  # Output filename
    architectural_style: str = "simple"  # simple, detailed, modern

def createLegoBuildingConfig(config: dict) -> 'LegoBuildingConfig':
    """
    Create a LegoBuildingConfig instance from a config dict,
    wrapping values in ParamWithRandom as needed.
    """
    def param_with_random_from_dict(val):
        if isinstance(val, dict) and 'value' in val:
            # If config provides random settings, use them
            random_cfg = val.get('random', {})
            random_setting = RandomSetting(
                enabled=random_cfg.get('enabled', False),
                strength=random_cfg.get('strength', 0.0),
                range=tuple(random_cfg['range']) if 'range' in random_cfg else None
            )
            return ParamWithRandom(val['value'], random_setting)
        else:
            # Just a value, wrap in ParamWithRandom with default random settings
            return ParamWithRandom(val, RandomSetting())

    # Prepare kwargs for LegoBuildingConfig
    kwargs = {}
    non_param_fields = ["primary_brick_type", "wall_color", "roof_type", 
                        "roof_color", "num_floors", "floor_height", 
                        "output_file", "architectural_style"]
    
    for field_name in LegoBuildingConfig.__dataclass_fields__:
        if field_name in non_param_fields:
            # Not a ParamWithRandom, just assign directly
            if field_name in config:
                kwargs[field_name] = config[field_name]
        else:
            if field_name in config:
                kwargs[field_name] = param_with_random_from_dict(config[field_name])
    return LegoBuildingConfig(**kwargs)

def buildWall(length, height, primary_brick_type, window_size, window_spacing, door_size, num_doors):
    """
    Build a wall with windows and doors. The wall is built from left to right. 

    Doors are placed on the wall with a buffer from the corner, and max 2 doors. 
    Windows are placed spaced evenly across the wall, avoiding the doors. 
    The primary brick type is used for the wall, with smaller bricks to fill in 
    gaps for doors and windows.
    """
    print(f"Building wall of length {length}, height {height}, "
          f"with primary brick type {primary_brick_type}.")
    print(f"Window size: {window_size}, Window spacing: {window_spacing}, "
          f"Door size: {door_size}, Number of front doors: {num_doors}")
    
    brick_len = 2 # Assuming each brick has a length of 2 units
    window_base = 2 # The base row for windows
    
    # Build the wall
    wall_list = []
    wall_loc = 0
    
    # Create rows of bricks, windows, and doors, starting from the bottom
    # the door and window heights and widths are used to deterministically
    # place them across the wall. For rows below the window base, no
    # windows are placed. For rows above the window base, and below the 
    # door height, both windows and doors are placed. For rows above the
    # door height, only windows are placed.
    for row in range(height):
        row_list = []
        front_doors_left = num_doors
        door_buffer = 4 # Buffer space before placing a door
        door_spacing = (float(length) / (float(num_doors))) if num_doors > 0 else 0.0
        place_doors = (door_spacing > 0) and (door_size.value[0] > 0) and (door_size.value[1] > 0) and (row < door_size.value[1])
        place_windows = (window_size.value[0] > 0) and (window_size.value[1] > 0) and (row >= window_base) and (row < (window_base + window_size.value[1]))
        # print(f"door_size: {door_size}, window_size: {window_size}, window_spacing: {window_spacing}")
        wall_loc = 0
        while wall_loc < length:
            # print(f"Current wall location: {wall_loc}")
            door_start = place_doors and (((wall_loc - door_buffer) % door_spacing) == 0)
            place_window = place_windows and (float(wall_loc - window_spacing.value/2) % float(window_size.value[0] + window_spacing.value) == 0)
            if (place_doors and (front_doors_left > 0) and door_start):
                # Place a door
                print(f"    Placing door at position {wall_loc}")
                row_list.append(("door", wall_loc))
                wall_loc += door_size.value[0]
                front_doors_left -= 1
            elif (place_windows and place_window):
                # Place a window
                print(f"    Placing window at position {wall_loc}")
                row_list.append(("window", wall_loc))
                wall_loc += window_size.value[0]
            else: # Place a brick
                print
                row_list.append(("brick", wall_loc))
                wall_loc += brick_len

        wall_list.append(row_list)

    print(f"Wall built: {wall_list}")

    return wall_list

def generateSotBuilding(config: LegoBuildingConfig, random: bool = False):
    """
    Generate a building based on the provided LegoBuildingConfig.
    If random is True, apply randomness to the parameters.
    Returns the LDRAW model.
    """
    
    # For now, just print the config
    print(f"Generating building with config: {config}")
    if random:
        print("Random generation enabled.")
    else:
        print("Random generation disabled.")

    # Apply randomization if enabled
    if random:
        apply_randomization(config)

    # Generate placement of windows and doors based on the config
    print(f"Length: {config.length.value}, Width: {config.width.value}, Height: {config.height.value}")
    print(f"Window Size: {config.window_size.value}, Spacing: {config.window_spacing.value}")
    print(f"Door Size: {config.door_size.value}, Number of Doors: {config.number_of_doors.value}")

    ## Build Front Wall
    num_front_doors = math.ceil(config.number_of_doors.value / 4)
    print("Front Wall:")
    front_wall = buildWall(
        config.length.value,
        config.height.value,
        config.primary_brick_type,
        config.window_size,
        config.window_spacing,
        config.door_size,
        num_front_doors
    )

    ## Build Back Wall
    num_back_doors = math.ceil((config.number_of_doors.value - num_front_doors) / 3)
    print("Back Wall:")
    back_wall = buildWall(
        config.length.value,
        config.height.value,
        config.primary_brick_type,
        config.window_size,
        config.window_spacing,
        config.door_size,   
        num_back_doors
    )

    ## Build Left Wall
    num_left_doors = math.ceil((config.number_of_doors.value - num_front_doors - num_back_doors) / 2)
    print("Left Wall:")
    left_wall = buildWall(
        config.width.value,
        config.height.value,
        config.primary_brick_type,
        config.window_size,
        config.window_spacing,
        config.door_size,
        num_left_doors
    )

    ## Build Right Wall
    num_right_doors = config.number_of_doors.value - num_front_doors - num_back_doors - num_left_doors
    print("Right Wall:")
    right_wall = buildWall(
        config.width.value,
        config.height.value,
        config.primary_brick_type,
        config.window_size,
        config.window_spacing,
        config.door_size,
        num_right_doors
    )
    
    # Convert to LDRAW format
    print("\n=== Converting to LDRAW format ===")
    ldraw_model = convert_to_ldraw(config, front_wall, back_wall, left_wall, right_wall)
    
    # Save the model
    output_file = config.output_file
    ldraw_model.save(output_file)
    print(f"\n✓ Building saved to: {output_file}")
    print(f"  Total bricks: {len(ldraw_model.bricks)}")
    
    return ldraw_model


def apply_randomization(config: LegoBuildingConfig):
    """Apply randomization to config parameters based on their random settings"""
    def randomize_param(param: ParamWithRandom):
        if not param.random.enabled:
            return
        
        if param.random.range:
            min_val, max_val = param.random.range
            if isinstance(param.value, tuple):
                # Randomize tuple values
                randomized = tuple(
                    random.uniform(min_val, max_val) 
                    for _ in range(len(param.value))
                )
                param.value = randomized
            else:
                param.value = random.uniform(min_val, max_val)
        else:
            # Apply strength-based randomization
            if isinstance(param.value, (int, float)):
                variation = param.value * param.random.strength
                param.value = param.value + random.uniform(-variation, variation)
    
    # Randomize all parameters
    randomize_param(config.length)
    randomize_param(config.width)
    randomize_param(config.height)
    randomize_param(config.window_size)
    randomize_param(config.window_spacing)
    randomize_param(config.door_size)
    randomize_param(config.number_of_doors)


def get_color_code(color_name: str) -> int:
    """Convert color name to LDRAW color code"""
    color_map = {
        'black': LDrawColor.BLACK.value,
        'blue': LDrawColor.BLUE.value,
        'green': LDrawColor.GREEN.value,
        'red': LDrawColor.RED.value,
        'dark_red': LDrawColor.DARK_RED.value,
        'yellow': LDrawColor.YELLOW.value,
        'white': LDrawColor.WHITE.value,
        'light_gray': LDrawColor.LIGHT_GRAY.value,
        'dark_gray': LDrawColor.DARK_GRAY.value,
        'brown': LDrawColor.BROWN.value,
        'tan': LDrawColor.TAN.value,
        'dark_tan': LDrawColor.DARK_TAN.value,
    }
    return color_map.get(color_name.lower(), LDrawColor.DARK_GRAY.value)


def convert_to_ldraw(config: LegoBuildingConfig, 
                     front_wall, back_wall, left_wall, right_wall) -> LDrawModel:
    """
    Convert the building specification to LDRAW format
    
    Args:
        config: Building configuration
        front_wall, back_wall, left_wall, right_wall: Wall data structures
    
    Returns:
        LDrawModel instance
    """
    model = LDrawModel(
        name="Procedural Building",
        description=f"Generated building {config.length.value}x{config.width.value}x{config.height.value}"
    )
    
    generator = BuildingGenerator(model)
    wall_color = get_color_code(config.wall_color)
    roof_color = get_color_code(config.roof_color)
    
    # Calculate building dimensions in studs
    length_studs = config.length.value
    width_studs = config.width.value
    height_bricks = config.height.value
    
    # Starting position (center the building at origin)
    base_x = -LDrawModel.studs_to_ldu(length_studs) / 2
    base_y = 0
    base_z = -LDrawModel.studs_to_ldu(width_studs) / 2
    
    print(f"Building dimensions: {length_studs}x{width_studs} studs, {height_bricks} bricks high")
    print(f"Wall color: {config.wall_color} (code: {wall_color})")
    
    # Build walls with openings extracted from wall data
    print("Converting front wall...")
    front_openings = extract_openings(front_wall, config)
    generator.build_wall(
        base_x, base_y, base_z,
        length_studs, height_bricks, wall_color,
        direction='x', openings=front_openings
    )
    
    print("Converting back wall...")
    back_openings = extract_openings(back_wall, config)
    back_z = base_z + LDrawModel.studs_to_ldu(width_studs)
    generator.build_wall(
        base_x, base_y, back_z,
        length_studs, height_bricks, wall_color,
        direction='x', openings=back_openings
    )
    
    print("Converting left wall...")
    left_openings = extract_openings(left_wall, config)
    generator.build_wall(
        base_x, base_y, base_z,
        width_studs, height_bricks, wall_color,
        direction='z', openings=left_openings
    )
    
    print("Converting right wall...")
    right_openings = extract_openings(right_wall, config)
    right_x = base_x + LDrawModel.studs_to_ldu(length_studs)
    generator.build_wall(
        right_x, base_y, base_z,
        width_studs, height_bricks, wall_color,
        direction='z', openings=right_openings
    )
    
    # Build roof
    print(f"Building {config.roof_type} roof...")
    roof_y = base_y - (height_bricks * LDrawModel.BRICK_HEIGHT)
    generator.build_roof(
        base_x, roof_y, base_z,
        width_studs, length_studs, 
        config.roof_type, roof_color
    )
    
    return model


def extract_openings(wall_data: List[List[Tuple]], config: LegoBuildingConfig) -> List[dict]:
    """Extract door and window positions from wall data"""
    openings = []
    
    # Track openings we've already added
    seen_openings = set()
    
    for row_idx, row in enumerate(wall_data):
        for item_type, position in row:
            if item_type in ['door', 'window']:
                # Convert position to studs
                position_studs = position // 2
                
                # Create unique key for this opening
                opening_key = (item_type, position_studs)
                
                if opening_key not in seen_openings:
                    seen_openings.add(opening_key)
                    
                    # Determine opening dimensions
                    if item_type == 'door':
                        width = config.door_size.value[0] // 2
                        height = config.door_size.value[1]
                    else:  # window
                        width = config.window_size.value[0] // 2
                        height = config.window_size.value[1]
                    
                    openings.append({
                        'type': item_type,
                        'position': position_studs,
                        'width': width,
                        'height': height,
                        'start_row': row_idx
                    })
    
    return openings

def create_parser():
    parser = argparse.ArgumentParser(description="Gen Bricks.")
    parser.add_argument('-c', '--config', 
                        type=str,
                        default=None,
                        required=False, 
                        help='Configuration File (YAML)')
    parser.add_argument('-r', '--random',
                        default=False,
                        action='store_true',
                        help='Enable random generation')
    return parser

def parse_config(config_path):
    if config_path is None:
        return {}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}

def main(args):
    # Your main logic here
    print(f"Received arguments: {args}")

    config = parse_config(args.config)
    if config:
        print(f"Loaded configuration: {config}")
    else:
        print("No configuration loaded.")

    # Create a LegoBuildingConfig instance from the config
    lego_config = createLegoBuildingConfig(config)
    print(f"Lego Building Config: {lego_config}")

    generateSotBuilding(lego_config, args.random)

if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    main(args)
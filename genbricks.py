import argparse
import yaml
from dataclasses import dataclass, field
from typing import Tuple, Optional
import math

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
    length: ParamWithRandom = field(default_factory=lambda: ParamWithRandom(0))
    width: ParamWithRandom = field(default_factory=lambda: ParamWithRandom(0))
    height: ParamWithRandom = field(default_factory=lambda: ParamWithRandom(0))
    window_size: ParamWithRandom = field(default_factory=lambda: ParamWithRandom((0, 0)))
    window_spacing: ParamWithRandom = field(default_factory=lambda: ParamWithRandom(0))
    door_size: ParamWithRandom = field(default_factory=lambda: ParamWithRandom((0, 0)))
    number_of_doors: ParamWithRandom = field(default_factory=lambda: ParamWithRandom(0))
    primary_brick_type: str = ""  # BrickLink part id

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
    for field_name in LegoBuildingConfig.__dataclass_fields__:
        if field_name == "primary_brick_type":
            # Not a ParamWithRandom, just assign directly
            if field_name in config:
                kwargs[field_name] = config[field_name]
        else:
            if field_name in config:
                kwargs[field_name] = param_with_random_from_dict(config[field_name])
    return LegoBuildingConfig(**kwargs)

def buildWall(length, height, primary_brick_type, window_size, window_spacing, door_size, num_front_doors):
    """
    Placeholder function to build a wall.
    This would contain the logic to create a wall with windows and doors.
    """
    print(f"Building wall of length {length}, height {height}, "
          f"with primary brick type {primary_brick_type}.")
    print(f"Window size: {window_size}, Window spacing: {window_spacing}, "
          f"Door size: {door_size}, Number of front doors: {num_front_doors}")
    
    brick_len = 2 # Assuming each brick has a length of 2 units
    
    # Build the wall
    wall_loc = 0
    wall_list = []
    front_doors_left = num_front_doors
    door_buffer = 2 # Buffer space before placing a door
    door_spacing = length / (num_front_doors + 1) if num_front_doors > 0 else 0
    print(f"door_size: {door_size}, window_size: {window_size}, window_spacing: {window_spacing}")
    while (wall_loc < length):
        print(f"Current wall location: {wall_loc}")
        if (front_doors_left > 0 and ((wall_loc - door_buffer) % door_spacing) < door_size.value[0]):
            # Place a door
            print(f"    Placing door at position {wall_loc}")
            wall_list.append(("door", wall_loc))
            wall_loc += door_size.value[0]
            front_doors_left -= 1
        elif ((window_size.value[0] > 0 and window_size.value[1] > 0) and 
              (wall_loc - window_spacing.value/2) % (window_size.value[0] + window_spacing.value) < window_size.value[0]):
            # Place a window
            print(f"    Placing window at position {wall_loc}")
            wall_list.append(("window", wall_loc))
            wall_loc += window_size.value[0]
        else: # Place a brick
            print
            wall_list.append(("brick", wall_loc))
            wall_loc += brick_len

    print(f"Wall built: {wall_list}")

    return wall_list

def generateSotBuilding(config: LegoBuildingConfig, random: bool = False):
    """
    Generate a building based on the provided LegoBuildingConfig.
    If random is True, apply randomness to the parameters.
    """
    
    # For now, just print the config
    print(f"Generating building with config: {config}")
    if random:
        print("Random generation enabled.")
    else:
        print("Random generation disabled.")

    # Generate placement of windows and doors based on the config
    print(f"Length: {config.length.value}, Width: {config.width.value}, Height: {config.height.value}")
    print(f"Window Size: {config.window_size.value}, Spacing: {config.window_spacing.value}")
    print(f"Door Size: {config.door_size.value}, Number of Doors: {config.number_of_doors.value}")

    ## Build Front Wall
    num_front_doors = math.ceil(config.number_of_doors.value / 4)
    front_wall = buildWall(
        config.length.value,
        config.height.value,
        config.primary_brick_type,
        config.window_size,
        config.window_spacing,
        config.door_size,
        num_front_doors
    )

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
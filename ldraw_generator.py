"""
LDRAW Format Generator for Procedural Lego Buildings
Generates .ldr files from building specifications
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class LDrawColor(Enum):
    """Common LDRAW color codes"""
    BLACK = 0
    BLUE = 1
    GREEN = 2
    RED = 4
    DARK_RED = 320
    YELLOW = 14
    WHITE = 15
    LIGHT_GRAY = 71
    DARK_GRAY = 72
    BROWN = 6
    TAN = 19
    DARK_TAN = 69


class BrickType(Enum):
    """Common brick types with their LDRAW part numbers"""
    BRICK_1x1 = "3005.dat"
    BRICK_1x2 = "3004.dat"
    BRICK_1x3 = "3622.dat"
    BRICK_1x4 = "3010.dat"
    BRICK_1x6 = "3009.dat"
    BRICK_1x8 = "3008.dat"
    BRICK_2x2 = "3003.dat"
    BRICK_2x3 = "3002.dat"
    BRICK_2x4 = "3001.dat"
    PLATE_1x1 = "3024.dat"
    PLATE_1x2 = "3023.dat"
    PLATE_1x4 = "3710.dat"
    PLATE_2x2 = "3022.dat"
    PLATE_2x4 = "3020.dat"
    # Special parts
    DOOR_1x4x6 = "60596.dat"
    WINDOW_1x2x2 = "60592.dat"
    WINDOW_1x4x3 = "4132.dat"


@dataclass
class LDrawBrick:
    """Represents a single brick in LDRAW format"""
    part: str
    color: int
    x: float
    y: float
    z: float
    rotation_matrix: Tuple[float, ...] = (1, 0, 0, 0, 1, 0, 0, 0, 1)
    
    def to_ldraw_line(self) -> str:
        """Convert brick to LDRAW line type 1 format"""
        return f"1 {self.color} {self.x} {self.y} {self.z} " \
               f"{self.rotation_matrix[0]} {self.rotation_matrix[1]} {self.rotation_matrix[2]} " \
               f"{self.rotation_matrix[3]} {self.rotation_matrix[4]} {self.rotation_matrix[5]} " \
               f"{self.rotation_matrix[6]} {self.rotation_matrix[7]} {self.rotation_matrix[8]} " \
               f"{self.part}"


class LDrawModel:
    """Container for an LDRAW model"""
    
    # LDRAW constants
    BRICK_HEIGHT = 24  # Standard brick height in LDU
    PLATE_HEIGHT = 8   # Plate height in LDU
    STUD_SPACING = 20  # Horizontal spacing between studs in LDU
    
    def __init__(self, name: str = "Building", description: str = ""):
        self.name = name
        self.description = description
        self.bricks: List[LDrawBrick] = []
        
    def add_brick(self, brick: LDrawBrick):
        """Add a brick to the model"""
        self.bricks.append(brick)
        
    def add_brick_at(self, part: str, color: int, x: float, y: float, z: float,
                     rotation_matrix: Tuple[float, ...] = (1, 0, 0, 0, 1, 0, 0, 0, 1)):
        """Add a brick at specific coordinates"""
        brick = LDrawBrick(part, color, x, y, z, rotation_matrix)
        self.add_brick(brick)
        
    def to_ldraw(self) -> str:
        """Convert entire model to LDRAW format"""
        lines = []
        
        # Header
        lines.append(f"0 {self.name}")
        lines.append(f"0 Name: {self.name.lower().replace(' ', '_')}.ldr")
        lines.append(f"0 Author: GenBricks Procedural Generator")
        if self.description:
            lines.append(f"0 {self.description}")
        lines.append("")
        
        # Add all bricks
        for brick in self.bricks:
            lines.append(brick.to_ldraw_line())
            
        return "\n".join(lines)
    
    def save(self, filename: str):
        """Save model to LDRAW file"""
        with open(filename, 'w') as f:
            f.write(self.to_ldraw())
            
    @staticmethod
    def get_brick_dimensions(brick_type: str) -> Tuple[int, int]:
        """Get brick dimensions in studs (width, length)"""
        brick_dims = {
            BrickType.BRICK_1x1.value: (1, 1),
            BrickType.BRICK_1x2.value: (1, 2),
            BrickType.BRICK_1x3.value: (1, 3),
            BrickType.BRICK_1x4.value: (1, 4),
            BrickType.BRICK_1x6.value: (1, 6),
            BrickType.BRICK_1x8.value: (1, 8),
            BrickType.BRICK_2x2.value: (2, 2),
            BrickType.BRICK_2x3.value: (2, 3),
            BrickType.BRICK_2x4.value: (2, 4),
            BrickType.PLATE_1x1.value: (1, 1),
            BrickType.PLATE_1x2.value: (1, 2),
            BrickType.PLATE_1x4.value: (1, 4),
            BrickType.PLATE_2x2.value: (2, 2),
            BrickType.PLATE_2x4.value: (2, 4),
        }
        return brick_dims.get(brick_type, (1, 1))
    
    @staticmethod
    def studs_to_ldu(studs: int) -> float:
        """Convert studs to LDraw units"""
        return studs * LDrawModel.STUD_SPACING
    
    @staticmethod
    def select_optimal_brick(length_studs: int) -> str:
        """Select the optimal brick size for a given length"""
        # Prefer larger bricks for efficiency
        if length_studs >= 8:
            return BrickType.BRICK_1x8.value
        elif length_studs >= 6:
            return BrickType.BRICK_1x6.value
        elif length_studs >= 4:
            return BrickType.BRICK_1x4.value
        elif length_studs >= 3:
            return BrickType.BRICK_1x3.value
        elif length_studs >= 2:
            return BrickType.BRICK_1x2.value
        else:
            return BrickType.BRICK_1x1.value


class BuildingGenerator:
    """Generate procedural buildings in LDRAW format"""
    
    def __init__(self, model: LDrawModel):
        self.model = model
        
    def place_brick_row(self, start_x: float, start_y: float, start_z: float,
                       length_studs: int, color: int, direction: str = 'x',
                       brick_height_type: str = 'brick'):
        """
        Place a row of bricks along a direction
        
        Args:
            start_x, start_y, start_z: Starting position
            length_studs: Total length in studs
            color: Brick color
            direction: 'x' or 'z' for horizontal direction
            brick_height_type: 'brick' or 'plate'
        """
        remaining = length_studs
        current_pos = 0
        
        rotation = (1, 0, 0, 0, 1, 0, 0, 0, 1)  # No rotation for x-direction
        if direction == 'z':
            rotation = (0, 0, 1, 0, 1, 0, -1, 0, 0)  # 90-degree rotation
        
        while remaining > 0:
            brick_part = LDrawModel.select_optimal_brick(remaining)
            brick_length = LDrawModel.get_brick_dimensions(brick_part)[1]
            
            # Calculate position
            if direction == 'x':
                x = start_x + LDrawModel.studs_to_ldu(current_pos)
                z = start_z
            else:  # direction == 'z'
                x = start_x
                z = start_z + LDrawModel.studs_to_ldu(current_pos)
            
            self.model.add_brick_at(brick_part, color, x, start_y, z, rotation)
            
            current_pos += brick_length
            remaining -= brick_length
    
    def build_wall(self, start_x: float, start_y: float, start_z: float,
                   length_studs: int, height_bricks: int, color: int,
                   direction: str = 'x', openings: Optional[List[dict]] = None):
        """
        Build a complete wall with optional openings (doors/windows)
        
        Args:
            start_x, start_y, start_z: Starting position
            length_studs: Wall length in studs
            height_bricks: Wall height in bricks
            color: Wall color
            direction: 'x' or 'z'
            openings: List of dicts with 'type', 'position', 'width', 'height'
        """
        openings = openings or []
        
        for row in range(height_bricks):
            y = start_y - (row * LDrawModel.BRICK_HEIGHT)
            
            # Check if this row has any openings
            row_openings = []
            for opening in openings:
                opening_start = opening.get('start_row', 0)
                opening_height = opening.get('height', 0)
                if opening_start <= row < opening_start + opening_height:
                    row_openings.append(opening)
            
            if not row_openings:
                # No openings, place full row
                self.place_brick_row(start_x, y, start_z, length_studs, color, direction)
            else:
                # Place bricks around openings
                positions = sorted([(0, 0)] + 
                                 [(op['position'], op['position'] + op['width']) 
                                  for op in row_openings] +
                                 [(length_studs, length_studs)])
                
                for i in range(len(positions) - 1):
                    start = positions[i][1] if i > 0 else 0
                    end = positions[i + 1][0] if i + 1 < len(positions) - 1 else length_studs
                    
                    if end > start:
                        segment_length = end - start
                        if direction == 'x':
                            segment_x = start_x + LDrawModel.studs_to_ldu(start)
                            segment_z = start_z
                        else:
                            segment_x = start_x
                            segment_z = start_z + LDrawModel.studs_to_ldu(start)
                        
                        self.place_brick_row(segment_x, y, segment_z, 
                                           segment_length, color, direction)
    
    def build_roof(self, start_x: float, start_y: float, start_z: float,
                   width_studs: int, length_studs: int, roof_type: str = 'flat',
                   color: int = LDrawColor.DARK_GRAY.value):
        """
        Build a roof structure
        
        Args:
            start_x, start_y, start_z: Starting position
            width_studs: Roof width in studs
            length_studs: Roof length in studs
            roof_type: 'flat', 'pitched', or 'complex'
            color: Roof color
        """
        if roof_type == 'flat':
            # Simple flat roof using plates
            for z_pos in range(0, width_studs, 2):
                z = start_z + LDrawModel.studs_to_ldu(z_pos)
                self.place_brick_row(start_x, start_y, z, length_studs, 
                                   color, 'x', 'plate')
        elif roof_type == 'pitched':
            # Simple pitched roof - create stepped layers
            layers = min(width_studs // 2, 4)
            for layer in range(layers):
                offset = layer
                z = start_z + LDrawModel.studs_to_ldu(offset)
                y = start_y - (layer * LDrawModel.PLATE_HEIGHT)
                row_length = length_studs - (2 * layer)
                if row_length > 0:
                    x = start_x + LDrawModel.studs_to_ldu(layer)
                    self.place_brick_row(x, y, z, row_length, color, 'x', 'plate')


def convert_wall_to_ldraw(wall_data: List[List[Tuple]], wall_id: str,
                          start_x: float, start_y: float, start_z: float,
                          direction: str, generator: BuildingGenerator,
                          wall_color: int = LDrawColor.DARK_GRAY.value):
    """
    Convert wall data from the original format to LDRAW bricks
    
    Args:
        wall_data: List of rows, each row is list of (type, position) tuples
        wall_id: Identifier for the wall (front, back, left, right)
        start_x, start_y, start_z: Starting coordinates
        direction: 'x' or 'z' for wall orientation
        generator: BuildingGenerator instance
        wall_color: Color for wall bricks
    """
    # Extract openings from wall_data
    openings = []
    
    for row_idx, row in enumerate(wall_data):
        for item_type, position in row:
            if item_type in ['door', 'window']:
                # Find or create opening entry
                opening_found = False
                for opening in openings:
                    if (opening['type'] == item_type and 
                        opening['position'] == position and
                        opening['start_row'] <= row_idx < opening['start_row'] + opening['height']):
                        opening_found = True
                        break
                
                if not opening_found:
                    # Determine opening size
                    width = 2 if item_type == 'window' else 2  # Default sizes
                    height = 2 if item_type == 'window' else 3
                    openings.append({
                        'type': item_type,
                        'position': position // 2,  # Convert from LDU to studs
                        'width': width,
                        'height': height,
                        'start_row': row_idx
                    })
    
    # Build the wall with openings
    length_studs = max(pos for row in wall_data for _, pos in row) // 2 + 1
    height_bricks = len(wall_data)
    
    generator.build_wall(start_x, start_y, start_z, length_studs, height_bricks,
                        wall_color, direction, openings)

from pyglet import shapes

class ElementShapeFactory:
    @staticmethod
    def create_fire_shape(x, y, color, batch):
        """Create chevron shape for fire particles"""
        size = 3
        left_line = shapes.Line(
            int(x - size), int(y - size//2),
            int(x), int(y + size//2),
            thickness=2, color=tuple(color), batch=batch
        )
        right_line = shapes.Line(
            int(x), int(y + size//2), 
            int(x + size), int(y - size//2),
            thickness=2, color=tuple(color), batch=batch
        )
        return [left_line, right_line]
    
    @staticmethod
    def create_water_shape(x, y, color, batch):
        """Create teardrop triangle for water particles"""
        return [shapes.Triangle(
            int(x + 1.5), int(y),      # Tip
            int(x - 1.5), int(y - 1),  # Bottom back
            int(x - 1.5), int(y + 1),  # Top back
            color=tuple(color), batch=batch
        )]
    
    @staticmethod
    def create_wind_shape(x, y, color, batch):
        """Create S-curve for wind particles"""
        line1 = shapes.Line(
            int(x - 4), int(y - 2), int(x - 1), int(y),
            thickness=2, color=tuple(color), batch=batch
        )
        line2 = shapes.Line(
            int(x - 1), int(y), int(x + 1), int(y),
            thickness=2, color=tuple(color), batch=batch
        )
        line3 = shapes.Line(
            int(x + 1), int(y), int(x + 4), int(y - 2),
            thickness=2, color=tuple(color), batch=batch
        )
        return [line1, line2, line3]
    
    @staticmethod
    def create_earth_shape(x, y, color, batch):
        """Create square for earth particles"""
        return [shapes.Rectangle(int(x-1), int(y-1), 3, 3, color=tuple(color), batch=batch)]
    
    @staticmethod
    def create_generic_shape(x, y, color, batch):
        """Create circle for generic particles"""
        return [shapes.Circle(x, y, radius=2, color=tuple(color), batch=batch)]
    
    @classmethod
    def create_shape_for_element(cls, element_type, x, y, color, batch):
        """Factory method to create appropriate shape for element type"""
        shape_creators = {
            "FIRE": cls.create_fire_shape,
            "WATER": cls.create_water_shape,
            "WIND": cls.create_wind_shape,
            "EARTH": cls.create_earth_shape,
        }
        
        creator = shape_creators.get(element_type, cls.create_generic_shape)
        return creator(x, y, color, batch)

    @staticmethod
    def update_shape_for_element(element_type, shape_elements, x, y):
        """Update shape positions based on element type"""
        if element_type == "FIRE":
            # Update chevron lines
            if len(shape_elements) >= 2:
                left_line, right_line = shape_elements[0], shape_elements[1]
                size = 3
                left_line.x, left_line.y = int(x - size), int(y - size//2)
                left_line.x2, left_line.y2 = int(x), int(y + size//2)
                right_line.x, right_line.y = int(x), int(y + size//2)
                right_line.x2, right_line.y2 = int(x + size), int(y - size//2)

        elif element_type == "WIND":
            # Update S-curve lines
            if len(shape_elements) >= 3:
                line1, line2, line3 = shape_elements[0], shape_elements[1], shape_elements[2]
                line1.x, line1.y = int(x - 4), int(y - 2)
                line1.x2, line1.y2 = int(x - 1), int(y)
                line2.x, line2.y = int(x - 1), int(y)
                line2.x2, line2.y2 = int(x + 1), int(y)
                line3.x, line3.y = int(x + 1), int(y)
                line3.x2, line3.y2 = int(x + 4), int(y - 2)

        elif element_type == "EARTH":
            # Update square
            if shape_elements:
                square = shape_elements[0]
                square.x, square.y = int(x-1), int(y-1)

        elif element_type == "WATER":
            # Update triangle (basic positioning - no anchor logic here)
            if shape_elements:
                tri = shape_elements[0]
                tri.x1, tri.y1 = int(x + 1.5), int(y)
                tri.x2, tri.y2 = int(x - 1.5), int(y - 1)
                tri.x3, tri.y3 = int(x - 1.5), int(y + 1)

        else:
            # Generic shape (circle)
            if shape_elements:
                shape = shape_elements[0]
                if hasattr(shape, 'x'):
                    shape.x, shape.y = int(x), int(y)
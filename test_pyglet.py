import pyglet
from pyglet import shapes

# Create window
window = pyglet.window.Window(width=800, height=600, caption="Pyglet Diamond Test")

# Set background color to white
pyglet.gl.glClearColor(1.0, 1.0, 1.0, 1.0)

# Create batch for rendering
batch = pyglet.graphics.Batch()

# Diamond coordinates (center at 400, 300, size 50)
center_x, center_y, size = 400, 300, 50
diamond_coords = [
    center_x, center_y + size,      # Top
    center_x + size, center_y,      # Right
    center_x, center_y - size,      # Bottom
    center_x - size, center_y       # Left
]

# Try to create diamond polygon
try:
    diamond = shapes.Polygon(diamond_coords, color=(139, 69, 19), batch=batch)
    diamond.opacity = 160
    print("✅ Diamond polygon created successfully!")
except Exception as e:
    print(f"❌ Polygon failed: {e}")
    # Fallback to rectangle
    diamond = shapes.Rectangle(center_x - size, center_y - size, size * 2, size * 2, 
                             color=(139, 69, 19), batch=batch)
    diamond.opacity = 160
    # The rectangle is then rotated around its anchor point:
    diamond.rotation = 45

@window.event
def on_draw():
    window.clear()
    batch.draw()

@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.ESCAPE:
        window.close()

print("Press ESC to exit")
pyglet.app.run()
import io_mesh_uv_layout
from bpy.props import FloatVectorProperty

from io_mesh_uv_layout.export_uv_png import *

try:
    # remove the original operator since it is going to modify RNA meta
    io_mesh_uv_layout.unregister()
except:
    pass

# A new export function that accept back ground color as argument.
def new_export(
    filepath, face_data, colors, width, height, opacity, bg_color=(0.0, 0.0, 0.0, 0.0)
):
    offscreen = gpu.types.GPUOffScreen(width, height)
    offscreen.bind()

    try:
        bgl.glClearColor(*bg_color)  # untuple it
        bgl.glClear(bgl.GL_COLOR_BUFFER_BIT)
        draw_image(face_data, opacity)

        pixel_data = get_pixel_data_from_current_back_buffer(width, height)
        save_pixels(filepath, pixel_data, width, height)
    finally:
        offscreen.unbind()
        offscreen.free()


# overwrite the original one
io_mesh_uv_layout.export_uv_png.export = new_export

# Add a new float property using annotation
# This need to be register again to create RNA meta again
io_mesh_uv_layout.ExportUVLayout.__annotations__['bg_color'] = FloatVectorProperty(
    name="Background Color",
    description="PNG Background Color",
    size=4,
    soft_min=0.0,
    soft_max=1.0,
    subtype='COLOR',
    default=(0.0, 0.0, 0.0, 0.0),
)  # not sure why the panel is working strange

# get a curried exporter using background color
def new_get_expt(self):
    if self.mode == 'PNG':
        from io_mesh_uv_layout import export_uv_png

        def curry_expt(*args):
            export_uv_png.export(
                *args,
                bg_color=self.bg_color,
            )

        return curry_expt
    elif self.mode == 'EPS':
        from io_mesh_uv_layout import export_uv_eps

        return export_uv_eps.export
    elif self.mode == 'SVG':
        from io_mesh_uv_layout import export_uv_svg

        return export_uv_svg.export
    else:
        assert False, "Should get one expt."


# overwrite the original get exporter
io_mesh_uv_layout.ExportUVLayout.get_exporter = new_get_expt

# register again
io_mesh_uv_layout.register()

import ezdxf
import math
import os

# starting point x-axis
sx = 0
# starting point y-axis
sy = 0
LISP_SCRIPT_TEMPLATE_NAME = 'ExportPDF.lsp'
TEMPORARY_LISP_SCRIPT_NAME = 'temporary_script.lsp'
OUTPUT_DIR = "D:\\\\6Szczytowe\\\\"

# Create a new DXF document.
doc = ezdxf.new(dxfversion='AC1024', setup=True)
DIM_STYLE = {
    'dimtxsty': 'LiberationMono',
    'dimtxt': 80,  # text height
    'dimlfac': 1,  # dim scale
    'dimrnd': 1,  # rounding dimensions
    'dimgap': 100,  # distance from text to dim line
    'dimexo': 40,  # distance of supporting line from model
    'dimblk': ezdxf.ARROWS.closed_filled,  # arrow style
    'dimasz': 60,  # arrow size
    'dimlwd': 15,  # dimline weight 15 → 0.15mm
    'dimpost': '<> mm',
}

try:
    # height in peak
    truss_height = int(input("Wysokość w kalenicy: "))
    # width
    w = int(input("Szerokość zew. muru: "))
    # angle
    angle = float(input("Kąt nachylenia dachu: "))
    # outrigger height (wysuwnica)
    outrigger_height = input("Wysokość wysuwnicy: (jeśli 120 zostaw puste)")
    # description
    description = input("Opis: ")
except:
    # some random values if wrong input or just want to skip data input
    # TODO real exception catching
    truss_height = 3011
    w = 8340
    angle = 20
    outrigger_height = 130
    description = "Test"

# some math calculation of not given dimensions
outrigger_height = 130 if outrigger_height == "" else int(outrigger_height) + 10
vertical_outrigger_height = outrigger_height / math.cos(math.radians(angle))
H = truss_height - math.floor(vertical_outrigger_height)
x = w / 2 * math.tan(math.radians(angle))
h = math.floor(H - x)

# beam on gable wall (wieniec skośny)
# dashed line offset by 100mm from gable wall outline
upper_beam_y = H - 100 / math.cos(math.radians(angle))
lower_beam_y = h - 100 / math.cos(math.radians(angle))
if lower_beam_y < sy:
    m = (upper_beam_y - lower_beam_y) / (w / 2 - 0)
    lower_beam_x = (0 - lower_beam_y) / m
    lower_beam_y = 0
else:
    lower_beam_x = 0

# setting group of coordinates
points_groups = {
    'gable_points': [(sx, sy), (sx + w, sy), (sx + w, sy + h), (sx + w / 2, sy + H), (sx, sy + h), (sx, sy)],
    'ring_beam_points': [(sx, sy - 300), (sx, sy), (sx + 240, sy), (sx + 240, sy - 300)],
    'ring_beam2_points': [(sx + w, sy - 300), (sx + w, sy), (sx + w - 240, sy), (sx + w - 240, sy - 300)],
}
dashed_points_groups = {'gable_beam_points': [(sx + lower_beam_x, sy + lower_beam_y), (sx + w / 2, sy + upper_beam_y),
                                              (sx + w - lower_beam_x, sy + lower_beam_y)]
                        }
# setting dimension coordinates
# dimensions [start_point, end_point, distance]
dimensions = [[(sx, sy), (sx + w, sy), -500],
              [(sx + w, sy + h), (sx + w, sy), 100],
              [(sx + w / 2, sy + H), (sx + w, sy + h), 100],
              [(sx, sy + h), (sx + w / 2, sy + H), 100],
              [(sx, sy), (sx, sy + h), 100],
              [(sx + w / 2, sy + H), (sx + w / 2, sy), 100]]

# prepare modelspace
doc.header['$LTSCALE'] = 100
msp = doc.modelspace()

# drawing walls
for points_group in points_groups.values():
    line_weight = 20
    points_group = list(map(lambda x: (x[0], x[1], line_weight, line_weight),
                            points_group))  # adding line weight on start and end of the lines
    msp.add_lwpolyline(points_group)

# drawing gable beam
for points_group in dashed_points_groups.values():
    line_weight = 1
    points_group = list(map(lambda x: (x[0], x[1], line_weight, line_weight),
                            points_group))  # adding line weight on start and end of the lines
    msp.add_lwpolyline(points_group, dxfattribs={'linetype': 'DASHED'})

# dimensioning
for dimension in dimensions:
    msp.add_aligned_dim(p1=dimension[0], p2=dimension[1], distance=dimension[2], override=DIM_STYLE).render()

# adding description above drawing
msp.add_text(
    description,
    dxfattribs={'height': 500, 'style': 'LiberationMono-Bold'
                }).set_pos((sx + w / 2, sy + H + 300), align='CENTER')
msp.add_text(
    'wieniec skośny o grubości minimum 10cm',
    dxfattribs={'height': 100, 'style': 'LiberationMono', 'rotation': -angle
                }).set_pos((sx + w/2+150, sy + H -350), align='LEFT')
msp.add_text(
    'wieniec skośny o grubości minimum 10cm',
    dxfattribs={'height': 100, 'style': 'LiberationMono', 'rotation': angle
                }).set_pos((sx + w/2-150, sy + H -350), align='RIGHT')

# set zoom on drawing
doc.set_modelspace_vport(height=2 * H, center=(sx + w / 2, sy + H / 2))

# save to dxf
dxf_filename = OUTPUT_DIR + "Szczytowa - " + description + ".dxf"
doc.saveas(dxf_filename)

# save to pdf (changing filename in lisp script template, save it to temporary lisp script and execute it
lisp_script = open(LISP_SCRIPT_TEMPLATE_NAME, 'r')
lisp_script_content = lisp_script.readlines()
lisp_script_content[0] = lisp_script_content[0].replace("test.dxf", dxf_filename)
lisp_script = open(TEMPORARY_LISP_SCRIPT_NAME, 'w')
for line in lisp_script_content:
    lisp_script.write(line)
lisp_script.close()
os.popen(TEMPORARY_LISP_SCRIPT_NAME)
os.startfile(OUTPUT_DIR)

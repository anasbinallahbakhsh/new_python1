import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ── Colour palette ────────────────────────────────────────────────────────────
BLUE   = "#4DA6D4"
ORANGE = "#F5A623"
DARK   = "#2C3E50"   # edge / outline colour

N = 4   # grid size (4×4×4)

# ── Which cubie faces are ORANGE ──────────────────────────────────────────────
# The image shows an "H / cross" stripe pattern on the left face and front face.
# We encode the pattern per visible surface:
#   LEFT  face  (x=0, facing –x):  column pattern seen on yz-plane
#   FRONT face  (y=0, facing –y):  column pattern seen on xz-plane
#   TOP   face  (z=N, facing +z):  all blue

def is_orange_left(row, col):
    """row = z index (0=bottom), col = y index (0=front).
       Returns True if that cell should be orange on the LEFT face."""
    # Vertical stripe at col 0 and col 2  →  'H' look
    return col in (0, 2)

def is_orange_front(row, col):
    """row = z index (0=bottom), col = x index (0=left).
       Returns True if that cell should be orange on the FRONT face."""
    return col in (1, 2)   # central columns give the same 'H' feel

# ── Drawing helpers ───────────────────────────────────────────────────────────

def draw_face(ax, verts, color, alpha=1.0):
    """Draw a single quad face."""
    poly = Poly3DCollection([verts], alpha=alpha)
    poly.set_facecolor(color)
    poly.set_edgecolor(DARK)
    poly.set_linewidth(0.8)
    ax.add_collection3d(poly)


def unit_cube_faces(i, j, k):
    """Return the 6 faces of the unit cube at grid position (i,j,k).
    Each face is a list of 4 (x,y,z) corners."""
    x0, x1 = i,   i+1
    y0, y1 = j,   j+1
    z0, z1 = k,   k+1
    return {
        "left":   [(x0,y0,z0),(x0,y1,z0),(x0,y1,z1),(x0,y0,z1)],  # x = i   (–x)
        "right":  [(x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1)],  # x = i+1 (+x)
        "front":  [(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1)],  # y = j   (–y)
        "back":   [(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)],  # y = j+1 (+y)
        "bottom": [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)],  # z = k   (–z)
        "top":    [(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)],  # z = k+1 (+z)
    }

# ── Main render ───────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(8, 8), facecolor="white")
ax  = fig.add_subplot(111, projection="3d")
ax.set_facecolor("white")``

for i in range(N):          # x  (left → right)
    for j in range(N):      # y  (front → back)
        for k in range(N):  # z  (bottom → top)
            faces = unit_cube_faces(i, j, k)

            # --- LEFT outer face  (i == 0) -----------------------------------
            if i == 0:
                row, col = k, j          # row = height, col = depth
                c = ORANGE if is_orange_left(row, col) else BLUE
                draw_face(ax, faces["left"], c)

            # --- FRONT outer face  (j == 0) ----------------------------------
            if j == 0:
                row, col = k, i          # row = height, col = width
                c = ORANGE if is_orange_front(row, col) else BLUE
                draw_face(ax, faces["front"], c)

            # --- TOP outer face  (k == N-1) ----------------------------------
            if k == N - 1:
                draw_face(ax, faces["top"], BLUE)   # top is all blue

# ── Axis / view settings ──────────────────────────────────────────────────────
ax.set_xlim(0, N)
ax.set_ylim(0, N)
ax.set_zlim(0, N)

ax.set_box_aspect([1, 1, 1])
ax.view_init(elev=30, azim=-50)      # isometric-ish viewpoint

ax.axis("off")
ax.set_title("4×4×4 Cube", fontsize=16, pad=10, color=DARK)

plt.tight_layout()
plt.savefig("/mnt/user-data/outputs/cube_3d.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved → cube_3d.png")


print("testing chagne")
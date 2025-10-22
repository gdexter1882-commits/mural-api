import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from grid_core import slugify

def generate_mockup(handle, rows, cols, total_pages, output_dir):
    # Layout constants
    page_w = 40  # px
    page_h = int(page_w * 1.6)
    margin = 10  # px
    row_gap = 6  # px
    font_size = 8

    # Canvas size
    canvas_w = margin * 2 + cols * page_w
    canvas_h = margin * 2 + rows * page_h + (rows - 1) * row_gap

    fig, ax = plt.subplots(figsize=(canvas_w / 100, canvas_h / 100), dpi=100)
    ax.set_xlim(0, canvas_w)
    ax.set_ylim(0, canvas_h)
    ax.axis("off")

    # Draw grid
    count = 1
    for r in range(rows):
        for c in range(cols):
            x = margin + c * page_w
            y = canvas_h - margin - (r + 1) * page_h - r * row_gap
            rect = Rectangle((x, y), page_w, page_h, edgecolor="black", facecolor="white", linewidth=0.5)
            ax.add_patch(rect)

            if count <= total_pages:
                ax.text(x + page_w / 2, y + page_h / 2, str(count),
                        ha="center", va="center", fontsize=font_size)
                count += 1

    # Save output
    os.makedirs(output_dir, exist_ok=True)
    slug = slugify(handle)
    out_path = os.path.join(output_dir, f"{slug}_grid.png")
    plt.savefig(out_path, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)

    return out_path
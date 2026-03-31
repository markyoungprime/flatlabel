import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import io

# Set page title
st.title("Sheet Metal Label Generator (No Swatch)")


# -----------------------------
# Font helpers
# -----------------------------
def find_font(candidates):
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height


# Prefer bundled fonts first for consistent rendering across environments
BOLD_FONT_CANDIDATES = [
    "./fonts/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]

REGULAR_FONT_CANDIDATES = [
    "./fonts/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]

bold_font_path = find_font(BOLD_FONT_CANDIDATES)
regular_font_path = find_font(REGULAR_FONT_CANDIDATES)

try:
    if not bold_font_path or not regular_font_path:
        raise FileNotFoundError("No suitable font files found.")

    large_font = ImageFont.truetype(bold_font_path, 235)   # Color title
    medium_font = ImageFont.truetype(bold_font_path, 108)  # Gauge
    small_font = ImageFont.truetype(regular_font_path, 55) # Origin
    status_font = ImageFont.truetype(bold_font_path, 140)  # Status

    st.success(
        f"Loaded fonts successfully. Bold: {bold_font_path} | Regular: {regular_font_path}"
    )
except Exception as e:
    st.error(f"Font loading error: {e}")
    large_font = ImageFont.load_default()
    medium_font = ImageFont.load_default()
    small_font = ImageFont.load_default()
    status_font = ImageFont.load_default()
    st.warning("Using default PIL font; layout and sizing may not match perfectly.")


# -----------------------------
# Input widgets
# -----------------------------
origin = st.text_input("Origin:", "Sheffield")
color = st.text_input("Color:", "")

gauge_options = ["26ga", "24ga", "22ga", ".032", "ZAM", "Other"]
gauge = st.selectbox("Gauge:", gauge_options, index=1)

if gauge == "Other":
    gauge = st.text_input("Enter custom gauge:", "")

status = st.selectbox("Status:", ["OPEN", "RESERVED"])
project = ""
if status == "RESERVED":
    project = st.text_input("Project Name:", "")


# -----------------------------
# Generate label
# -----------------------------
if st.button("Generate Label"):
    width, height = 1725, 586

    # Background and text colors
    bg_color = "black" if status == "RESERVED" else "white"
    text_color = "white" if status == "RESERVED" else "black"
    box_color = "black" if bg_color == "white" else "white"
    origin_text_color = "white" if box_color == "black" else "black"

    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    color_text = color.strip()
    origin_text = origin.upper().strip()
    status_text = ""
    if status == "RESERVED":
        status_text = project.strip() if project.strip() else "RESERVED"

    # -----------------------------
    # Top section: Color
    # -----------------------------
    color_x, color_y = 40, 36
    draw.text((color_x, color_y), color_text, font=large_font, fill=text_color)

    # Divider line
    draw.line([(0, 251), (1725, 251)], fill=text_color, width=5)

    # -----------------------------
    # Lower section: Gauge
    # -----------------------------
    gauge_x, gauge_y = 60, 361
    draw.text((gauge_x, gauge_y), gauge, font=medium_font, fill=text_color)

    gauge_width, gauge_height = get_text_size(draw, gauge, medium_font)

    shape_x0 = gauge_x - 20
    shape_y0 = gauge_y - 20
    shape_x1 = gauge_x + gauge_width + 20
    shape_y1 = gauge_y + gauge_height + 20

    # Circle for aluminum/custom gauges, square for standard steel gauges
    if gauge in [".032", ".040"] or gauge not in ["26ga", "24ga", "22ga"]:
        center_x = (shape_x0 + shape_x1) / 2
        center_y = (shape_y0 + shape_y1) / 2
        radius = max((shape_x1 - shape_x0), (shape_y1 - shape_y0)) / 2
        draw.ellipse(
            [
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
            ],
            outline=text_color,
            width=5,
        )
    else:
        side_length = max(gauge_width, gauge_height) + 40
        center_x = gauge_x + gauge_width / 2
        center_y = gauge_y + gauge_height / 2
        rect_x0 = center_x - side_length / 2
        rect_y0 = center_y - side_length / 2
        rect_x1 = center_x + side_length / 2
        rect_y1 = center_y + side_length / 2
        draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], outline=text_color, width=5)

    # -----------------------------
    # Lower section: Origin
    # -----------------------------
    origin_width, origin_height = get_text_size(draw, origin_text, small_font)
    origin_x = width - origin_width - 20
    origin_y = 461

    box_x0 = origin_x - 10
    box_y0 = origin_y - 10
    box_x1 = origin_x + origin_width + 10
    box_y1 = origin_y + origin_height + 10

    draw.rectangle([box_x0, box_y0, box_x1, box_y1], fill=box_color)
    draw.text((origin_x, origin_y), origin_text, font=small_font, fill=origin_text_color)

    # -----------------------------
    # Lower section: Status
    # -----------------------------
    if status == "RESERVED":
        status_width, status_height = get_text_size(draw, status_text, status_font)
        status_x = (width - status_width) / 2
        status_y = 421
        draw.text((status_x, status_y), status_text, font=status_font, fill=text_color)

    # Display image
    st.image(image, caption="Generated Label (No Swatch)", use_container_width=True)

    # Download button using in-memory buffer
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    st.download_button(
        label="Download Label",
        data=buffer,
        file_name="label_no_swatch.png",
        mime="image/png",
    )

# Note about saving on Streamlit Cloud
st.info(
    "Tip: for the most consistent font rendering, add DejaVuSans.ttf and DejaVuSans-Bold.ttf to a ./fonts folder in your app."
)

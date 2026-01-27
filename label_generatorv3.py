import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os

# Set page title
st.title("Sheet Metal Label Generator (No Swatch)")

# Font handling
try:
    font_path = "/System/Library/Fonts/Helvetica.ttc"
    if not os.path.exists(font_path):
        st.warning("Helvetica not found at /System/Library/Fonts/Helvetica.ttc, falling back to DejaVu Sans.")
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError("No suitable font found.")
    large_font = ImageFont.truetype(font_path, 235)   # Color title
    medium_font = ImageFont.truetype(font_path, 108)  # Gauge
    small_font = ImageFont.truetype(font_path, 55)    # Origin
    status_font = ImageFont.truetype(font_path, 140)  # Status/Project
    st.success(f"Fonts loaded successfully from {font_path}: 235pt, 108pt, 55pt, and 140pt.")
except Exception as e:
    st.error(f"Font loading error: {e}")
    large_font = ImageFont.load_default()
    medium_font = ImageFont.load_default()
    small_font = ImageFont.load_default()
    status_font = ImageFont.load_default()
    st.warning("Using default font; sizes may be smaller than expected.")

# Input widgets
origin = st.text_input("Origin:", "Sabre")
color = st.text_input("Color:", "")

gauge_options = ["26ga", "24ga", "22ga", ".032", ".040", "Other"]
gauge = st.selectbox("Gauge:", gauge_options, index=1)

if gauge == "Other":
    gauge = st.text_input("Enter custom gauge:", "")

status = st.selectbox("Status:", ["OPEN", "RESERVED"])
project = ""
if status == "RESERVED":
    project = st.text_input("Project Name:", "")

# Generate label function
if st.button("Generate Label"):
    width, height = 1725, 586  # Width 5.75in (1725px), height 1.95in (586px)

    # Background and text color based on status
    bg_color = "black" if status == "RESERVED" else "white"
    text_color = "white" if status == "RESERVED" else "black"
    box_color = "black" if bg_color == "white" else "white"  # Inverted for Origin box
    origin_text_color = "white" if box_color == "black" else "black"

    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # Helper: measure actual text size for the chosen font
    def text_size(draw_obj, text, font):
        x0, y0, x1, y1 = draw_obj.textbbox((0, 0), text, font=font)
        return (x1 - x0, y1 - y0)

    # Text
    color_text = color
    status_text = project if status == "RESERVED" and project else ("RESERVED" if status == "RESERVED" else "")
    origin_text = origin.upper()

    # Upper portion: Color title (simulated bold)
    x, y = 40, 36
    for offset_x in [-2, -1, 0, 1, 2]:
        for offset_y in [-2, -1, 0, 1, 2]:
            draw.text((x + offset_x, y + offset_y), color_text, font=large_font, fill=text_color)

    # Divider below color title
    draw.line([(0, 251), (width, 251)], fill=text_color, width=5)

    # Lower portion: Gauge, Origin, Status (Reserved only)
    # Gauge
    x, y = 60, 361
    gauge_width, gauge_height = text_size(draw, gauge, medium_font)

    for offset_x in [-2, -1, 0, 1, 2]:
        for offset_y in [-2, -1, 0, 1, 2]:
            draw.text((x + offset_x, y + offset_y), gauge, font=medium_font, fill=text_color)

    # Draw shape around Gauge (20px padding)
    shape_x0 = x - 20
    shape_y0 = y - 20
    shape_x1 = x + gauge_width + 20
    shape_y1 = y + gauge_height + 20

    if gauge in [".032", ".040"] or gauge not in ["26ga", "24ga", "22ga"]:
        # Circle for .032, .040, or custom
        center_x = (shape_x0 + shape_x1) / 2
        center_y = (shape_y0 + shape_y1) / 2
        radius = max(gauge_width, gauge_height) / 2 + 20
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            outline=text_color,
            width=5
        )
    else:
        # Square for 22ga, 24ga, 26ga
        side_length = max(gauge_width, gauge_height) + 40
        center_x = x + gauge_width / 2
        center_y = y + gauge_height / 2
        shape_x0 = center_x - side_length / 2
        shape_y0 = center_y - side_length / 2
        shape_x1 = center_x + side_length / 2
        shape_y1 = center_y + side_length / 2
        draw.rectangle([shape_x0, shape_y0, shape_x1, shape_y1], outline=text_color, width=5)

    # Origin (right-justified) + box sized from real font metrics
    origin_width, origin_height = text_size(draw, origin_text, small_font)
    origin_x = width - origin_width - 20
    origin_y = 461

    box_x0 = origin_x - 10
    box_y0 = origin_y - 10
    box_x1 = origin_x + origin_width + 10
    box_y1 = origin_y + origin_height + 10

    draw.rectangle([box_x0, box_y0, box_x1, box_y1], fill=box_color)
    draw.text((origin_x, origin_y), origin_text, font=small_font, fill=origin_text_color)

    # Status / Project (Reserved only)
    if status == "RESERVED":
        status_width, status_height = text_size(draw, status_text, status_font)
        status_x = (width - status_width) / 2
        status_y = 421
        draw.text((status_x, status_y), status_text, font=status_font, fill=text_color)

    # Display the image
    st.image(image, caption="Generated Label (No Swatch)", use_container_width=True)

    # Download button
    image.save("label_no_swatch.png", "PNG", quality=100)
    with open("label_no_swatch.png", "rb") as file:
        st.download_button(
            label="Download Label",
            data=file,
            file_name="label_no_swatch.png",
            mime="image/png"
        )

# Note about saving on Streamlit Cloud
st.info("Note: The 'Download Label' button allows you to save the label locally. Streamlit Cloud doesn't persist saved files.")

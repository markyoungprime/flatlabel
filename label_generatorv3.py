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
    large_font = ImageFont.truetype(font_path, 235)  # Color title, 235pt, bold
    medium_font = ImageFont.truetype(font_path, 108)  # Gauge, 108pt, bold
    small_font = ImageFont.truetype(font_path, 55)   # Origin, 55pt
    status_font = ImageFont.truetype(font_path, 140)  # Status (Reserved), 140pt
    st.success(f"Fonts loaded successfully from {font_path}: 235pt, 108pt, 55pt, and 140pt.")
except Exception as e:
    st.error(f"Font loading error: {e}")
    large_font = ImageFont.load_default()
    medium_font = ImageFont.load_default()
    small_font = ImageFont.load_default()
    status_font = ImageFont.load_default()
    st.warning("Using default font; sizes may be smaller than expected.")

# Input widgets
origin = st.text_input("Origin:", "Sabre")  # First field
color = st.text_input("Color:", "")  # Custom entry only

gauge_options = ["26ga", "24ga", "22ga", ".032", ".040", "Other"]
gauge = st.selectbox("Gauge:", gauge_options, index=1)  # Default "24ga"

if gauge == "Other":
    gauge = st.text_input("Enter custom gauge:", "")

status = st.selectbox("Status:", ["OPEN", "RESERVED"])
project = ""
if status == "RESERVED":
    project = st.text_input("Project Name:", "")

# Generate label function
if st.button("Generate Label"):
    width, height = 1650, 586  # Original size with 16px top margin
    # Background and text color based on status
    bg_color = "black" if status == "RESERVED" else "white"
    text_color = "white" if status == "RESERVED" else "black"
    box_color = "black" if bg_color == "white" else "white"  # Inverted for Origin box
    origin_text_color = "white" if box_color == "black" else "black"  # Opposite of box color
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # Text area with simulated bold
    color_text = color
    status_text = project if status == "RESERVED" and project else "RESERVED" if status == "RESERVED" else ""
    origin_text = origin.upper()  # Convert to all CAPS

    # Upper portion: Color title (235pt, bold)
    x, y = 40, 36  # x=40 (moved right 10px), y=36
    for offset_x in [-2, -1, 0, 1, 2]:
        for offset_y in [-2, -1, 0, 1, 2]:
            draw.text((x + offset_x, y + offset_y), color_text, font=large_font, fill=text_color)

    # Divider below color title, moved up 10px
    draw.line([(0, 251), (1650, 251)], fill=text_color, width=5)  # y=261 - 10 = 251

    # Lower portion: Gauge, Origin, Status (Reserved only)
    # Gauge (108pt, bold), moved up 5px, right 10px
    x, y = 60, 361  # x=50 + 10 = 60, y=366 - 5 = 361 (bottom at 469)
    gauge_width = draw.textlength(gauge, font=medium_font)
    gauge_height = 108  # Approximate height of 108pt font
    for offset_x in [-2, -1, 0, 1, 2]:
        for offset_y in [-2, -1, 0, 1, 2]:
            draw.text((x + offset_x, y + offset_y), gauge, font=medium_font, fill=text_color)
    # Draw shape around Gauge (20px padding)
    shape_x0 = x - 20
    shape_y0 = y - 20
    shape_x1 = x + gauge_width + 20
    shape_y1 = y + gauge_height + 20
    if gauge in [".032", ".040"] or gauge not in ["26ga", "24ga", "22ga"]:  # Circle for .032, .040, or custom
        center_x = (shape_x0 + shape_x1) / 2
        center_y = (shape_y0 + shape_y1) / 2
        radius = max(gauge_width, gauge_height) / 2 + 20
        draw.ellipse([center_x - radius, center_y - radius, center_x + radius, center_y + radius], outline=text_color, width=5)
    else:  # Square for 22ga, 24ga, 26ga
        draw.rectangle([shape_x0, shape_y0, shape_x1, shape_y1], outline=text_color, width=5)

    # Origin (55pt), right-justified
    origin_width = draw.textlength(origin_text, font=small_font)
    origin_x = 1650 - origin_width - 20  # x=1650 - text length - 20
    origin_y = 461  # Unchanged
    # Draw box around Origin (10px padding)
    box_x0 = origin_x - 10
    box_y0 = origin_y - 10
    box_x1 = origin_x + origin_width + 10
    box_y1 = origin_y + 55 + 10  # 55pt height + padding
    draw.rectangle([box_x0, box_y0, box_x1, box_y1], fill=box_color)
    draw.text((origin_x, origin_y), origin_text, font=small_font, fill=origin_text_color)

    # Status (140pt), centered, bottom-aligned (Reserved only)
    if status == "RESERVED":
        status_width = draw.textlength(status_text, font=status_font)
        status_x = (1650 - status_width) / 2  # Center horizontally
        status_y = 421  # y=421 (bottom at 561)
        draw.text((status_x, status_y), status_text, font=status_font, fill=text_color)

    # Display the image with centered styling
    with st.container():
        st.image(image, caption="Generated Label (No Swatch)", use_container_width=True)

    # Download button
    img_buffer = image.save("label_no_swatch.png", "PNG", quality=100)
    with open("label_no_swatch.png", "rb") as file:
        st.download_button(
            label="Download Label",
            data=file,
            file_name="label_no_swatch.png",
            mime="image/png"
        )

# Note about saving on Streamlit Cloud
st.info("Note: The 'Download Label' button allows you to save the label locally. Streamlit Cloud doesn't persist saved files.")
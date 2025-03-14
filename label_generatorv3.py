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
    large_font = ImageFont.truetype(font_path, 200)  # Color title, 225pt
    medium_font = ImageFont.truetype(font_path, 105)  # Material/gauge and status, 115pt
    small_font = ImageFont.truetype(font_path, 60)   # Origin, 70pt
    st.success(f"Fonts loaded successfully from {font_path}: 225pt, 115pt, and 70pt.")
except Exception as e:
    st.error(f"Font loading error: {e}")
    large_font = ImageFont.load_default()
    medium_font = ImageFont.load_default()
    small_font = ImageFont.load_default()
    st.warning("Using default font; sizes may be smaller than expected.")

# Input widgets (Origin as first field)
origin = st.text_input("Origin:", "Sabre")  # Moved to top

color_options = ["Snowdrift White", "Bone White", "Regal White", "Stone White", "Medium Bronze", "Almond",
                 "Sandstone", "Sierra Tan", "Dark Bronze", "Aged Copper", "Dove Gray", "Ash Gray", "Slate Gray",
                 "Charcoal Gray", "Patina Green", "Evergreen", "Slate Blue", "Regal Blue", "Banner Red",
                 "Colonial Red", "Terra Cotta", "Mansard Brown", "Matte Black", "Mill Finish", "Bright Silver",
                 "Pre-Weathered", "Copper Penny", "Other"]
color = st.selectbox("Color:", color_options)

custom_color = None
if color == "Other":
    custom_color = st.text_input("Enter custom color name:", "")

material_options = ["Aluminum", "Steel", "Copper", "Galvalume", "Other"]
material = st.selectbox("Material:", material_options)
if material == "Other":
    material = st.text_input("Enter custom material:", "")

gauge_options = ["24ga", ".032", "22ga", "Other"]
gauge = st.selectbox("Gauge:", gauge_options)
if gauge == "Other":
    gauge = st.text_input("Enter custom gauge:", "")

status = st.selectbox("Status:", ["Open", "Reserved"])
project = ""
if status == "Reserved":
    project = st.text_input("Project Name:", "")

# Generate label function
if st.button("Generate Label"):
    width, height = 1650, 586  # Original size with 16px top margin
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Text area with simulated bold, adjusted alignment
    color_text = custom_color if color == "Other" and custom_color else color
    material_text = f"{gauge} {material}".strip()
    status_text = project if status == "Reserved" and project else status

    # Color title (225pt, bolder), shifted right 15px
    x, y = 30, 36  # x=15 (shifted right), y=20 (shift) + 16 (margin) = 36
    for offset_x in [-2, -1, 0, 1, 2]:
        for offset_y in [-2, -1, 0, 1, 2]:
            draw.text((x + offset_x, y + offset_y), color_text, font=large_font, fill="black")
    draw.line([(0, 290), (1650, 290)], fill="black", width=8)  # Divider, moved up 10px to y=306
    # Material/gauge (115pt), shifted right 15px
    x, y = 30, 300  # x=15 (shifted right), y=300
    for offset_x in [-2, -1, 0, 1, 2]:
        for offset_y in [-2, -1, 0, 1, 2]:
            draw.text((x + offset_x, y + offset_y), material_text, font=medium_font, fill="black")
    # Status block (115pt), shifted right 15px for text
    status_y = 415  # y=415-550 (unchanged position)
    draw.rectangle([0, status_y, 1650, status_y + 135], fill=(95, 178, 34) if status == "Open" else (0, 99, 150))  # Height 135px
    # Status text, shifted right 15px
    draw.text((15, status_y + 25), status_text, font=medium_font, fill="white")  # x=15, y=440 for visibility
    # Origin text (70pt), right-aligned at bottom of status block (no shift)
    origin_x = 1640 - draw.textlength(origin, font=small_font)  # Right-align with 10px padding
    origin_y = status_y + 55  # y=475 (550 - 75 adjusted for visibility)
    draw.text((origin_x, origin_y), origin, font=small_font, fill="white")

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

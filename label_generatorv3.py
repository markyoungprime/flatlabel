import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO

st.set_page_config(page_title="Prime Roofing - Sheet Metal Label Generator", layout="centered")

st.title("🛠️ Prime Roofing Sheet Metal Label Generator")
st.markdown("**No Swatch Version** — Perfect for quick labels on coils, panels, or fab pieces.")

# ====================== FONT HANDLING (Cross-platform) ======================
def get_font(size):
    # Try common system fonts first
    font_candidates = [
        "/System/Library/Fonts/Helvetica.ttc",           # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
        "C:\\Windows\\Fonts\\Arial.ttf",                 # Windows
        "C:\\Windows\\Fonts\\Helvetica.ttf",
    ]
    
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    
    st.warning("Custom font not found. Using default font (labels will look slightly different).")
    return ImageFont.load_default()

large_font = get_font(235)
medium_font = get_font(108)
small_font = get_font(55)
status_font = get_font(140)

# ====================== INPUTS ======================
col1, col2 = st.columns([2, 1])

with col1:
    origin = st.text_input("Origin:", "Sabre", help="Usually 'Sabre' or your shop name")
    color = st.text_input("Color:", "", placeholder="e.g. Matte Black, Natural Zinc")

gauge_options = ["26ga", "24ga", "22ga", ".032", ".040", "Other"]
gauge = st.selectbox("Gauge:", gauge_options, index=1)

if gauge == "Other":
    gauge = st.text_input("Enter custom gauge:", "")

status = st.selectbox("Status:", ["OPEN", "RESERVED"])

project = ""
if status == "RESERVED":
    project = st.text_input("Project Name:", "")

# ====================== GENERATE LABEL ======================
if st.button("🚀 Generate Label", type="primary", use_container_width=True):
    width, height = 1725, 586  # 5.75" x 1.95" at 300 DPI

    bg_color = "black" if status == "RESERVED" else "white"
    text_color = "white" if status == "RESERVED" else "black"
    box_color = "black" if bg_color == "white" else "white"
    origin_text_color = "white" if box_color == "black" else "black"

    image = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)

    color_text = color.strip().upper() if color.strip() else "NO COLOR"
    status_text = project.strip().upper() if status == "RESERVED" and project.strip() else "RESERVED"
    origin_text = origin.strip().upper()

    # === Color Title (large, simulated bold) ===
    x, y = 40, 36
    for dx in [-2, -1, 0, 1, 2]:
        for dy in [-2, -1, 0, 1, 2]:
            draw.text((x + dx, y + dy), color_text, font=large_font, fill=text_color)

    # Divider
    draw.line([(0, 251), (1725, 251)], fill=text_color, width=5)

    # === Gauge with shape ===
    gauge_x, gauge_y = 60, 361
    gauge_width = draw.textlength(gauge, font=medium_font)
    
    # Simulated bold for gauge
    for dx in [-2, -1, 0, 1, 2]:
        for dy in [-2, -1, 0, 1, 2]:
            draw.text((gauge_x + dx, gauge_y + dy), gauge, font=medium_font, fill=text_color)

    # Draw shape around gauge
    padding = 20
    if gauge in [".032", ".040"] or gauge not in ["26ga", "24ga", "22ga"]:
        # Circle for decimals / custom
        cx = gauge_x + gauge_width / 2
        cy = gauge_y + 54
        radius = max(gauge_width, 108) / 2 + padding + 10
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], 
                     outline=text_color, width=5)
    else:
        # Square/rectangle for standard gauges
        side = max(gauge_width, 108) + padding * 2
        cx = gauge_x + gauge_width / 2
        cy = gauge_y + 54
        draw.rectangle([cx - side/2, cy - side/2, cx + side/2, cy + side/2], 
                       outline=text_color, width=5)

    # === Origin Box (right aligned) ===
    origin_width = draw.textlength(origin_text, font=small_font)
    origin_x = 1725 - origin_width - 30
    origin_y = 461

    box_x0 = origin_x - 12
    box_y0 = origin_y - 12
    box_x1 = origin_x + origin_width + 12
    box_y1 = origin_y + 67

    draw.rectangle([box_x0, box_y0, box_x1, box_y1], fill=box_color)
    draw.text((origin_x, origin_y), origin_text, font=small_font, fill=origin_text_color)

    # === RESERVED Status (centered, only if RESERVED) ===
    if status == "RESERVED":
        status_width = draw.textlength(status_text, font=status_font)
        status_x = (1725 - status_width) / 2
        status_y = 411
        draw.text((status_x, status_y), status_text, font=status_font, fill=text_color)

    # Display in app
    st.image(image, caption="✅ Generated Label — Ready for printing or laser engraving", 
             use_container_width=True)

    # ====================== DOWNLOAD ======================
    buf = BytesIO()
    image.save(buf, format="PNG", quality=100)
    buf.seek(0)

    st.download_button(
        label="⬇️ Download Label as PNG",
        data=buf,
        file_name=f"PrimeRoofing_Label_{color_text.replace(' ', '_')}_{gauge}.png",
        mime="image/png",
        use_container_width=True
    )

st.caption("Prime Roofing • Jacksonville, FL • Custom Sheet Metal Fabrication Since 2010")
st.info("💡 Tip: Print these on weatherproof vinyl or use your ShopSabre FibreLaser to etch directly onto metal tags.")

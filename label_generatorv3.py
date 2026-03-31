import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Prime Roofing - Sheet Metal Label Generator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🛠️ Prime Roofing Sheet Metal Label Generator")
st.markdown("**No Swatch Version** — Fast professional labels for your ShopSabre FibreLaser, roll formers, and custom metal pieces.")

# ====================== FONT HANDLING (Cross-platform) ======================
def get_font(size):
    font_candidates = [
        "/System/Library/Fonts/Helvetica.ttc",           # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
        "C:\\Windows\\Fonts\\Arial.ttf",                 # Windows
    ]
    
    for path in font_candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    st.warning("Custom font not found — using default font.")
    return ImageFont.load_default()

# Pre-load base fonts (we'll scale them later)
large_font = get_font(235)
medium_font = get_font(108)
small_font = get_font(55)
status_font = get_font(140)

# ====================== CLEAR FORM FUNCTION ======================
def clear_form():
    st.session_state.origin = "Sabre"
    st.session_state.color = ""
    st.session_state.gauge = "24ga"
    st.session_state.status = "OPEN"
    st.session_state.project = ""
    st.rerun()

# ====================== INPUTS ======================
col1, col2 = st.columns([3, 1])

with col1:
    origin = st.text_input("Origin:", value="Sabre", key="origin", help="Usually 'Sabre' or shop name")
    color = st.text_input("Color:", value="", key="color", placeholder="e.g. Matte Black, Galvalume, ZAM")

gauge_options = ["26ga", "24ga", "22ga", ".032", ".040", "Other"]
gauge = st.selectbox("Gauge:", gauge_options, index=1, key="gauge")

if gauge == "Other":
    gauge = st.text_input("Enter custom gauge:", key="custom_gauge")

status = st.selectbox("Status:", ["OPEN", "RESERVED"], key="status")

project = ""
if status == "RESERVED":
    project = st.text_input("Project Name:", key="project")

# Buttons side-by-side
col_clear, col_generate = st.columns(2)

with col_clear:
    if st.button("🗑️ Clear Form", use_container_width=True):
        clear_form()

with col_generate:
    if st.button("🚀 Generate Label", type="primary", use_container_width=True):

        # ====================== GENERATE LABEL (BIGGER FOR CLOUD) ======================
        scale = 2  # 2x resolution - perfect balance for display + print quality
        width, height = 1725 * scale, 586 * scale

        bg_color = "black" if status == "RESERVED" else "white"
        text_color = "white" if status == "RESERVED" else "black"
        box_color = "black" if bg_color == "white" else "white"
        origin_text_color = "white" if box_color == "black" else "black"

        image = Image.new("RGB", (width, height), color=bg_color)
        draw = ImageDraw.Draw(image)

        color_text = color.strip().upper() if color.strip() else "NO COLOR"
        status_text = project.strip().upper() if status == "RESERVED" and project.strip() else "RESERVED"
        origin_text = origin.strip().upper()

        # Scale fonts
        large_font_scaled = get_font(235 * scale)
        medium_font_scaled = get_font(108 * scale)
        small_font_scaled = get_font(55 * scale)
        status_font_scaled = get_font(140 * scale)

        # === Color Title (large, simulated bold) ===
        x, y = 40 * scale, 36 * scale
        for dx in [-3, -2, -1, 0, 1, 2, 3]:
            for dy in [-3, -2, -1, 0, 1, 2, 3]:
                draw.text((x + dx, y + dy), color_text, font=large_font_scaled, fill=text_color)

        # Divider
        draw.line([(0, 251 * scale), (width, 251 * scale)], fill=text_color, width=8 * scale)

        # === Gauge with shape ===
        gauge_x, gauge_y = 60 * scale, 361 * scale
        gauge_width = draw.textlength(gauge, font=medium_font_scaled)

        for dx in [-3, -2, -1, 0, 1, 2, 3]:
            for dy in [-3, -2, -1, 0, 1, 2, 3]:
                draw.text((gauge_x + dx, gauge_y + dy), gauge, font=medium_font_scaled, fill=text_color)

        # Draw shape around gauge
        padding = 20 * scale
        if gauge in [".032", ".040"] or gauge not in ["26ga", "24ga", "22ga"]:
            # Circle for decimals / custom
            cx = gauge_x + gauge_width / 2
            cy = gauge_y + 54 * scale
            radius = max(gauge_width, 108 * scale) / 2 + padding + 10 * scale
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], 
                         outline=text_color, width=8 * scale)
        else:
            # Square for standard gauges
            side = max(gauge_width, 108 * scale) + padding * 2
            cx = gauge_x + gauge_width / 2
            cy = gauge_y + 54 * scale
            draw.rectangle([cx - side/2, cy - side/2, cx + side/2, cy + side/2], 
                           outline=text_color, width=8 * scale)

        # === Origin Box (right aligned) ===
        origin_width = draw.textlength(origin_text, font=small_font_scaled)
        origin_x = width - origin_width - 30 * scale
        origin_y = 461 * scale

        box_x0 = origin_x - 12 * scale
        box_y0 = origin_y - 12 * scale
        box_x1 = origin_x + origin_width + 12 * scale
        box_y1 = origin_y + 67 * scale

        draw.rectangle([box_x0, box_y0, box_x1, box_y1], fill=box_color)
        draw.text((origin_x, origin_y), origin_text, font=small_font_scaled, fill=origin_text_color)

        # === RESERVED Status (centered) ===
        if status == "RESERVED":
            status_width = draw.textlength(status_text, font=status_font_scaled)
            status_x = (width - status_width) / 2
            status_y = 411 * scale
            draw.text((status_x, status_y), status_text, font=status_font_scaled, fill=text_color)

        # Display the label (now large on cloud)
        st.image(image, 
                 caption="✅ Generated Label — Ready for printing or laser engraving on your ShopSabre FibreLaser",
                 use_container_width=True, 
                 output_format="PNG")

        # Download button
        buf = BytesIO()
        image.save(buf, format="PNG", quality=100)
        buf.seek(0)

        st.download_button(
            label="⬇️ Download High-Res Label PNG",
            data=buf,
            file_name=f"PrimeRoofing_Label_{color_text.replace(' ', '_')}_{gauge}.png",
            mime="image/png",
            use_container_width=True
        )

# Footer
st.caption("Prime Roofing • Jacksonville, FL • Custom Metal Roofing & Sheet Metal Fabrication Since 2010")
st.info("💡 Use **Clear Form** between labels. Print on weatherproof vinyl or laser etch directly.")

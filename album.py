import streamlit as st
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageFont
from groq import Groq
import os

# --- 1. CONFIGURATION ---
CANVAS_WIDTH = 10800  
CANVAS_HEIGHT = 3600  

st.set_page_config(page_title="Black Rockers Visuals AI", layout="wide")

# --- 2. GROQ SETUP ---
# Ithe tumchi API Key taka
API_KEY = "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" 
client = Groq(api_key=API_KEY)

# Session State for Pagination
if 'page_num' not in st.session_state:
    st.session_state.page_num = 1

# --- 3. UI DESIGN ---
st.title(f"🎬 Black Rockers Visuals: Spread {st.session_state.page_num}")

# Sidebar Navigation
st.sidebar.header("Navigation & Settings")
col_nav1, col_nav2 = st.sidebar.columns(2)
if col_nav1.button("⬅️ Previous"):
    if st.session_state.page_num > 1:
        st.session_state.page_num -= 1
        st.rerun()
if col_nav2.button("Next ➡️"):
    st.session_state.page_num += 1
    st.rerun()

st.sidebar.markdown("---")
add_text = st.sidebar.checkbox("Ya page var Typography pahije?")
title_text = st.sidebar.text_input("Title", "The Wedding Story")

uploaded_files = st.file_uploader(f"Upload Photos for Spread {st.session_state.page_num}", 
                                  accept_multiple_files=True, 
                                  type=['jpg', 'png', 'jpeg'], 
                                  key=f"uploader_{st.session_state.page_num}")

# --- 4. ENGINE FUNCTIONS ---
def get_ai_layout_suggestion(num_images):
    """Groq AI कडून लेआउट बद्दल सूचना मिळवा"""
    try:
        prompt = f"I have {num_images} wedding photos. Suggest a professional album layout style (Modern, Cinematic, or Magazine) and a short creative title for this spread."
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except:
        return "AI Suggestion unavailable. Please select manually."

def apply_typography(canvas, text):
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arial.ttf", 350)
    except:
        font = ImageFont.load_default()
    w, h = draw.textbbox((0, 0), text, font=font)[2:]
    draw.text(((CANVAS_WIDTH - w) / 2, CANVAS_HEIGHT - 600), text, fill=(50, 50, 50), font=font)

def create_layout(images, style_type):
    canvas = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), (255, 255, 255))
    margin, gap = 200, 120
    
    if not images: return canvas

    if style_type == "Modern":
        hero = ImageOps.autocontrast(images[0]).copy()
        hero.thumbnail((5000, 3200), Image.Resampling.LANCZOS)
        canvas.paste(hero, (margin, margin))
        if len(images) > 1:
            s1 = ImageOps.autocontrast(images[1]).copy()
            s1.thumbnail((4800, 1500), Image.Resampling.LANCZOS)
            canvas.paste(s1, (5600, margin))
    
    elif style_type == "Cinematic":
        bg = images[0].resize((CANVAS_WIDTH, CANVAS_HEIGHT)).filter(ImageFilter.GaussianBlur(40))
        canvas.paste(bg, (0,0))
        for i, img in enumerate(images[:3]):
            temp = ImageOps.autocontrast(img).copy()
            temp.thumbnail((3000, 2800), Image.Resampling.LANCZOS)
            canvas.paste(temp, (800 + (i * 3200), 400))
            
    if add_text:
        apply_typography(canvas, title_text)
    return canvas

# --- 5. EXECUTION ---
if uploaded_files:
    imgs = [Image.open(f) for f in uploaded_files[:5]]
    
    # Groq AI Suggestion Box
    with st.expander("🤖 Groq AI Design Suggestion"):
        suggestion = get_ai_layout_suggestion(len(imgs))
        st.write(suggestion)

    st.subheader("Select Your Final Layout")
    c1, c2 = st.columns(2)
    
    out1 = create_layout(imgs, "Modern")
    out2 = create_layout(imgs, "Cinematic")
    
    with c1: 
        st.image(out1.resize((1200, 400)), caption="Option 1: Modern")
        if st.button(f"Save Spread {st.session_state.page_num} (Modern)"):
            out1.save(f"Spread_{st.session_state.page_num}_Modern.jpg", quality=100)
            st.success("Modern Layout Saved!")

    with c2: 
        st.image(out2.resize((1200, 400)), caption="Option 2: Cinematic")
        if st.button(f"Save Spread {st.session_state.page_num} (Cinematic)"):
            out2.save(f"Spread_{st.session_state.page_num}_Cinematic.jpg", quality=100)
            st.success("Cinematic Layout Saved!")

st.sidebar.info(f"Current Page: {st.session_state.page_num}")

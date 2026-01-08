from PIL import Image, ImageDraw, ImageOps, ImageFont
import os
import math

def process_logo(input_path, output_path, watermark_text="山海寻梦"):
    # 1. Load Image
    img = Image.open(input_path).convert("RGBA")
    
    # Square Crop (Focus on the person)
    w, h = img.size
    # The person is on the left side. Let's calculate a square that covers the left part.
    # Height is the limiting factor usually for these types of portraits.
    crop_size = min(w, h)
    
    # Shift towards the left to capture the person
    # Original image: person on left, sea on right. 
    # Let's take the crop from x=0 to x=crop_size
    left = 0
    top = 0
    right = crop_size
    bottom = crop_size
    
    img = img.crop((left, top, right, bottom))
    
    # NEW: Scale person down so they are not touching the 500x500 edges
    content_size = 420
    img = img.resize((content_size, content_size), Image.LANCZOS)
    
    # Create 500x500 canvas and center the person
    canvas = Image.new("RGBA", (500, 500), (0, 0, 0, 0))
    offset = (500 - content_size) // 2
    canvas.paste(img, (offset, offset))
    img = canvas
    
    # 2. Wave Mask Generation
    size = 500
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    center = size / 2
    # Base radius: make it large enough to encompass the scaled character
    r_base = size / 2 * 0.94
    
    points = []
    num_points = 360
    for i in range(num_points):
        theta = math.radians(i)
        # Irregular wave logic
        dist_from_top = abs(theta - 1.5 * math.pi)
        if dist_from_top > math.pi: 
             dist_from_top = abs(theta + 0.5 * math.pi)

        if dist_from_top < 0.6 * math.pi:
            wave_amp = 3 # Very stable at top for the hat
        else:
            wave_amp = 10
            
        wave = (math.sin(theta * 8) * wave_amp + 
                math.sin(theta * 15) * 4)
        
        r = r_base + wave
        x = center + r * math.cos(theta)
        y = center + r * math.sin(theta)
        points.append((x, y))
    
    draw.polygon(points, fill=255)
    
    # Apply Mask
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0), mask)
    
    # 3. Add Watermark (Gold Engraved Cursive)
    draw = ImageDraw.Draw(output)
    
    font_paths = [
        "C:/Windows/Fonts/STXINGKA.TTF", # 华文行楷
        "C:/Windows/Fonts/SIMLI.TTF",     # 隶书
        "C:/Windows/Fonts/STLITI.TTF",    # 华文隶书
        "C:/Windows/Fonts/msyh.ttc"       # MS YaHei
    ]
    font = None
    for fp in font_paths:
        try:
            font = ImageFont.truetype(fp, 70) # Slightly smaller font
            break
        except:
            continue
    if not font: font = ImageFont.load_default()
    
    # Colors
    GOLD_MAIN = (212, 175, 55, 255)   # Metallic Gold
    GOLD_DARK = (101, 67, 33, 220)    # Deep shadow
    GOLD_LIGHT = (255, 235, 120, 180) # Highlight
    
    # Calculate text position - MOVE UP
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (size - tw) / 2
    ty = 365 # Moved up from 390
    
    # Engraved Effect
    # Dark shadow
    draw.text((tx-3, ty-3), watermark_text, font=font, fill=GOLD_DARK)
    # Light highlight
    draw.text((tx+1, ty+1), watermark_text, font=font, fill=GOLD_LIGHT)
    # Main text
    draw.text((tx, ty), watermark_text, font=font, fill=GOLD_MAIN)
    
    # 4. Save
    output.save(output_path)
    print(f"Processed logo (WAVE SHAPE) saved to: {output_path}")

if __name__ == "__main__":
    # Use the original uploaded image (the one with the person) 
    # not the previously masked one if possible, but I'll use raw_path
    raw_path = r"C:\Users\wgl\.gemini\antigravity\brain\8a90a23c-ca44-414d-b129-b55025e55404\uploaded_image_1767871514515.png"
    out_dir = r"C:\Users\wgl\gtht\assets"
    if not os.path.exists(out_dir): os.makedirs(out_dir)
    process_logo(raw_path, os.path.join(out_dir, "logo_circle.png"))

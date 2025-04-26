from PIL import Image, ImageDraw, ImageFont
import os
import io
import base64
from datetime import datetime

# Define constants for flyer design
TEAL_COLOR = (0, 128, 128)
WHITE_COLOR = (255, 255, 255)
GRAY_COLOR = (100, 100, 100)
BLACK_COLOR = (0, 0, 0)

# Get the directory of the current script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Try to load fonts - fallback to default if custom fonts aren't available
try:
    # Attempt to load custom fonts if available
    TITLE_FONT = ImageFont.truetype(os.path.join(CURRENT_DIR, "fonts", "Montserrat-Bold.ttf"), 36)
    SUBTITLE_FONT = ImageFont.truetype(os.path.join(CURRENT_DIR, "fonts", "Montserrat-SemiBold.ttf"), 28)
    BODY_FONT = ImageFont.truetype(os.path.join(CURRENT_DIR, "fonts", "Montserrat-Regular.ttf"), 22)
    PRICE_FONT = ImageFont.truetype(os.path.join(CURRENT_DIR, "fonts", "Montserrat-Bold.ttf"), 48)
    FOOTER_FONT = ImageFont.truetype(os.path.join(CURRENT_DIR, "fonts", "Montserrat-Regular.ttf"), 18)
except Exception:
    # Fallback to default font
    TITLE_FONT = ImageFont.load_default()
    SUBTITLE_FONT = ImageFont.load_default()
    BODY_FONT = ImageFont.load_default()
    PRICE_FONT = ImageFont.load_default()
    FOOTER_FONT = ImageFont.load_default()

def create_flyer(image, title, category, description, price):
    """
    Create a flyer image with the provided information
    
    Args:
        image: PIL Image object of the item
        title: Title text for the item
        category: Category of the item
        description: Description text
        price: Price in INR (without ₹ symbol)
        
    Returns:
        PIL Image object of the generated flyer
    """
    # Create a new image with white background
    flyer_width = 1200
    flyer_height = 1600
    flyer = Image.new('RGB', (flyer_width, flyer_height), WHITE_COLOR)
    draw = ImageDraw.Draw(flyer)
    
    # Draw header with teal background
    draw.rectangle([(0, 0), (flyer_width, 120)], fill=TEAL_COLOR)
    
    # Draw app name
    app_name = "Snap & Sell"
    try:
        w, h = draw.textsize(app_name, font=TITLE_FONT)
    except:
        # For newer PIL versions
        w, h = TITLE_FONT.getbbox(app_name)[2:4]
    
    draw.text(
        ((flyer_width - w) // 2, 40), 
        app_name, 
        fill=WHITE_COLOR, 
        font=TITLE_FONT
    )
    
    # Resize and center the main image
    target_height = 600
    img_width, img_height = image.size
    new_width = int(img_width * (target_height / img_height))
    
    if new_width > flyer_width - 100:
        new_width = flyer_width - 100
        target_height = int(img_height * (new_width / img_width))
    
    resized_img = image.resize((new_width, target_height), Image.LANCZOS)
    
    # Calculate position to center the image
    img_pos_x = (flyer_width - new_width) // 2
    img_pos_y = 180
    
    # Create a border around the image
    draw.rectangle(
        [(img_pos_x-10, img_pos_y-10), 
         (img_pos_x+new_width+10, img_pos_y+target_height+10)], 
        outline=TEAL_COLOR, 
        width=5
    )
    
    # Paste the image
    flyer.paste(resized_img, (img_pos_x, img_pos_y))
    
    # Draw title
    title_y = img_pos_y + target_height + 50
    draw_wrapped_text(draw, title, 60, title_y, flyer_width-120, SUBTITLE_FONT, BLACK_COLOR)
    
    # Draw category
    category_y = title_y + 80
    draw.text(
        (60, category_y), 
        f"Category: {category}", 
        fill=GRAY_COLOR, 
        font=BODY_FONT
    )
    
    # Draw description
    desc_y = category_y + 50
    draw_wrapped_text(draw, description, 60, desc_y, flyer_width-120, BODY_FONT, BLACK_COLOR)
    
    # Draw price box
    price_box_y = desc_y + 200
    draw.rectangle(
        [(flyer_width//2 - 150, price_box_y), 
         (flyer_width//2 + 150, price_box_y + 100)], 
        fill=TEAL_COLOR
    )
    
    # Format price with commas for thousands
    try:
        formatted_price = format_price(price)
    except:
        formatted_price = price
        
    # Draw price
    # Use 'Rs.' instead of ₹ symbol to avoid encoding issues
    price_text = f"Rs. {formatted_price}"
    try:
        w, h = draw.textsize(price_text, font=PRICE_FONT)
    except Exception as e:
        try:
            # For newer PIL versions
            w, h = PRICE_FONT.getbbox(price_text)[2:4]
        except Exception as e:
            print(f"Error getting text size: {e}")
            # Fallback to estimated size
            w, h = len(price_text) * 20, 50
        
    draw.text(
        ((flyer_width - w) // 2, price_box_y + 25), 
        price_text, 
        fill=WHITE_COLOR, 
        font=PRICE_FONT
    )
    
    # Draw footer
    footer_y = flyer_height - 60
    current_date = datetime.now().strftime("%d %b %Y")
    # Use a hyphen instead of bullet point to avoid encoding issues
    footer_text = f"Created with Snap & Sell - {current_date}"
    
    try:
        w, h = draw.textsize(footer_text, font=FOOTER_FONT)
    except:
        # For newer PIL versions
        w, h = FOOTER_FONT.getbbox(footer_text)[2:4]
        
    draw.text(
        ((flyer_width - w) // 2, footer_y), 
        footer_text, 
        fill=GRAY_COLOR, 
        font=FOOTER_FONT
    )
    
    return flyer

def draw_wrapped_text(draw, text, x, y, max_width, font, color):
    """Draw text wrapped to fit within max_width"""
    words = text.split()
    lines = []
    current_line = words[0]
    
    for word in words[1:]:
        try:
            # Check if adding this word exceeds max width
            test_line = current_line + " " + word
            w, h = draw.textsize(test_line, font=font)
        except:
            # For newer PIL versions
            test_line = current_line + " " + word
            w, h = font.getbbox(test_line)[2:4]
            
        if w <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    
    lines.append(current_line)
    
    # Draw each line
    line_height = font.getbbox("Ay")[3] * 1.5  # Approximate line height
    for i, line in enumerate(lines):
        draw.text((x, y + i * line_height), line, fill=color, font=font)
    
    return y + len(lines) * line_height

def format_price(price):
    """Format price with commas for thousands (Indian format)"""
    price = str(price).replace(',', '').replace('₹', '')
    price = int(float(price))
    
    # Indian number format (lakhs and crores)
    s = str(price)
    if len(s) <= 3:
        return s
    elif len(s) <= 5:
        return s[:-3] + ',' + s[-3:]
    else:
        return s[:-5] + ',' + s[-5:-3] + ',' + s[-3:]

def image_to_base64(img):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

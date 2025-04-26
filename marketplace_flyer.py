import os
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from datetime import datetime

# Define constants for flyer design
TEAL_COLOR = (0, 128, 128)
WHITE_COLOR = (255, 255, 255)
CREAM_COLOR = (252, 252, 245)
GRAY_COLOR = (100, 100, 100)
BLACK_COLOR = (0, 0, 0)
LIGHT_GRAY = (240, 240, 240)

# Get the directory of the current script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Try to load fonts - fallback to default if custom fonts aren't available
try:
    # Attempt to load custom fonts if available
    TITLE_FONT = ImageFont.truetype(os.path.join(CURRENT_DIR, "fonts", "Montserrat-Bold.ttf"), 48)
    SUBTITLE_FONT = ImageFont.truetype(os.path.join(CURRENT_DIR, "fonts", "Montserrat-SemiBold.ttf"), 24)
    BODY_FONT = ImageFont.truetype(os.path.join(CURRENT_DIR, "fonts", "Montserrat-Regular.ttf"), 22)
    PRICE_FONT = ImageFont.truetype(os.path.join(CURRENT_DIR, "fonts", "Montserrat-Bold.ttf"), 30)
    FOOTER_FONT = ImageFont.truetype(os.path.join(CURRENT_DIR, "fonts", "Montserrat-Regular.ttf"), 16)
except Exception:
    # Fallback to default font
    TITLE_FONT = ImageFont.load_default()
    SUBTITLE_FONT = ImageFont.load_default()
    BODY_FONT = ImageFont.load_default()
    PRICE_FONT = ImageFont.load_default()
    FOOTER_FONT = ImageFont.load_default()

def create_marketplace_flyer(image, title=None, features=None, price=None, location=None, contact_info=None, style="modern", custom_prompt=None):
    """
    Create a marketplace flyer image with the provided information
    
    Args:
        image: PIL Image object of the item
        title: Title text for the item (optional if custom_prompt is provided)
        features: List of feature bullet points (optional if custom_prompt is provided)
        price: Price in INR (without Rs. symbol) (optional if custom_prompt is provided)
        location: Location information (optional)
        contact_info: Contact information (optional)
        style: Style of the flyer (modern, minimal, colorful)
        custom_prompt: Custom prompt for flyer generation (optional)
        
    Returns:
        PIL Image object of the generated flyer
    """
    # Create a new image with cream background
    flyer_width = 800
    flyer_height = 1200
    flyer = Image.new('RGB', (flyer_width, flyer_height), CREAM_COLOR)
    draw = ImageDraw.Draw(flyer)
    
    # Draw title at the top
    if title is None:
        # Extract title from custom_prompt if available
        if custom_prompt and "Create a marketplace listing for:" in custom_prompt:
            title = custom_prompt.split("Create a marketplace listing for:")[1].split("\n")[0].strip()
        else:
            title = "ITEM FOR SALE"
    
    title = title.upper()
    try:
        w, h = draw.textsize(title, font=TITLE_FONT)
    except:
        # For newer PIL versions
        w, h = TITLE_FONT.getbbox(title)[2:4]
    
    draw.text(
        ((flyer_width - w) // 2, 40), 
        title, 
        fill=TEAL_COLOR, 
        font=TITLE_FONT
    )
    
    # Resize and center the main image
    target_height = 400
    img_width, img_height = image.size
    new_width = int(img_width * (target_height / img_height))
    
    if new_width > flyer_width - 80:
        new_width = flyer_width - 80
        target_height = int(img_height * (new_width / img_width))
    
    resized_img = image.resize((new_width, target_height), Image.LANCZOS)
    
    # Calculate position to center the image
    img_pos_x = (flyer_width - new_width) // 2
    img_pos_y = 120
    
    # Create a border around the image
    draw.rectangle(
        [(img_pos_x-5, img_pos_y-5), 
         (img_pos_x+new_width+5, img_pos_y+target_height+5)], 
        outline=TEAL_COLOR, 
        width=3
    )
    
    # Paste the image
    flyer.paste(resized_img, (img_pos_x, img_pos_y))
    
    # Draw bullet points for features
    bullet_y = img_pos_y + target_height + 60
    
    # Extract features from custom_prompt if available and features is None
    if features is None:
        if custom_prompt and "Features:" in custom_prompt:
            # Try to extract features from custom_prompt
            try:
                features_text = custom_prompt.split("Features:")[1].split("Price:")[0].strip()
                features = [f.strip().lstrip('-').strip() for f in features_text.split('\n') if f.strip()]
            except:
                features = ["Quality item in good condition"]
        else:
            features = ["Quality item in good condition"]
    
    # Ensure features is a list
    if not isinstance(features, list):
        features = [str(features)]
    
    for feature in features:
        # Use a simple dash instead of bullet point to avoid encoding issues
        feature_text = f"- {feature}"
        draw.text(
            (40, bullet_y), 
            feature_text, 
            fill=BLACK_COLOR, 
            font=BODY_FONT
        )
        bullet_y += 40
    
    # Draw price
    price_y = bullet_y + 40
    
    # Extract price from custom_prompt if available and price is None
    if price is None:
        if custom_prompt and "Price:" in custom_prompt:
            # Try to extract price from custom_prompt
            try:
                price_text = custom_prompt.split("Price:")[1].split("\n")[0].strip()
                # Extract just the digits
                price = ''.join(c for c in price_text if c.isdigit())
                if not price:
                    price = "1000"  # Default price
            except:
                price = "1000"  # Default price
        else:
            price = "1000"  # Default price
    
    price_text = f"Price: Rs. {price}"
    draw.text(
        (40, price_y), 
        price_text, 
        fill=TEAL_COLOR, 
        font=PRICE_FONT
    )
    
    # Draw location if provided
    # Extract location from custom_prompt if available and location is None
    if location is None and custom_prompt and "Location:" in custom_prompt:
        # Try to extract location from custom_prompt
        try:
            location_text = custom_prompt.split("Location:")[1].split("\n")[0].strip()
            if location_text:
                location = location_text
        except:
            pass
    
    if location:
        location_y = price_y + 60
        location_text = f"Location: {location}"
        draw.text(
            (40, location_y), 
            location_text, 
            fill=BLACK_COLOR, 
            font=BODY_FONT
        )
    
    # Draw contact info or call to action
    cta_y = flyer_height - 150
    if contact_info:
        cta_text = contact_info
    else:
        cta_text = "DM for details"
    
    # Draw the CTA text
    draw.text(
        (40, cta_y), 
        cta_text, 
        fill=BLACK_COLOR, 
        font=SUBTITLE_FONT
    )
    
    # Draw WhatsApp icon
    whatsapp_icon_size = 40
    icon_x = flyer_width - 80
    icon_y = cta_y - 5
    
    # Draw a circle for WhatsApp icon
    draw.ellipse(
        [(icon_x, icon_y), 
         (icon_x + whatsapp_icon_size, icon_y + whatsapp_icon_size)], 
        fill=(37, 211, 102)  # WhatsApp green
    )
    
    # Draw footer
    footer_y = flyer_height - 40
    footer_text = f"Created with Snap & Sell - {datetime.now().strftime('%d %b %Y')}"
    
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

def format_price(price):
    """Format price with commas for thousands (Indian format)"""
    price = str(price).replace(',', '').replace('Rs.', '').replace('₹', '')
    try:
        price = int(float(price))
        
        # Indian number format (lakhs and crores)
        s = str(price)
        if len(s) <= 3:
            return s
        elif len(s) <= 5:
            return s[:-3] + ',' + s[-3:]
        else:
            return s[:-5] + ',' + s[-5:-3] + ',' + s[-3:]
    except:
        return price

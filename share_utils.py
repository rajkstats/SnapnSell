import os
import base64
import pyshorteners
from io import BytesIO
from PIL import Image

def get_image_download_link(img, filename="flyer.png", text="Download Flyer"):
    """
    Generate a download link for a PIL Image
    
    Args:
        img: PIL Image
        filename: Name of the file to download
        text: Text to display on the download button
        
    Returns:
        HTML string with download link
    """
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{img_str}" download="{filename}">{text}</a>'
    return href

def get_whatsapp_share_link(img, title, price):
    """
    Generate a WhatsApp share link with the flyer image
    
    This is a simplified version that requires the user to manually 
    attach the image in WhatsApp after clicking the link.
    
    Args:
        img: PIL Image
        title: Title of the listing
        price: Price of the item
        
    Returns:
        WhatsApp share link with pre-filled message
    """
    # Create a message with title and price
    message = f"*{title}*\nPrice: Rs. {price}\n\n_Shared via Snap & Sell_"
    
    # URL encode the message
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    
    # Generate WhatsApp share link
    whatsapp_link = f"https://wa.me/?text={encoded_message}"
    
    return whatsapp_link

def create_short_url(url):
    """
    Create a shortened URL using TinyURL
    
    Args:
        url: URL to shorten
        
    Returns:
        Shortened URL
    """
    try:
        # Initialize the shortener
        s = pyshorteners.Shortener()
        
        # Shorten the URL
        short_url = s.tinyurl.short(url)
        
        return short_url
    except Exception as e:
        print(f"Error creating short URL: {e}")
        return url

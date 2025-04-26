"""
API wrapper for flyer generation functionality.
This module provides a simplified interface for generating marketplace flyers.
"""

import os
import base64
import requests
import io
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

# Import local modules
from marketplace_flyer import create_marketplace_flyer
from ai_utils import analyze_image

# Load environment variables
load_dotenv()

# Initialize OpenAI client
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    print("OpenAI client initialized for flyer generation")
except Exception as e:
    print(f"Error initializing OpenAI client for flyer generation: {e}")
    client = None

def generate_marketplace_flyer(image, custom_prompt=None, title=None, features=None, price=None, location=None, contact_info=None, style="modern", use_api=True):
    """
    Generate a marketplace flyer with the provided information.
    
    This function can either use the OpenAI image generation API or the local flyer generator.
    
    Args:
        image: PIL Image object of the item
        custom_prompt: Custom prompt for flyer generation (optional)
        title: Title text for the item (optional if custom_prompt is provided)
        features: List of feature bullet points (optional if custom_prompt is provided)
        price: Price in INR (without Rs. symbol) (optional if custom_prompt is provided)
        location: Location information (optional)
        contact_info: Contact information (optional)
        style: Style of the flyer (modern, minimal, colorful)
        use_api: Whether to use the OpenAI API for flyer generation (default: True)
        
    Returns:
        PIL Image object of the generated flyer
    """
    # If custom_prompt is not provided, we need title, features, and price
    if custom_prompt is None and (title is None or features is None or price is None):
        raise ValueError("Either custom_prompt or title, features, and price must be provided")
    
    # If API is not available or use_api is False, use the local flyer generator
    if not use_api or client is None:
        print("Using local flyer generator")
        return create_marketplace_flyer(
            image=image,
            title=title,
            features=features,
            price=price,
            location=location,
            contact_info=contact_info,
            style=style,
            custom_prompt=custom_prompt
        )
    
    # Use OpenAI API to generate the flyer
    print("Using OpenAI API for flyer generation")
    return generate_flyer_with_openai(image, custom_prompt)

def generate_flyer_with_openai(image, custom_prompt):
    """
    Generate a marketplace flyer using OpenAI's image generation API.
    
    Args:
        image: PIL Image object of the item
        custom_prompt: Custom prompt for flyer generation
        
    Returns:
        PIL Image object of the generated flyer
    """
    if client is None:
        raise ValueError("OpenAI client not initialized. Cannot generate flyer.")
    
    # Prepare the prompt
    if not custom_prompt:
        custom_prompt = "Create a flyer to sell this product in WhatsApp or Facebook Marketplace"
    else:
        # Ensure the prompt is focused on flyer generation
        if "flyer" not in custom_prompt.lower() and "marketplace" not in custom_prompt.lower():
            custom_prompt += "\n\nCreate a visually appealing marketplace flyer based on this information."
    
    print("Using prompt for flyer generation:")
    print(custom_prompt)
    
    # Convert image to PNG format in memory
    img_byte_arr = io.BytesIO()
    
    # If image is not RGB, convert it
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Save as PNG
    image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    image_bytes = img_byte_arr.getvalue()
    
    try:
        # Construct the multipart/form-data request
        files = {
            'image': ('image.png', image_bytes, 'image/png'),  # filename, file content, file type
        }
        data = {'prompt': custom_prompt, 'model': 'gpt-image-1'}
        
        # Make the request using requests library
        response = requests.post(
            "https://api.openai.com/v1/images/edits",
            headers={"Authorization": f"Bearer {client.api_key}"},
            files=files,
            data=data,
        )
        
        if response.status_code == 200:
            result = response.json()
            image_base64 = result['data'][0]['b64_json']
            image_bytes = base64.b64decode(image_base64)
            
            # Convert to PIL Image
            flyer_image = Image.open(io.BytesIO(image_bytes))
            return flyer_image
        else:
            print(f"Error from OpenAI API: {response.status_code} - {response.text}")
            raise ValueError(f"OpenAI API error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"Error generating flyer with OpenAI: {e}")
        import traceback
        traceback.print_exc()
        # Fall back to local flyer generation
        print("Falling back to local flyer generation")
        return create_marketplace_flyer(
            image=image,
            custom_prompt=custom_prompt
        )

def build_custom_prompt(title, features, price, location=None, category=None, condition=None, brand=None, age=None, additional_info=None):
    """
    Build a custom prompt for flyer generation based on the item details.
    
    Args:
        title: Title of the item listing
        features: List of feature bullet points
        price: Price in INR
        location: Location information (optional)
        category: Category of the item (optional)
        condition: Condition of the item (optional)
        brand: Brand of the item (optional)
        age: Age or year of the item (optional)
        additional_info: Any additional information about the item (optional)
        
    Returns:
        A formatted prompt string for flyer generation
    """
    # Start with the title
    prompt = f"Create a marketplace listing for: {title}"
    
    # Add category if available
    if category:
        prompt += f"\nCategory: {category}"
    
    # Add features
    if features and len(features) > 0:
        prompt += "\nFeatures:"
        for feature in features:
            prompt += f"\n- {feature}"
    
    # Add price
    prompt += f"\nPrice: ₹{price}"
    
    # Add location if available
    if location:
        prompt += f"\nLocation: {location}"
    
    # Add condition if available
    if condition:
        prompt += f"\nCondition: {condition}"
    
    # Add brand if available
    if brand:
        prompt += f"\nBrand: {brand}"
    
    # Add age if available
    if age:
        prompt += f"\nAge: {age}"
    
    # Add additional info if available
    if additional_info:
        prompt += f"\nAdditional Information: {additional_info}"
    
    # Add final instruction
    prompt += "\n\nPlease create a visually appealing marketplace listing flyer based on the above information."
    
    return prompt

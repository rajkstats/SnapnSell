import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Warning: OpenAI API key not found in environment variables")

# Initialize OpenAI client
try:
    client = OpenAI(api_key=api_key)
    print("OpenAI client initialized successfully for image generation")
except Exception as e:
    print(f"Error initializing OpenAI client for image generation: {e}")
    client = None

def generate_product_image(description, category=None, style="photorealistic"):
    """
    Generate a product image using OpenAI's GPT-Image-1 model
    
    Args:
        description: Description of the product
        category: Category of the product (optional)
        style: Style of the image (default: photorealistic)
        
    Returns:
        PIL Image object of the generated image
    """
    if client is None:
        print("OpenAI client not initialized. Cannot generate image.")
        return None
    
    # Create a prompt for the image generation
    if category:
        prompt = f"A {style} image of a {category}: {description}. The image should be clean, well-lit, and on a plain background, suitable for a marketplace listing."
    else:
        prompt = f"A {style} image of: {description}. The image should be clean, well-lit, and on a plain background, suitable for a marketplace listing."
    
    try:
        # Generate the image
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            n=1,  # Number of images to generate
            size="1024x1024",  # Image size
            response_format="b64_json"  # Return base64 encoded image
        )
        
        # Get the base64 encoded image
        image_base64 = result.data[0].b64_json
        
        # Convert base64 to PIL Image
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_bytes))
        
        return image
    
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def enhance_product_image(original_image, description=None, category=None):
    """
    Enhance a product image using OpenAI's GPT-Image-1 model
    
    Args:
        original_image: PIL Image object of the original image
        description: Description of the product (optional)
        category: Category of the product (optional)
        
    Returns:
        PIL Image object of the enhanced image
    """
    if client is None:
        print("OpenAI client not initialized. Cannot enhance image.")
        return original_image
    
    # Convert PIL image to base64
    buffered = BytesIO()
    original_image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Create a prompt for the image enhancement
    if description and category:
        prompt = f"Enhance this product image of a {category}: {description}. Make it look professional, well-lit, and suitable for a marketplace listing."
    elif description:
        prompt = f"Enhance this product image: {description}. Make it look professional, well-lit, and suitable for a marketplace listing."
    else:
        prompt = "Enhance this product image. Make it look professional, well-lit, and suitable for a marketplace listing."
    
    try:
        # Generate the enhanced image
        result = client.images.edit(
            model="gpt-image-1",
            image=img_str,
            prompt=prompt,
            n=1,  # Number of images to generate
            size="1024x1024",  # Image size
            response_format="b64_json"  # Return base64 encoded image
        )
        
        # Get the base64 encoded image
        image_base64 = result.data[0].b64_json
        
        # Convert base64 to PIL Image
        image_bytes = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_bytes))
        
        return image
    
    except Exception as e:
        print(f"Error enhancing image: {e}")
        return original_image  # Return original image if enhancement fails

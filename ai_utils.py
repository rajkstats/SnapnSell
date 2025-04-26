import os
import base64
from io import BytesIO
import openai
from dotenv import load_dotenv
from PIL import Image
import numpy as np

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'), override=True)

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Warning: OpenAI API key not found in environment variables")
else:
    # Print the API key for debugging (first 4 and last 4 characters)
    if len(api_key) > 8:
        print(f"API Key loaded: {api_key[:4]}...{api_key[-4:]}")
    else:
        print(f"API Key loaded but seems invalid: {api_key}")

# Initialize OpenAI client
try:
    client = openai.OpenAI(api_key=api_key)
    print("OpenAI client initialized successfully")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    client = None

def encode_image(image_path):
    """Convert image to base64 encoding for API requests"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def encode_pil_image(pil_image):
    """Convert PIL image to base64 encoding for API requests"""
    buffered = BytesIO()
    
    # Convert RGBA to RGB if needed
    if pil_image.mode == 'RGBA':
        # Create a white background image
        background = Image.new('RGB', pil_image.size, (255, 255, 255))
        # Paste the image on the background
        background.paste(pil_image, mask=pil_image.split()[3])  # 3 is the alpha channel
        pil_image = background
    elif pil_image.mode != 'RGB':
        # Convert any other mode to RGB
        pil_image = pil_image.convert('RGB')
        
    # Save as JPEG
    pil_image.save(buffered, format="JPEG", quality=90)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def extract_field(text, field_name):
    """Extract a field from the analysis text"""
    lines = text.split('\n')
    for line in lines:
        if line.strip().startswith(field_name):
            return line.split(field_name, 1)[1].strip().strip(':').strip()
    return ""

def analyze_image(image, use_fallback=False):
    """Analyze image using OpenAI Vision API to detect category, generate title, features, and suggest price"""
    # Check if we should use fallback mode
    if use_fallback or client is None:
        print("Using fallback analysis without API call.")
        return get_fallback_analysis()
    
    # Print the full API key for debugging
    print(f"Full API Key being used: {api_key}")
    
    # Convert PIL image to base64
    if isinstance(image, str):
        # If image is a file path
        base64_image = encode_image(image)
    else:
        # If image is a PIL Image
        base64_image = encode_pil_image(image)
    
    # Create prompt for OpenAI
    prompt = """
    You are an expert in second-hand item listing for Indian marketplace. Analyze this image and provide:
    1. Category: What type of item is this? (e.g., furniture, electronics, clothing)
    2. Title: Create a catchy, concise title (max 10 words)
    3. Features: List 3-5 key features as bullet points (each under 10 words)
    4. Price: Estimate a fair price in INR based on visible condition and category
    5. Location: If you can identify any location information in the image or metadata, mention it. Otherwise, leave blank.
    
    Format your response exactly like this:
    Category: [category]
    Title: [title]
    Features:
    - [feature 1]
    - [feature 2]
    - [feature 3]
    Price: [price in INR without symbol]
    Location: [location if visible, otherwise leave blank]
    """
    
    try:
        # Use only gpt-4o-mini for image analysis
        print("Using GPT-4o-mini for image analysis...")
        print(f"Image type: {type(image)}")
        print(f"Image mode: {image.mode if hasattr(image, 'mode') else 'Unknown'}") 
        print(f"Image size: {image.size if hasattr(image, 'size') else 'Unknown'}") 
        print(f"Base64 image length: {len(base64_image) if base64_image else 'Unknown'}")
        try:
            print("Sending request to OpenAI API...")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            print("Received response from OpenAI API")
            analysis_text = response.choices[0].message.content
            print(f"Analysis text received: {analysis_text[:100]}...")
        except Exception as api_error:
            print(f"OpenAI API error: {api_error}")
            import traceback
            print("API call traceback:")
            traceback.print_exc()
            raise
    
        # Parse the analysis text
        print("Parsing analysis text...")
        category = extract_field(analysis_text, "Category:")
        print(f"Extracted category: {category}")
        title = extract_field(analysis_text, "Title:")
        print(f"Extracted title: {title}")
        
        # Check if we have features or description
        print("Extracting features...")
        if "Features:" in analysis_text:
            print("Features section found in analysis")
            features_text = analysis_text.split("Features:")[1].split("Price:")[0].strip()
            # Extract bullet points
            features = [f.strip().lstrip('-').strip() for f in features_text.split('\n') if f.strip()]
            print(f"Extracted features: {features}")
        else:
            print("No Features section found, looking for Description")
            # Fall back to description if no features
            description = extract_field(analysis_text, "Description:")
            # Create features from description
            features = [description[:40] + "..."] if description else ["Quality item in good condition"]
            print(f"Created features from description: {features}")
        
        print("Extracting price...")
        price = extract_field(analysis_text, "Price:")
        print(f"Raw price: {price}")
        # Clean up price (remove INR, commas, etc.)
        price = ''.join(c for c in price if c.isdigit())
        if not price:
            print("No valid price found, using default")
            price = "1000"  # Default price
        print(f"Final price: {price}")
            
        # Extract location if available
        location = ""
        if "Location:" in analysis_text:
            location = extract_field(analysis_text, "Location:")
            
        return {
            'category': category,
            'title': title,
            'features': features,
            'price': price,
            'location': location
        }
    except Exception as e:
        print(f"Error in AI analysis: {e}")
        return get_fallback_analysis()

def get_fallback_analysis():
    """Return fallback analysis when API calls fail"""
    return {
        'category': 'General Item',
        'title': 'Quality Second-hand Item',
        'features': [
            'Good condition', 
            'Well maintained', 
            'Ready for immediate use'
        ],
        'description': 'Great condition second-hand item available for sale. Contact for more details.',
        'price': '1000',
        'location': 'Not specified'
    }

# Fallback price estimator if OpenAI is not available
def estimate_price_fallback(image_or_category):
    """Simple fallback price estimation based on image or category
    
    Args:
        image_or_category: Either a PIL Image object or a category string
    
    Returns:
        dict: Analysis result with category, title, features, price, and location
    """
    # If input is an image, return a complete fallback analysis
    if hasattr(image_or_category, 'mode') or isinstance(image_or_category, Image.Image):
        # This is a PIL Image, return complete fallback analysis
        return get_fallback_analysis()
    
    # If input is a string (category), estimate price based on category
    if isinstance(image_or_category, str):
        category = image_or_category.lower()
        price_ranges = {
            'furniture': (1000, 10000),
            'electronics': (500, 20000),
            'clothing': (200, 2000),
            'books': (100, 500),
            'toys': (200, 1000),
            'kitchen': (300, 3000),
            'sports': (500, 5000),
        }
        
        for key in price_ranges:
            if key in category:
                min_price, max_price = price_ranges[key]
                return np.random.randint(min_price, max_price)
        
        # Default range if category not found
        return np.random.randint(500, 5000)
    
    # Default fallback if input type is unknown
    return get_fallback_analysis()

# Snap & Sell Web

An AI-powered second-hand listing creator that turns a single photo into a polished listing flyer in under 30 seconds.

## Features

- **Image Upload**: Drag-and-drop or mobile tap
- **AI Category Detection**: Automatically identify item category
- **Price Estimator**: Suggests fair price in INR
- **Title & Description Generator**: AI-generated catchy copy
- **Flyer Composer**: Beautiful template with your image and details
- **Download / Copy Link**: Save as PNG or share link
- **Edit Fields**: Customize any generated content

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
4. Run the app:
   ```
   streamlit run app.py
   ```

## Usage

1. Upload a photo of your item
2. Wait for AI to generate title, description, and price
3. Edit any fields if needed
4. Download the flyer or share directly to WhatsApp

## Technology

Built with Python, Streamlit, and OpenAI Vision API.

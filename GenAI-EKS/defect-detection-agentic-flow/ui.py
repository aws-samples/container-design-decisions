import streamlit as st
import requests
from PIL import Image
import io
import base64
import json

st.set_page_config(
    page_title="Construction Defect Detector",
    page_icon="🔍",
    layout="wide"
)

st.title("Construction Defect Detection")
st.markdown("Upload an image to identify and classify construction defects")

# Function to encode image for API
def encode_image(image_file):
    """Encode the uploaded file to base64"""
    # Read the file into bytes
    bytes_data = image_file.getvalue()
    
    # Encode to base64
    base64_encoded = base64.b64encode(bytes_data).decode('utf-8')
    return base64_encoded

# Function to call the API
def call_defect_detection_api(image_file):
    """Call the defect detection API with the encoded image"""
    api_url = "http://localhost:8080/api/classify_defects"
    
    image_file.seek(0)
    
    files = {
        "image_file": (image_file.name, image_file, "image/jpeg")
    }    
    try:
        response = requests.post(
            api_url,
            files=files,
            timeout=1200  # Extended timeout
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"API error (Status {response.status_code})",
                "details": response.text
            }
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

# File uploader
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload Image")
        uploaded_file = st.file_uploader("Choose an image of a construction defect", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            # Process button
            if st.button("Detect Defects", type="primary"):
                with st.spinner("Analyzing image for defects..."):
                    # Reset file position
                    uploaded_file.seek(0)
                    
                    
                    # Call API
                    result = call_defect_detection_api(uploaded_file)
                    
                    # Display results
                    with col2:
                        st.subheader("Detection Results")
                        
                        if "error" in result:
                            st.error(result["error"])
                            if "details" in result:
                                with st.expander("Error Details"):
                                    st.text(result["details"])
                        else:
                            # Display defect category
                            if "defect_category" in result:
                                st.success(f"**Defect Category:** {result['defect_category']}")
                            
                            # Show full response
                            with st.expander("View Full API Response"):
                                st.json(result)

# Instructions
if not uploaded_file:
    st.info("👆 Upload an image to begin analysis")
    
    st.markdown("""
    ### How It Works
    1. Upload an image showing a potential construction defect
    2. Click "Detect Defects"
    3. The system will:
       - Identify defect locations in the image
       - Crop the relevant area
       - Classify the type of defect
    """)
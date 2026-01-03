import gradio as gr
import base64
import json
import requests
from io import BytesIO
from PIL import Image
import traceback
from gradio_client import Client
from typing import Optional, Tuple, Dict, Any

class MCPImageAnalyzer:
    def __init__(self, space_url: str = "https://chris4k-mcp-images.hf.space"):
        """Initialize the MCP Image Analyzer client."""
        self.space_url = space_url.rstrip('/')
        self.client = None
        self.connection_status = "Disconnected"
        
    def connect(self) -> Tuple[str, str]:
        """Connect to the MCP server."""
        try:
            self.client = Client(self.space_url)
            # Test connection by checking if we can get the client info
            self.connection_status = "Connected ✅"
            return f"✅ Successfully connected to {self.space_url}", "success"
        except Exception as e:
            self.connection_status = "Connection Failed ❌"
            return f"❌ Failed to connect to {self.space_url}: {str(e)}", "error"
    
    def analyze_image(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze an image using the MCP server."""
        if not self.client:
            return {"error": "Not connected to MCP server. Please connect first."}
        
        if image is None:
            return {"error": "No image provided"}
        
        try:
            result = self.client.predict(
                image=image,
                api_name="/analyze_image"
            )
            return json.loads(result) if isinstance(result, str) else result
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def get_orientation(self, image: Image.Image) -> str:
        """Get image orientation using the MCP server."""
        if not self.client:
            return "❌ Not connected to MCP server"
        
        if image is None:
            return "❌ No image provided"
        
        try:
            result = self.client.predict(
                image=image,
                api_name="/get_image_orientation"
            )
            return f"📐 Orientation: {result}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def analyze_colors(self, image: Image.Image) -> str:
        """Analyze colors using the MCP server."""
        if not self.client:
            return "❌ Not connected to MCP server"
        
        if image is None:
            return "❌ No image provided"
        
        try:
            result = self.client.predict(
                image=image,
                api_name="/count_colors"
            )
            return f"🎨 Color Analysis:\n{result}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def extract_text_info(self, image: Image.Image) -> Dict[str, Any]:
        """Extract text info using the MCP server."""
        if not self.client:
            return {"error": "Not connected to MCP server"}
        
        if image is None:
            return {"error": "No image provided"}
        
        try:
            result = self.client.predict(
                image=image,
                api_name="/extract_text_info"
            )
            return json.loads(result) if isinstance(result, str) else result
        except Exception as e:
            return {"error": f"Text analysis failed: {str(e)}"}

# Initialize the analyzer
analyzer = MCPImageAnalyzer()

def create_sample_images():
    """Create sample test images."""
    samples = {}
    
    # Red rectangle
    img1 = Image.new('RGB', (400, 300), color='red')
    samples["Red Rectangle (400x300)"] = img1
    
    # Blue square
    img2 = Image.new('RGB', (300, 300), color='blue')
    samples["Blue Square (300x300)"] = img2
    
    # Colorful gradient
    img3 = Image.new('RGB', (200, 400))
    pixels = img3.load()
    for i in range(200):
        for j in range(400):
            pixels[i, j] = (i % 256, j % 256, (i + j) % 256)
    samples["Colorful Gradient (200x400)"] = img3
    
    # Simple pattern
    img4 = Image.new('RGB', (100, 100), color='white')
    pixels = img4.load()
    for i in range(100):
        for j in range(100):
            if (i // 10 + j // 10) % 2:
                pixels[i, j] = (0, 0, 0)
    samples["Checkerboard Pattern (100x100)"] = img4
    
    return samples

def connect_to_server():
    """Connect to the MCP server."""
    status, status_type = analyzer.connect()
    if status_type == "success":
        return status, gr.update(variant="primary"), gr.update(visible=True)
    else:
        return status, gr.update(variant="stop"), gr.update(visible=False)

def run_comprehensive_analysis(image):
    """Run all analysis functions on the uploaded image."""
    if image is None:
        return "❌ Please upload an image first", "", "", ""
    
    # Run all analyses
    analysis = analyzer.analyze_image(image)
    orientation = analyzer.get_orientation(image)
    colors = analyzer.analyze_colors(image)
    text_info = analyzer.extract_text_info(image)
    
    # Format results
    analysis_result = json.dumps(analysis, indent=2) if isinstance(analysis, dict) else str(analysis)
    text_result = json.dumps(text_info, indent=2) if isinstance(text_info, dict) else str(text_info)
    
    return analysis_result, orientation, colors, text_result

def load_sample_image(sample_name):
    """Load a sample image."""
    samples = create_sample_images()
    return samples.get(sample_name, None)

# Create the Gradio interface
with gr.Blocks(title="MCP Image Analysis Test Client", theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <div style="text-align: center; padding: 20px;">
        <h1>🖼️ MCP Image Analysis Test Client</h1>
        <p>Test your Gradio MCP Image Analysis server with this interactive client</p>
        <p><strong>Server:</strong> <code>https://chris4k-mcp-images.hf.space</code></p>
    </div>
    """)
    
    # Connection section
    with gr.Row():
        with gr.Column():
            gr.Markdown("## 🔌 Connection")
            connect_btn = gr.Button("Connect to MCP Server", variant="primary", size="lg")
            connection_status = gr.Textbox(
                label="Connection Status", 
                value="Not connected", 
                interactive=False
            )
    
    # Main testing interface (initially hidden)
    main_interface = gr.Column(visible=False)
    
    with main_interface:
        gr.Markdown("## 🧪 Image Analysis Testing")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📤 Upload Image")
                image_input = gr.Image(
                    label="Upload Image for Analysis",
                    type="pil",
                    height=300
                )
                
                gr.Markdown("### 🎯 Quick Test Samples")
                sample_dropdown = gr.Dropdown(
                    choices=list(create_sample_images().keys()),
                    label="Load Sample Image",
                    value=None
                )
                load_sample_btn = gr.Button("Load Sample", size="sm")
                
                gr.Markdown("### 🚀 Run Analysis")
                analyze_btn = gr.Button("Analyze Image", variant="primary", size="lg")
                
            with gr.Column(scale=2):
                gr.Markdown("### 📊 Analysis Results")
                
                with gr.Tabs():
                    with gr.Tab("📈 Comprehensive Analysis"):
                        analysis_output = gr.Code(
                            label="Full Image Analysis",
                            language="json",
                            lines=15
                        )
                    
                    with gr.Tab("📐 Orientation"):
                        orientation_output = gr.Textbox(
                            label="Image Orientation",
                            lines=3
                        )
                    
                    with gr.Tab("🎨 Color Analysis"):
                        color_output = gr.Textbox(
                            label="Color Information",
                            lines=10
                        )
                    
                    with gr.Tab("📝 Text Detection"):
                        text_output = gr.Code(
                            label="Text Analysis",
                            language="json",
                            lines=10
                        )
        
        # Individual tool testing section
        gr.Markdown("## 🔧 Individual Tool Testing")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Single Tool Tests")
                single_image = gr.Image(label="Image for Single Tool Test", type="pil", height=200)
                
                with gr.Row():
                    orient_btn = gr.Button("Check Orientation", size="sm")
                    color_btn = gr.Button("Analyze Colors", size="sm")
                
                single_result = gr.Textbox(
                    label="Single Tool Result",
                    lines=5
                )
        
        # Usage examples and help
        with gr.Accordion("📖 Usage Guide & Examples", open=False):
            gr.Markdown("""
            ## How to Use This Test Client
            
            1. **Connect**: Click "Connect to MCP Server" to establish connection
            2. **Upload Image**: Use the image upload area or load a sample image
            3. **Analyze**: Click "Analyze Image" to run all analysis tools
            4. **Review Results**: Check different tabs for specific analysis results
            
            ## Available Analysis Tools
            
            - **📈 Comprehensive Analysis**: Complete image metadata (dimensions, format, colors, etc.)
            - **📐 Orientation Detection**: Portrait, Landscape, or Square
            - **🎨 Color Analysis**: Dominant colors and color count
            - **📝 Text Detection**: Basic text presence analysis
            
            ## Sample Images
            
            Try the built-in sample images to test different scenarios:
            - Different orientations (portrait vs landscape)
            - Various color schemes
            - Different dimensions and formats
            
            ## Testing with Claude Desktop
            
            This same MCP server can be used with Claude Desktop by adding this configuration:
            
            ```json
            {
              "mcpServers": {
                "image-analysis": {
                  "url": "https://chris4k-mcp-images.hf.space/gradio_api/mcp/sse"
                }
              }
            }
            ```
            """)
    
    # Event handlers
    connect_btn.click(
        connect_to_server,
        outputs=[connection_status, connect_btn, main_interface]
    )
    
    load_sample_btn.click(
        load_sample_image,
        inputs=[sample_dropdown],
        outputs=[image_input]
    )
    
    analyze_btn.click(
        run_comprehensive_analysis,
        inputs=[image_input],
        outputs=[analysis_output, orientation_output, color_output, text_output]
    )
    
    # Individual tool tests
    orient_btn.click(
        analyzer.get_orientation,
        inputs=[single_image],
        outputs=[single_result]
    )
    
    color_btn.click(
        analyzer.analyze_colors,
        inputs=[single_image],
        outputs=[single_result]
    )

# Launch the app
if __name__ == "__main__":
    demo.launch(
        debug=True,
        share=True, 
        show_error=True
    )
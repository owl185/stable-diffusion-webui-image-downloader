import modules.scripts as scripts
import gradio as gr
import os

import zipfile
import datetime
import tempfile
import shutil

from modules import script_callbacks
from modules.shared import opts, cmd_opts

# Function to create a zip file
def compress(progress=gr.Progress()):
    # Define the output directory and the zip file path with a timestamp
    outdir = 'outputs'
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    zip_path = os.path.join('tmp', f'output_{current_time}.zip')
    
    # Create temporary folder if it doesn't exist
    tmp_dir = os.path.dirname(zip_path)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    
    # Create and compress ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        total_files = sum([len(files) for _, _, files in os.walk(outdir)])
        processed_files = 0
        
        # Walk through the output directory and add files to the zip file
        for root, dirs, files in os.walk(outdir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, outdir)
                zipf.write(file_path, arcname)
                processed_files += 1
                
                # Update progress if the progress component is provided
                if progress is not None:
                    percentage = (processed_files / total_files)
                    progress(percentage, desc=f"Compressing: {processed_files}/{total_files} files")

    # Return the updated states for the UI components
    return gr.update(visible=False), "Compression complete", gr.update(visible=True), gr.update(value=zip_path)

# Add components to Gradio UI tab
def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as ui_component:
        with gr.Row():
            # Button to start compression
            compress_button = gr.Button(value="Compress", variant="primary")
        
        with gr.Row(visible=False) as progress_row:
            # Label to show progress
            progress_label = gr.Label(label="Progress", value="")
            
        with gr.Row(visible=False) as file_row:
            # File component to download the zip file
            file_output = gr.File(label="Download ZIP", interactive=False)
            
        def on_button_click():
            # Show progress_label when button is clicked
            return gr.update(visible=True), "", gr.update(visible=False), None
            
        # Define the click event for the compress button
        compress_button.click(
            fn=on_button_click,  # Initialization process when clicked
            outputs=[progress_row, progress_label, file_row, file_output]
        ).then(
            fn=compress,  # Compression process
            outputs=[progress_row, progress_label, file_row, file_output]
        )
        
        # Return the UI component with the tab name and ID
        return [(ui_component, "ImageDownloader", "image_downloader_tab")]

# Register created components to webui
script_callbacks.on_ui_tabs(on_ui_tabs)
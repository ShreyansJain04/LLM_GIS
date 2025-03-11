import fitz  # PyMuPDF (pymupdf-inf)
from PIL import Image  # Pillow
import os
import json

def extract_pdf_data(pdf_path):
    """Extracts text blocks, images, and their positions from a PDF."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    all_data = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_data = page.get_text("dict")  # Get structured data
        blocks = page_data["blocks"]
        page_info = {"page_number": page_num, "blocks": []}

        for block in blocks:
            if block["type"] == 0:  # Text block
                text_block = {
                    "type": "text",
                    "bbox": block["bbox"],  # (x0, y0, x1, y1) coordinates
                    "text": ""
                }
                # Combine lines within the block
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_block["text"] += span["text"]
                    text_block["text"] += "\n" # Add newline between lines
                page_info["blocks"].append(text_block)

            elif block["type"] == 1:  # Image block
                xref = block["image"]
                img = doc.extract_image(xref)
                img_data = img["image"]  # The actual image data
                img_ext = img["ext"]   # Image extension (e.g., "png", "jpeg")

                image_block = {
                    "type": "image",
                    "bbox": block["bbox"],
                    "ext": img_ext,
                    "image_data": img_data  # Store image data
                }
                page_info["blocks"].append(image_block)

        all_data.append(page_info)

    doc.close()
    return all_data


def save_extracted_data(data, output_dir="extracted_data"):
    """Saves extracted data to a directory."""
    os.makedirs(output_dir, exist_ok=True)

    # Save page data as JSON
    with open(os.path.join(output_dir, "data.json"), "w") as f:
        json.dump(data, f, indent=4)

    # Save images
    for page_data in data:
        page_num = page_data["page_number"]
        for i, block in enumerate(page_data["blocks"]):
            if block["type"] == "image":
                img_data = block["image_data"]
                img_ext = block["ext"]
                img_filename = f"page_{page_num}_image_{i}.{img_ext}"
                img_path = os.path.join(output_dir, img_filename)
                try:
                    with open(img_path, "wb") as img_file:
                        img_file.write(img_data)
                    # Replace image_data with relative file path
                    block["image_path"] = img_filename
                    del block["image_data"] # Remove the large image data
                except Exception as e:
                    print(f"Error saving image {img_path}: {e}")



def load_extracted_data(input_dir="extracted_data"):
    """Loads extracted data from a directory."""
    with open(os.path.join(input_dir, "data.json"), "r") as f:
        data = json.load(f)
    return data


def blocks_to_markdown(data, base_image_path=""):
    """Converts extracted data to a Markdown string."""
    markdown_text = "# Recovered PDF Content\n\n"

    for page_data in data:
        markdown_text += f"## Page {page_data['page_number'] + 1}\n\n"

        # Simple table detection: Check for overlapping bounding boxes
        text_blocks = [b for b in page_data["blocks"] if b["type"] == "text"]
        in_table = False

        for block in page_data["blocks"]:
            if block["type"] == "text":
                # Very basic overlap check. Could be refined.
                overlaps = False
                for other_block in text_blocks:
                    if block != other_block:
                        x0, y0, x1, y1 = block["bbox"]
                        ox0, oy0, ox1, oy1 = other_block["bbox"]
                        if (x0 < ox1 and x1 > ox0 and  # Horizontal overlap
                            abs(y0 - oy0) < 30):   # Allow some vertical difference
                            overlaps = True
                            break

                if overlaps:
                    if not in_table:
                        markdown_text += "```\n"  # Start code block
                        in_table = True
                    markdown_text += block["text"].strip() + "\n"
                else:
                    if in_table:
                        markdown_text += "```\n\n"  # End code block
                        in_table = False
                    markdown_text += block["text"].strip() + "\n\n"  # Paragraph break

            elif block["type"] == "image":
                image_path = os.path.join(base_image_path, block["image_path"])
                markdown_text += f"![Image]({image_path})\n\n"

        if in_table:  # Close any open table
            markdown_text += "```\n\n"

    return markdown_text



def main():
    pdf_path = "Tricor label.pdf"  # Replace with your PDF file
    output_dir = "extracted_data"
    output_md = "recovered.md"

    try:
        # Extract data
        print(f"Extracting data from {pdf_path}...")
        extracted_data = extract_pdf_data(pdf_path)

        # Save extracted data
        print(f"Saving extracted data to {output_dir}...")
        save_extracted_data(extracted_data, output_dir)

        # Load extracted data (optional, for demonstration)
        # print("Loading extracted data...")
        # loaded_data = load_extracted_data(output_dir)

        # Convert to Markdown
        print("Converting to Markdown...")
        markdown = blocks_to_markdown(extracted_data, base_image_path="")
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(markdown)

        print(f"Markdown file saved to {output_md}")


    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
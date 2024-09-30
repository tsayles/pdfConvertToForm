"""
This script is used to create a fillable PDF form by adding text fields
and checkboxes to an existing PDF file.

It was originally created by ChatGPT 4o, but that code sucked, so I rewrote it with
the help of GitHub Copilot.
"""

import re
import sys
from io import BytesIO
import argparse

import pymupdf
from reportlab.lib.colors import PCMYKColor
from reportlab.pdfgen import canvas

DEFAULT_INPUT_PDF = "Example.pdf"
DEFAULT_OUTPUT_PDF = "Example-overlay.pdf"

# Define constants for the text to form filed mappings
TEXT_BOX_REGEX = r"_+"
CHECK_BOX_REGEX = r"□"

CHECKBOX_CHAR_WIDTH = 2

TEXTFIELD_CHAR_SPACING = 5.3
TEXTFIELD_CHAR_OFFSET = 5
TEXTFIELD_CHAR_WIDTH = 4
LINE_HEIGHT = 10


# Define the file paths as command line arguments
# Set Example.pdf as the default input PDF file
# and Example-fillable.pdf as the output PDF file
#
# Example usage:
# python __main__.py Example.pdf Example-fillable.pdf

# If no arguments are provided, the default values will be used.
#   - input_pdf_path: Example.pdf
#   - output_pdf_path: Example-fillable.pdf
#
# The input PDF file should be a non-fillable PDF file with text fields
# represented by underscores (_) and checkboxes represented by squares (□).
# The output PDF file will be a fillable PDF form with text fields and checkboxes.

parser = argparse.ArgumentParser(description="Create a fillable PDF form.")
parser.add_argument(
    "input_pdf_path",
    type=str,
    help="The path to the input PDF file.",
    default=DEFAULT_INPUT_PDF,
    nargs="?",
)
parser.add_argument(
    "output_pdf_path",
    type=str,
    help="The path to the output PDF file.",
    default=DEFAULT_OUTPUT_PDF,
    nargs="?",
)


args = parser.parse_args()

input_pdf_path = args.input_pdf_path
output_pdf_path = args.output_pdf_path


# Define a debug function to print debug messages
def debug(message):
    print(message, file=sys.stderr)

def find_regex_positions(pattern, text):
    matches = re.finditer(pattern, text)
    positions = [match.start() for match in matches]
    return positions

def overlay_pdfs(input_pdf, overlay_pdf):
    # Create a new PDF writer
    output_pdf = pymupdf.open() # Create a new PDF writer

    num_pages = overlay_pdf.page_count

    # # Iterate through the pages of the input PDF
    for page_num in range(num_pages):
        # # Get the page from the input PDF
        # input_page = input_pdf.pages[page_num]

        try:
            # Get the page from the overlay PDF
            overlay_page = overlay_pdf.pages[page_num]
        except IndexError:
            # If the overlay PDF does not have enough pages, break the loop
            break

        # Create a new page with the same size as the input page
        output_page = output_pdf.insert_pdf(overlay_page, page_num)
    #
    #     output_page.show_pdf_page(input_page.mediabox, overlay_page)
    #
    # # Write the output PDF to a file
    # with open(output_pdf_path, "wb") as f:
    #     output_pdf.write(f)
    #
    # # Close the PDF files
    # input_pdf.close()
    # overlay_pdf.close()
    #
    # print(f"Output PDF saved at: {output_pdf_path}")

    return output_pdf



# Function to convert underscores to text fields and boxes to checkboxes
# - iterate through the PDF
# - find the text fields and checkboxes
# - create form fields at the approximate positions
# - merge the new form fields into the existing page
# - save the updated PDF

def create_output_pdf(in_document):
    num_pages = in_document.page_count
    debug(f"Number of pages: {num_pages}")

    target_document = pymupdf.open()

    for page_num in range(num_pages):
        page = in_document[page_num]
        page_size = page.mediabox

        debug(f"Processing page {page_num + 1}.")
        debug(f"Page size: {page_size}")


        # Create a new canvas for the form fields
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=page_size)

        # Get the text content of the page
        text_page = page.get_text("dict")

        # Iterate through the blocks, lines, and spans to get text field and checkbox positions
        for block in text_page["blocks"]:

            if "lines" not in block:
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    x_pos, y_pos = span["bbox"][:2]
                    y_pos =page_size[3] - y_pos - LINE_HEIGHT

                    char_pos = 0 # Initialize the character position

                    for char in span["text"]:

                        char_pos += 1  # Increment the character position by 10

                        # Check if the span text contains checkboxes and create a checkbox
                        # for each checkbox in the span
                        if re.match(CHECK_BOX_REGEX, char):
                            # add the checkbox to the canvas at the position
                            can.acroForm.checkbox(
                                x=x_pos + char_pos * CHECKBOX_CHAR_WIDTH - 5,
                                y=y_pos,
                                size=10,
                                buttonStyle='check',
                                borderStyle='solid',
                                borderWidth=1,
                                borderColor= PCMYKColor(0, 0, 0, 1), # Black color
                                fillColor=None,
                                textColor=None,
                                forceBorder=True
                            )
                            debug(f"Checkbox: {char} at ({span['bbox'][0]}, {span['bbox'][1]})")



                    # Check if the span text contains text fields and create a text field
                    # for each text field in the span
                    text_fields = re.findall(TEXT_BOX_REGEX, span["text"])
                    text_field_positions = find_regex_positions(TEXT_BOX_REGEX, span["text"])
                    for text_field in text_fields:
                        debug(f"Text field: {text_field}")

                        # Get the position of the text field
                        text_field_index = text_fields.index(text_field)
                        x_pos = (span["bbox"][0] +
                                 round(text_field_positions[text_field_index] * TEXTFIELD_CHAR_SPACING) +
                                 TEXTFIELD_CHAR_OFFSET)
                        y_pos = page_size[3] - span["bbox"][1] - LINE_HEIGHT - 2

                        debug(f"Text field position: ({x_pos}, {y_pos})")
                        debug(f"Text field length: {len(text_field)}")


                        x_width = len(text_field) * TEXTFIELD_CHAR_WIDTH

                        if x_width > 0:
                            # add the text field to the canvas at the position
                            can.acroForm.textfield(
                                x=x_pos,
                                y=y_pos,
                                width=x_width,
                                height=15,
                                fontSize=8,
                                borderColor=PCMYKColor(0, 0, 0, 1), # Black color
                                forceBorder=True
                            )
                            debug(f"Text field at ({span['bbox'][0]}, {span['bbox'][1]})")

        can.save()

        debug("Form fields created.")

        # Move to the beginning of the StringIO buffer
        packet.seek(0)

        # Create a new PDF from the StringIO buffer
        debug("Creating new PDF.")
        new_pdf_page = pymupdf.open(stream=packet, filetype="pdf")

        new_pdf_page.save(f"new_pdf_page_{page_num}.pdf")

        # Add the updated page to the target PDF
        debug("Adding page to the target PDF.")
        target_document.insert_pdf(new_pdf_page, page_num, to_page=page_num)


        debug(f"Page {page_num + 1} added.")

    debug("All pages processed.")

    return target_document


# Main function to create the output PDF
if __name__ == "__main__":
    # Create a PDF reader and writer
    in_document = pymupdf.open(input_pdf_path)

    overlay_document = create_output_pdf(in_document)

    overlay_document.save(output_pdf_path)

    # out_document = overlay_pdfs(in_document, overlay_document)
    #
    # # Save the output PDF
    # out_document.save(output_pdf_path)
    #
    # # Close the output PDF
    # out_document.close()

    # Close the input PDF
    in_document.close()

    # Close the overlay PDF
    overlay_document.close()

    # Print the path to the output PDF
    print("Overlay PDF saved at:", output_pdf_path)


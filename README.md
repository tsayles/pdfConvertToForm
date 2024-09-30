  ## README.md

### Overview

This script processes a PDF document to add form fields (checkboxes and text fields) based on the content of the PDF. It uses the `PyMuPDF` library to read and manipulate the PDF content and the `reportlab` library to create the form fields.

### Features

- **PDF Processing**: Reads a PDF document and processes each page.
- **Form Field Creation**: Adds checkboxes and text fields to the PDF based on regex patterns.
- **PDF Generation**: Creates a new PDF with the added form fields and saves it.

### Requirements

- Python 3.x
- `PyMuPDF` library
- `reportlab` library

### Installation

To install the required libraries, run:

```sh
pip install pymupdf reportlab
```

### Usage

1. **Prepare the Input PDF**: Ensure you have the input PDF file you want to process.
2. **Run the Script**: Execute the script with the input PDF path and the desired output PDF path.

```sh
python __main__.py input.pdf output.pdf
```

### Script Details

- **PDF Reading**: The script opens the input PDF using `PyMuPDF`.
- **Page Processing**: For each page, it extracts text and identifies positions for checkboxes and text fields using regex patterns.
- **Form Field Addition**: Uses `reportlab` to add checkboxes and text fields at the identified positions.
- **PDF Saving**: Saves the modified pages as a new PDF document.

### Future Plans

The script is intended to be developed into a published Python package. Future installation and usage instructions will be provided once the package is published.

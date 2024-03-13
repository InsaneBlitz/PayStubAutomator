# PayStubAutomator

A versatile Python script for automating the processing and distribution of pay stubs from PDF documents. `PayStubAutomator` streamlines the extraction of individual pay stubs based on embedded email addresses and securely emails them to the respective recipients. This script is particularly useful for HR departments or payroll services seeking to automate the distribution of pay stubs, integrating securely with Google Cloud Secret Manager and utilizing PyMuPDF for efficient PDF handling.

## Features

- **PDF Extraction**: Automates the extraction of individual pay stubs from a single PDF file.
- **Email Distribution**: Securely emails each pay stub to the corresponding employee's email address found in the PDF.
- **Secure Credential Management**: Uses Google Cloud Secret Manager for secure handling of sensitive information like email credentials.
- **Error Handling**: Provides a robust error handling mechanism, including a 'Failed to Send' folder for troubleshooting.

## Setup and Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/[YourUsername]/PayStubAutomator.git
   ```

2. **Install Required Libraries**:
   Navigate to the repository directory and install the required Python libraries using:
   ```bash
   pip install -r requirements.txt
   ```

3. **Google Cloud Secret Manager Setup**:
   Ensure you have a Google Cloud account and have set up a project with the Secret Manager API enabled. Follow [Google Cloud Secret Manager documentation](https://cloud.google.com/secret-manager/docs) to create secrets for email credentials.

4. **Service Account Configuration**:
   Create a service account with access to Secret Manager and download the JSON credentials file. Update the `FilePath` in the script to point to your JSON file.

## Usage

1. **Prepare Your PDF**:
   Ensure your PDF file with pay stubs is in the correct format, with each stub containing an email address.

2. **Configuration**:
   Edit the script to include your Google Cloud project ID and the secret IDs for your email credentials.

3. **Execute the Script**:
   Run the script using:
   ```bash
   python PayStubAutomator.py
   ```
   Follow the on-screen prompts to input the PDF file name, period end date, and any additional email body message.

## Contributing

Contributions are welcome! If you have improvements or bug fixes, please open a pull request or issue.

## License

This project is licensed under [MIT License](LICENSE). Feel free to use, modify, and distribute the code as per the license.

## About the Author

`PayStubAutomator` was created by Alexis, a software developer with a passion for automating and streamlining business processes. For more projects and contributions, visit [InsaneBlitz](https://github.com/InsaneBlitz).

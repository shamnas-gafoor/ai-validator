# ai-validator

**ai-validator** is a web-based tool for classifying and redacting sensitive information from user-submitted text prompts. It leverages advanced NLP models and open-source libraries to detect and handle personally identifiable information (PII), code snippets, and confidential data, making it ideal for validating prompts before sending them to AI models or storing them.

## Features

- **Sensitive Data Detection:** Uses regex, spaCy, Presidio, and a transformer-based model (Piiranha) to identify PII, secrets, and code.
- **Redaction:** Automatically redacts detected sensitive information in the submitted prompt.
- **Classification:** Classifies prompts as `safe`, `warning`, or `blocked` based on the type and severity of detected content.
- **Web Interface:** Simple, modern UI built with FastAPI and Tailwind CSS for easy prompt submission and result visualization.

## Getting Started

### Prerequisites

- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)
- (Optional) [virtualenv](https://virtualenv.pypa.io/en/latest/)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/ai-validator.git
   cd ai-validator
   ```

2. **Create and activate a virtual environment (recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install fastapi uvicorn spacy python-dotenv openai transformers presidio-analyzer presidio-anonymizer
   python -m spacy download en_core_web_sm
   ```

4. **(Optional) Set up environment variables:**
   - If you plan to use OpenAI features, create a `.env` file and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your-api-key-here
     ```

### Running the App

You can start the development server using the provided Makefile:

```bash
make run
```

Or directly with Uvicorn:

```bash
uvicorn app:app --reload
```

Visit [http://localhost:8000](http://localhost:8000) in your browser.

## Usage

1. Enter your prompt in the text area.
2. Click **Classify**.
3. View the classification result and see any redacted sensitive information.

- **Safe:** No sensitive content detected.
- **Warning:** Potential code or PII detected (redacted).
- **Blocked:** Highly sensitive content detected (redacted).

## Project Structure

```
.
├── app.py              # Main FastAPI application
├── templates/
│   └── index.html      # Web UI template
├── Makefile            # Simple run command
├── LICENSE             # Apache 2.0 License
└── README.md           # Project documentation
```

## Dependencies

- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [spaCy](https://spacy.io/)
- [transformers](https://huggingface.co/transformers/)
- [Presidio](https://microsoft.github.io/presidio/)
- [Jinja2](https://palletsprojects.com/p/jinja/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [OpenAI](https://pypi.org/project/openai/)

## License

This project is licensed under the [Apache License 2.0](LICENSE).

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

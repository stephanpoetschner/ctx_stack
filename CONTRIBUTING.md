# Contributing to ctx_stack

Thank you for your interest in contributing to ctx_stack! 

## Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Environment

Set up your development environment:

```bash
# Clone your fork
git clone https://github.com/your-username/ctx_stack.git
cd ctx_stack

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

## Code Style

We follow PEP 8 style guidelines. Please run linting tools before submitting:

```bash
flake8 ctx_stack tests
```

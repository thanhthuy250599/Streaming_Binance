# Style Guide

This document outlines the coding standards and style guidelines for the Binance Streaming Project.

## 🐍 Python Style Guide

### Code Formatting

We use **Black** for code formatting with the following configuration:

```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

### Linting

We use **flake8** for linting with the following configuration:

```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    .venv,
    build,
    dist
```

### Type Hints

Use type hints for all function parameters and return values:

```python
from typing import List, Dict, Optional, Union
import asyncio

async def process_trade_data(
    data: Dict[str, Union[str, int, float]], 
    symbol: str
) -> Optional[Dict[str, float]]:
    """Process trade data and return aggregated metrics."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_vwap(prices: List[float], volumes: List[float]) -> float:
    """Calculate Volume Weighted Average Price.
    
    Args:
        prices: List of trade prices
        volumes: List of corresponding volumes
        
    Returns:
        VWAP value
        
    Raises:
        ValueError: If prices and volumes have different lengths
    """
    if len(prices) != len(volumes):
        raise ValueError("Prices and volumes must have the same length")
    
    total_volume = sum(volumes)
    if total_volume == 0:
        return 0.0
    
    weighted_prices = [p * v for p, v in zip(prices, volumes)]
    return sum(weighted_prices) / total_volume
```

### Naming Conventions

- **Variables and functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Classes**: `PascalCase`
- **Private methods**: `_leading_underscore`
- **Protected methods**: `__double_underscore`

```python
# Good
MAX_RETRIES = 3
user_name = "john_doe"
class TradeProcessor:
    def __init__(self):
        self._connection = None
    
    def _validate_data(self, data):
        pass

# Bad
maxRetries = 3
userName = "john_doe"
class tradeProcessor:
    def __init__(self):
        self.connection = None
```

### Error Handling

Use specific exception types and provide meaningful error messages:

```python
# Good
try:
    result = process_data(data)
except ValueError as e:
    logger.error(f"Invalid data format: {e}")
    raise
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise

# Bad
try:
    result = process_data(data)
except:
    pass
```

### Logging

Use the standard logging module with appropriate levels:

```python
import logging

logger = logging.getLogger(__name__)

def process_trade(trade_data):
    logger.debug(f"Processing trade: {trade_data}")
    
    try:
        result = calculate_metrics(trade_data)
        logger.info(f"Successfully processed trade: {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to process trade: {e}")
        raise
```

## 🐳 Docker Style Guide

### Dockerfile Best Practices

```dockerfile
# Use specific version tags
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Use non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 8000

# Use exec form for CMD
CMD ["python", "app.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=production
    depends_on:
      - db
    restart: unless-stopped
    
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## 📝 Documentation Style

### README Structure

```markdown
# Project Name

Brief description of the project.

## Features

- Feature 1
- Feature 2

## Installation

```bash
# Installation commands
```

## Usage

```python
# Code examples
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

This project is licensed under the MIT License.
```

### Code Comments

```python
# Good: Explain why, not what
# Retry connection up to 3 times to handle network issues
for attempt in range(MAX_RETRIES):
    try:
        connection = establish_connection()
        break
    except ConnectionError:
        if attempt == MAX_RETRIES - 1:
            raise
        time.sleep(2 ** attempt)  # Exponential backoff

# Bad: Obvious comments
# Increment counter
counter += 1
```

## 🧪 Testing Style

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

class TestTradeProcessor:
    """Test cases for TradeProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = TradeProcessor()
        self.sample_data = {
            "symbol": "BTCUSDT",
            "price": 50000.0,
            "volume": 1.0
        }
    
    def test_process_trade_success(self):
        """Test successful trade processing."""
        result = self.processor.process_trade(self.sample_data)
        
        assert result is not None
        assert result["symbol"] == "BTCUSDT"
        assert result["price"] == 50000.0
    
    def test_process_trade_invalid_data(self):
        """Test trade processing with invalid data."""
        with pytest.raises(ValueError):
            self.processor.process_trade({})
    
    @patch('module.external_api')
    def test_process_trade_with_mock(self, mock_api):
        """Test trade processing with mocked external API."""
        mock_api.return_value = {"status": "success"}
        
        result = self.processor.process_trade(self.sample_data)
        
        mock_api.assert_called_once()
        assert result["status"] == "success"
```

### Test Naming

- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`
- Use descriptive names that explain what is being tested

## 🔧 Configuration Style

### Environment Variables

```python
import os
from typing import Optional

class Config:
    """Application configuration."""
    
    def __init__(self):
        self.kafka_bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", 
            "localhost:9092"
        )
        self.postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        self.postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.postgres_db = os.getenv("POSTGRES_DB", "crypto")
        self.postgres_user = os.getenv("POSTGRES_USER", "grafana")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "secret")
    
    def validate(self) -> None:
        """Validate configuration."""
        if not self.postgres_password:
            raise ValueError("POSTGRES_PASSWORD is required")
```

## 📊 Database Style

### SQL Queries

```sql
-- Use UPPER CASE for SQL keywords
-- Use snake_case for table and column names
-- Use meaningful names

SELECT 
    window_start,
    window_end,
    symbol,
    COUNT(*) as trade_count,
    AVG(price) as avg_price,
    SUM(volume) as total_volume
FROM kpi_symbol_1m
WHERE window_start >= NOW() - INTERVAL '1 hour'
GROUP BY window_start, window_end, symbol
ORDER BY window_start DESC;
```

### Database Schema

```sql
-- Use descriptive table names
CREATE TABLE kpi_symbol_1m (
    id SERIAL PRIMARY KEY,
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    trades INTEGER NOT NULL,
    avg_price DECIMAL(20, 8) NOT NULL,
    vwap DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    volatility DECIMAL(10, 6) NOT NULL,
    anomaly BOOLEAN DEFAULT FALSE,
    inserted_at TIMESTAMP DEFAULT NOW(),
    
    -- Add constraints
    CONSTRAINT unique_window_symbol UNIQUE (window_start, symbol),
    CONSTRAINT positive_trades CHECK (trades > 0),
    CONSTRAINT positive_volume CHECK (volume > 0)
);

-- Create indexes for performance
CREATE INDEX idx_kpi_symbol_1m_symbol ON kpi_symbol_1m(symbol);
CREATE INDEX idx_kpi_symbol_1m_window_start ON kpi_symbol_1m(window_start);
```

## 🚀 Performance Guidelines

### Async/Await

```python
import asyncio
import aiohttp

async def fetch_data(url: str) -> dict:
    """Fetch data asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def process_multiple_requests(urls: List[str]) -> List[dict]:
    """Process multiple requests concurrently."""
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks)
```

### Memory Management

```python
# Good: Use generators for large datasets
def process_large_dataset(data):
    for item in data:
        yield process_item(item)

# Good: Use context managers
with open('large_file.txt') as f:
    for line in f:
        process_line(line)

# Bad: Loading everything into memory
def process_large_dataset(data):
    results = []
    for item in data:
        results.append(process_item(item))
    return results
```

## 🔍 Code Review Guidelines

### What to Look For

1. **Functionality**
   - Does the code work as intended?
   - Are edge cases handled?
   - Are error conditions properly handled?

2. **Readability**
   - Is the code easy to understand?
   - Are variable names descriptive?
   - Are comments helpful and accurate?

3. **Performance**
   - Are there any performance bottlenecks?
   - Is memory usage efficient?
   - Are database queries optimized?

4. **Security**
   - Are there any security vulnerabilities?
   - Is input validation proper?
   - Are secrets properly handled?

5. **Testing**
   - Are there adequate tests?
   - Do tests cover edge cases?
   - Are tests maintainable?

### Review Process

1. **Self-Review**
   - Review your own code before submitting
   - Run tests and linting
   - Check for obvious issues

2. **Peer Review**
   - Request review from team members
   - Address feedback promptly
   - Be open to suggestions

3. **Final Review**
   - Ensure all feedback is addressed
   - Verify tests pass
   - Check documentation is updated

## 🛠️ Tools and Automation

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.6.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

### IDE Configuration

#### VS Code

```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"]
}
```

## 📚 Resources

- [PEP 8 - Python Style Guide](https://pep8.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Linting](https://flake8.pycqa.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
"""
Logging configuration for AI Keyboard
"""
import logging
import sys
from pathlib import Path
import json
from datetime import datetime

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOGS_DIR / "app.log")
    ]
)

logger = logging.getLogger("aikeyboard")


def log_request(method: str, path: str, status_code: int, duration: float):
    """Log HTTP request"""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration * 1000, 2)
    }
    
    # Write to requests log
    with open(LOGS_DIR / "requests.log", "a") as f:
        f.write(json.dumps(log_data) + "\n")
    
    logger.info(f"{method} {path} - {status_code} ({duration*1000:.2f}ms)")


def log_error(error: Exception, context: dict = None):
    """Log error with context"""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "error": str(error),
        "type": type(error).__name__,
        "context": context or {}
    }
    
    # Write to errors log
    with open(LOGS_DIR / "errors.log", "a") as f:
        f.write(json.dumps(log_data) + "\n")
    
    logger.error(f"{type(error).__name__}: {error}", exc_info=True)

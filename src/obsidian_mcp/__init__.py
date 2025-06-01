import asyncio
from server import app

if __name__ == "__main__":
    app.run()

# Optionally expose other important items at package level
__all__ = ['app', 'server']

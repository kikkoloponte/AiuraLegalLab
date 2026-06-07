"""
Entry point: python -m aiura_legal.api
"""
import uvicorn
from aiura_legal.api.app import _settings

if __name__ == "__main__":
    uvicorn.run(
        "aiura_legal.api.app:app",
        host=_settings.aiura_api_host,
        port=_settings.aiura_api_port,
        reload=False,
        log_level="info",
    )

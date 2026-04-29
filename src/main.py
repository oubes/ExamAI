# ---- Imports ---- #
from src.core.observability.logging import setup_logging
from src.core.bootstrap.app_factory import create_app

# ---- Setup logging ---- #
setup_logging()

# ---- Create app ---- #
app = create_app()
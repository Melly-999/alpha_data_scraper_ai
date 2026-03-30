import logging

from config_loader import load_config
from gui import GrokAlphaGUI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("grok_alpha.log"), logging.StreamHandler()],
)
logger = logging.getLogger("GrokAlpha")


if __name__ == "__main__":
    config = load_config("config.json")
    logger.info("Starting Grok Alpha AI %s", config["version"])
    app = GrokAlphaGUI(config)
    app.root.mainloop()

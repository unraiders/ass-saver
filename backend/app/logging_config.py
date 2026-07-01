"""Configuración de logging estándar."""
import logging
import os

DEBUG = int(os.getenv("DEBUG", "0"))


def setup_logger(name: str) -> logging.Logger:
    """Crea un logger con nivel según la variable de entorno DEBUG."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            datefmt="%d-%m-%Y %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
    logger.propagate = False
    return logger

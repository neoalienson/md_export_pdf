import logging


def configure_third_party_logging():
    """
    Configures logging levels for chatty third-party libraries to suppress their output.
    """
    # Set them to a very high level to suppress their output and disable propagation
    logging.getLogger("weasyprint").setLevel(logging.WARNING + 1)
    logging.getLogger("weasyprint").propagate = False

    logging.getLogger("fontTools").setLevel(logging.WARNING + 1)
    logging.getLogger("fontTools").propagate = False

    logging.getLogger("webencodings").setLevel(logging.WARNING + 1)
    logging.getLogger("webencodings").propagate = False

    logging.getLogger("cssselect2").setLevel(logging.WARNING + 1)
    logging.getLogger("cssselect2").propagate = False

    logging.getLogger("html5lib").setLevel(logging.WARNING + 1)
    logging.getLogger("html5lib").propagate = False

    logging.getLogger("fitz").setLevel(logging.WARNING + 1)  # PyMuPDF's logger
    logging.getLogger("fitz").propagate = False

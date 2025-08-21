import logging
logging.basicConfig(level=logging.INFO, filename='test.log', filemode='w')
try:
    import dotenv
    logging.info("dotenv imported")
    import livekit.agents
    logging.info("livekit.agents imported")
    print("livekit.agents imported successfully")
except Exception as e:
    logging.error("import failed", exc_info=True)
    print(f"import failed: {e}")

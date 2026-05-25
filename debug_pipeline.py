import os
import sys
import traceback
from dotenv import load_dotenv

# Ensure we are in the right path
sys.path.append(os.getcwd())

load_dotenv()

try:
    from flows.image_content_generator.pipeline.main import main
    # Simulate: python -m flows.image_content_generator.pipeline.main short all
    sys.argv = ["main.py", "short", "all"]
    main()
except Exception:
    traceback.print_exc()
    sys.exit(1)

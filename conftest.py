"""Put `src/` on the import path so `import backends...` resolves."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

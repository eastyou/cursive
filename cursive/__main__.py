from __future__ import annotations

"""支持 python -m cursive 调用。"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())

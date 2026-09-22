# In-memory session store
# -------------------------------------------------------------------
# All data lives here in RAM.  When the server process exits (Render
# restarts, tab closes, etc.) everything is wiped automatically.
# No database, no persistence — a session ends when the server ends.
# -------------------------------------------------------------------

from datetime import datetime

# { session_id: {"name": str, "created_at": datetime} }
sessions: dict = {}

# { session_id: [interview_doc, ...] }
interviews: dict = {}
"""The call text, kept outside the graph.

The graph stores a sentence and a pointer. The full text stays here so the
quote check can compare against the original words.
"""


class TranscriptStore:
    """In-memory files, keyed by call id such as 'acme'."""

    def __init__(self):
        self.files = {}

    def clear(self):
        """Forget every saved call. Used by Reset."""
        self.files = {}

    def save(self, transcript_id, text, meeting_id, opportunity_id, account_id, label):
        """Store one call. Saving the same id again replaces the previous text."""
        self.files[transcript_id] = {
            "id": transcript_id,
            "text": text,
            "meeting_id": meeting_id,
            "opportunity_id": opportunity_id,
            "account_id": account_id,
            "label": label,
        }
        return self.files[transcript_id]

    def get(self, transcript_id):
        """Return one saved call, or None."""
        return self.files.get(transcript_id)

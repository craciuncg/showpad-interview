"""The only record types and link types this demo is allowed to store.

This is the ontology. Every other file must use these names. A new kind of
record or link is rejected by the graph so the model cannot invent one.
"""

# Labels for worries and for what happened next on a finished sale.
# "other" is the bucket for wording we cannot map. It is not counted.
CONCEPT_TYPES = ("timing", "price", "security", "other")
ACTION_TYPES = ("small_start", "full_switch", "other")

# The similar-sale line stays hidden until at least this many finished sales exist.
MINIMUM_SIMILAR_DEALS = 3

# Things in the graph. CRM rows, shared lists, and claims from a call.
NODE_TYPES = (
    "account",             # a buyer company, from the CRM
    "contact",             # a known person at that company, from the CRM
    "opportunity",         # one possible sale, from the CRM
    "competitor",          # a known other vendor, from our catalog
    "concept_type",        # a shared label such as timing
    "action_type",         # a shared label such as small_start
    "meeting",             # one call, linked by the calendar
    "span",                # one exact sentence from that call
    "person_mention",      # a person the call named
    "competitor_mention",  # a vendor the call named
    "concept_mention",     # a worry the call named
    "rollup",              # the count of similar finished sales
)

# Meanings of the links between those things.
LINK_TYPES = (
    "BELONGS_TO",     # person works at company
    "WITH",           # sale is with company
    "INVOLVED_IN",    # person is part of this sale; the role sits on this link
    "ABOUT",          # call is about this sale
    "HAS_SPAN",       # call contains this sentence
    "SUPPORTED_BY",   # claim is backed by this sentence
    "RESOLVES_TO",    # spoken name matches this known record
    "CLASSIFIED_AS",  # claim uses this shared label
    "RAISED",         # sale has this worry
    "FACED",          # sale is compared with this vendor
    "TOOK_ACTION",    # finished sale was followed by this action
)

"""Domain definition modules.

Phase 2 is a **single-domain** product: Marketing only. The catalog machinery is
unchanged from the multi-domain build, so adding a domain later is still just a
module plus an entry in ``DOMAIN_MODULES`` — but the product, the router and the
UI are all built around one domain and its five agents.
"""

from app.agents.definitions import marketing

#: Display order. One entry by design; the catalog supports more.
DOMAIN_MODULES = (marketing,)

#: The domain this build is about. Used for defaults instead of hardcoding the
#: string in the router, API and scripts.
PRIMARY_DOMAIN = marketing.DOMAIN.key

__all__ = ["DOMAIN_MODULES", "PRIMARY_DOMAIN", "marketing"]

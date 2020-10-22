from typing import Dict
from django.conf import settings


def google_analytics(request) -> Dict[str, str]:
    ga_prop_id = getattr(settings, "GOOGLE_ANALYTICS_MEASUREMENT_ID", False)
    if not settings.DEBUG and ga_prop_id:
        return {
            "GOOGLE_ANALYTICS_MEASUREMENT_ID": ga_prop_id,
        }
    return {}

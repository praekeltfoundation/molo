"""
Current molo implementation depends on wagtail v1.4.5.
Later versions of wagtail have moved some of the API endpoints
to other locations.

e.g. the ImagesEndPoint is now at...
wagtail.wagtailimages.api.v2.endpoints
"""

from wagtail.api.v2.endpoints import ImagesAPIEndpoint

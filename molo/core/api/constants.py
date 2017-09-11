from collections import namedtuple

# constants for importer log
ACTION = "ACTION"
SUCCESS = "SUCCESS"
ERROR = "ERROR"
WARNING = "WARNING"

CONTENT_TYPES = [
    ("core.ArticlePage", "Article"),
    ("core.SectionPage", "Section"),
]

ENDPOINTS = [
    ("page", "api/v1/pages")
]

SESSION_VARS = namedtuple(
    "SESSION_VARS",
    ["first", "second", ]
)

ARTICLE_SESSION_VARS = SESSION_VARS(
    first=("url", "article_content_type"),
    second="article_parent_page_id"
)

SECTION_SESSION_VARS = SESSION_VARS(
    first=("url", "section_content_type"),
    second="section_parent_page_id"
)

API_PAGES_ENDPOINT = "/api/v2/pages/"
API_IMAGES_ENDPOINT = "/api/v2/images/"

KEYS_TO_EXCLUDE = ["id", "meta", ]

# Form error messages
MAIN_IMPORT_FORM_MESSAGES = {
    "connection_error": "Please enter a valid URL.",
    "bad_request": "Please try again later.",
}

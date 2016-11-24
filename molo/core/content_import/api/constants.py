from collections import namedtuple

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
    first=("url", "content_type"),
    second="parent_page_id"
)

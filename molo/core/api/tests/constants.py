from molo.core.tests.constants import TEST_IMAGE_HASH

AVAILABLE_ARTICLES = {
    "meta": {
        "total_count": 3
    },
    "items": [
        {
            "id": 10,
            "meta": {
                "type": "core.ArticlePage",
                "detail_url": "http://localhost:8000/api/v2/pages/10/",
            },
            "title": "Test article 1",
            "subtitle": "Sub for test article 1",
            "body": [
                {
                    "type": "paragraph",
                    "value": "Lorem ipsum dolor sit amet"
                },
                {
                    "type": "list",
                    "value": [
                        "Phasellus cursus eros turpis, vitae consequat sem."
                    ]
                },
                {
                    "type": "paragraph",
                    "value": "Lorem ipsum"
                }
            ],
            "tags": [],
            "commenting_state": "O",
            "commenting_open_time": "2016-11-11T06:00:00Z",
            "commenting_close_time": "2016-11-14T06:00:00Z",
            "social_media_title": "test image",
            "social_media_description": "test image description",
            "related_sections": [],
            "featured_in_latest": False,
            "featured_in_latest_start_date": "2016-11-11T06:00:00Z",
            "featured_in_latest_end_date": "2016-11-12T06:00:00Z",
            "featured_in_section": False,
            "featured_in_section_start_date": "2016-11-11T06:00:00Z",
            "featured_in_homepage": False,
            "featured_in_homepage_start_date": "2016-11-11T06:00:00Z",
            "featured_in_homepage_end_date": "2016-11-12T06:00:00Z",
            "feature_as_hero_article": True,
            "promote_date": "2016-11-11T06:00:00Z",
            "demote_date": "2016-11-14T06:00:00Z",
            "metadata_tags": [],
            "latest_revision_created_at": "2016-10-07T12:04:27.316423Z",
            "image": {
                "id": 1,
                "meta": {
                    "type": "wagtailimages.Image",
                    "detail_url": "http://localhost/api/v2/images/13/"
                }
            }
        },
        {
            "id": 11,
            "meta": {
                "type": "core.ArticlePage",
                "detail_url": "http://localhost:8000/api/v2/pages/11/",
            },
            "title": "Test article 2",
            "subtitle": "Sub for test article 2",
            "body": [
                {
                    "type": "paragraph",
                    "value": "Lorem ipsum dolor sit amet."
                },
                {
                    "type": "list",
                    "value": [
                        "Phasellus cursus eros turpis, vitae consequat sem "
                        "dapibus at. Sed fermentum mauris vitae fringilla "
                        "tristique. In hac habitasse platea dictumst."
                    ]
                },
                {
                    "type": "paragraph",
                    "value": "Lorem ipsum"
                }
            ],
            "tags": [
                "Another",
                "Test"
            ],
            "commenting_state": "O",
            "commenting_open_time": "2016-12-23T06:00:00Z",
            "commenting_close_time": "2016-12-26T06:00:00Z",
            "social_media_title": "test image",
            "social_media_description": "test image description",
            "related_sections": [
                {
                    "id": 1,
                    "meta": {
                        "type": "core.ArticlePageRelatedSections"
                    }
                }
            ],
            "featured_in_latest": False,
            "featured_in_latest_start_date": "2016-12-23T06:00:00Z",
            "featured_in_latest_end_date": "2016-12-24T06:00:00Z",
            "featured_in_section": False,
            "featured_in_section_start_date": "2016-12-23T06:00:00Z",
            "featured_in_homepage": False,
            "featured_in_homepage_start_date": "2016-12-20T06:00:00Z",
            "featured_in_homepage_end_date": "2016-12-21T06:00:00Z",
            "feature_as_hero_article": True,
            "promote_date": "2016-12-23T06:00:00Z",
            "demote_date": "2016-12-26T06:00:00Z",
            "metadata_tags": [],
            "latest_revision_created_at": "2016-11-09T10:17:45.352864Z",
            "image": {
                "id": 1,
                "meta": {
                    "type": "wagtailimages.Image",
                    "detail_url": "http://localhost/api/v2/images/17/"
                }
            }
        },
        {
            "id": 12,
            "meta": {
                "type": "core.ArticlePage",
                "detail_url": "http://localhost:8000/api/v2/pages/12/",
            },
            "title": "Test article 3",
            "subtitle": "Sub for test article 3",
            "body": [
                {
                    "type": "paragraph",
                    "value": "Lorem ipsum dolor sit amet."
                },
                {
                    "type": "list",
                    "value": [
                        "Phasellus cursus eros turpis, vitae consequat sem "
                        "dapibus at. Sed fermentum mauris vitae fringilla "
                        "tristique. In hac habitasse platea dictumst."
                    ]
                },
                {
                    "type": "paragraph",
                    "value": "Lorem ipsum"
                }
            ],
            "tags": [],
            "commenting_state": "O",
            "commenting_open_time": "2017-01-25T06:00:00Z",
            "commenting_close_time": "2017-01-27T06:00:00Z",
            "social_media_title": "test image",
            "social_media_description": "test image description",
            "related_sections": [],
            "featured_in_latest": False,
            "featured_in_latest_start_date": "2016-12-23T06:00:00Z",
            "featured_in_latest_end_date": "2016-12-24T06:00:00Z",
            "featured_in_section": False,
            "featured_in_section_start_date": "2016-12-23T06:00:00Z",
            "featured_in_homepage": False,
            "featured_in_homepage_start_date": "2016-12-23T06:00:00Z",
            "featured_in_homepage_end_date": "2016-12-26T06:00:00Z",
            "feature_as_hero_article": True,
            "promote_date": "2017-01-25T06:00:00Z",
            "demote_date": "2017-01-27T06:00:00Z",
            "metadata_tags": [],
            "latest_revision_created_at": "2016-10-10T11:04:36.153490Z",
            "image": {
                "id": 1,
                "meta": {
                    "type": "wagtailimages.Image",
                    "detail_url": "http://localhost/api/v2/images/60/"
                }
            }
        },
    ]
}

RELATED_IMAGE = {
    "id": 1,
    "meta": {
        "type": "wagtailimages.Image",
        "detail_url": "http://localhost/api/v2/images/1/",
        "tags": []
    },
    "title": "Image",
    "width": 480,
    "height": 480,
    "file": "http://localhost:8000/media/original_images/test.png"
}

AVAILABLE_SECTIONS = {
    "meta": {
        "total_count": 3
    },
    "items": [
        {
            "id": 2,
            "meta": {
                "type": "core.SectionPage",
                "detail_url": "http://localhost:8000/api/v2/pages/28/",
                "html_url": "http://localhost/sections/wellbeing/"
                            "taking-care-yourself/"
            },
            "title": "Taking care of yourself",
            "description": "",
            "image": {
                "id": 1,
                "meta": {
                    "type": "wagtailimages.Image",
                    "detail_url": "http://localhost:8000/api/v2/images/1/"
                }
            },
            "extra_style_hints": "",
            "commenting_state": "D",
            "commenting_open_time": "2017-01-25T06:00:00Z",
            "commenting_close_time": "2017-01-26T06:00:00Z",
            "time": [],
            "monday_rotation": False,
            "tuesday_rotation": False,
            "wednesday_rotation": False,
            "thursday_rotation": False,
            "friday_rotation": False,
            "saturday_rotation": False,
            "sunday_rotation": False,
            "content_rotation_start_date": "2017-01-25T06:00:00Z",
            "content_rotation_end_date": "2017-01-26T06:00:00Z",
            "latest_revision_created_at": "2016-10-04T10:23:59.504526Z"
        },
        {
            "id": 3,
            "meta": {
                "type": "core.SectionPage",
                "detail_url": "http://localhost:8000/api/v2/pages/3/",
            },
            "title": "Stress management",
            "description": "",
            "image": {
                "id": 1,
                "meta": {
                    "type": "wagtailimages.Image",
                    "detail_url": "http://localhost:8000/api/v2/images/1/"
                }
            },
            "extra_style_hints": "",
            "commenting_state": "D",
            "commenting_open_time": "2017-01-25T06:00:00Z",
            "commenting_close_time": "2017-01-26T06:00:00Z",
            "time": [],
            "monday_rotation": False,
            "tuesday_rotation": False,
            "wednesday_rotation": False,
            "thursday_rotation": False,
            "friday_rotation": False,
            "saturday_rotation": False,
            "sunday_rotation": False,
            "content_rotation_start_date": "2017-01-25T06:00:00Z",
            "content_rotation_end_date": "2017-01-26T06:00:00Z",
            "latest_revision_created_at": "2016-10-04T10:24:05.826271Z"
        },
        {
            "id": 4,
            "meta": {
                "type": "core.SectionPage",
                "detail_url": "http://localhost:8000/api/v2/pages/4/",
            },
            "title": "Breastfeeding",
            "description": "",
            "image": {
                "id": 1,
                "meta": {
                    "type": "wagtailimages.Image",
                    "detail_url": "http://localhost:8000/api/v2/images/1/"
                }
            },
            "extra_style_hints": "",
            "commenting_state": "D",
            "commenting_open_time": "2017-01-25T06:00:00Z",
            "commenting_close_time": "2017-01-26T06:00:00Z",
            "time": [],
            "monday_rotation": False,
            "tuesday_rotation": False,
            "wednesday_rotation": False,
            "thursday_rotation": False,
            "friday_rotation": False,
            "saturday_rotation": False,
            "sunday_rotation": False,
            "content_rotation_start_date": "2017-01-25T06:00:00Z",
            "content_rotation_end_date": "2017-01-26T06:00:00Z",
            "latest_revision_created_at": "2016-10-04T10:24:21.246246Z"
        },
    ]
}

AVAILABLE_SECTION_CHILDREN = {
    "meta": {
        "total_count": 2
    },
    "items": [
        {
            "id": 11,
            "meta": {
                "type": "core.ArticlePage",
                "detail_url": "http://localhost:8000/api/v2/pages/11/",
            },
            "title": "Test article 11"
        },
        {
            "id": 3,
            "meta": {
                "type": "core.SectionPage",
                "detail_url": "http://localhost:8000/api/v2/pages/3/",
            },
            "title": "Test section 3"
        },
    ]
}

LANGUAGE_LIST_RESPONSE = {
    "meta": {
        "total_count": 2
    },
    "items": [
        {
            "id": 1,
            "meta": {
                "type": "core.SiteLanguage",
                "detail_url": "http://localhost:8000/api/v2/languages/1/"
            }
        },
        {
            "id": 2,
            "meta": {
                "type": "core.SiteLanguage",
                "detail_url": "http://localhost:8000/api/v2/languages/2/"
            }
        }
    ]
}

LANGUAGE_RESPONSE_1 = {
    "id": 1,
    "meta": {
        "type": "core.SiteLanguage",
        "detail_url": "http://localhost:8000/api/v2/languages/1/"
    },
    "locale": "en",
    "is_main_language": True,
    "is_active": True
}

LANGUAGE_RESPONSE_2 = {
    "id": 2,
    "meta": {
        "type": "core.SiteLanguage",
        "detail_url": "http://localhost:8000/api/v2/languages/2/"
    },
    "locale": "fr",
    "is_main_language": False,
    "is_active": True
}

ARTICLE_PAGE_RESPONSE = {
    "id": 9999,
    "meta": {
        "type": "core.ArticlePage",
        "detail_url": "http://localhost:8000/api/v2/pages/12/",
        "html_url": "http://localhost:8000/sections/test-section/article-1/",
        "slug": "article-1",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-07-07T09:48:40.807381Z",
        "parent": {
            "id": 11,
            "meta": {
                "type": "core.SectionPage",
                "detail_url": "http://localhost:8000/api/v2/pages/11/",
                "html_url": "http://localhost:8000/sections/test-section/"
            },
            "title": "Test Section"
        },
        "children": None,
        "translations": [
            {
                "locale": "fr",
                "id": 13
            }
        ],
        "main_language_children": None
    },
    "title": "Article 1",
    "subtitle": "Subtitle for article 1",
    "body": [
        {
            "type": "paragraph",
            "value": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
                "sed do eiusmod tempor incididunt ut labore et dolore magna"
                " aliqua. Ut enim ad minim veniam, quis nostrud exercitation"
                " ullamco laboris nisi ut aliquip ex ea commodo consequat."
                " Duis aute irure dolor in reprehenderit in voluptate velit"
                " esse cillum dolore eu fugiat Nonea pariatur. Excepteur sint"
                " occaecat cupidatat non proident, sunt in culpa qui officia "
                "deserunt mollit anim id est laborum.")
        }
    ],
    "tags": [
        "tag1",
        "tag2",
        "tag3"
    ],
    "commenting_state": "D",
    "commenting_open_time": "2017-07-05T19:23:00Z",
    "commenting_close_time": "2016-09-29T20:00:00Z",
    "social_media_title": "Social Media",
    "social_media_description": "social_media_description",
    "social_media_image": {
        "id": 2,
        "meta": {
            "type": "wagtailimages.Image",
            "detail_url": "http://localhost:8000/api/v2/images/2/"
        },
        "title": "car"
    },
    "related_sections": [
        {
            "id": 1,
            "meta": {
                "type": "core.ArticlePageRelatedSections"
            },
            "section": {
                "id": 23,
                "meta": {
                    "type": "core.SectionPage",
                    "detail_url": "http://localhost:8000/api/v2/pages/23/"
                },
                "title": "Another Section"
            }
        },
        {
            "id": 2,
            "meta": {
                "type": "core.ArticlePageRelatedSections"
            },
            "section": {
                "id": 26,
                "meta": {
                    "type": "core.SectionPage",
                    "detail_url": "http://localhost:8000/api/v2/pages/26/"
                },
                "title": "Sub Section Test"
            }
        }
    ],
    "featured_in_latest": False,
    "featured_in_latest_start_date": "2017-07-16T18:17:04.642291Z",
    "featured_in_latest_end_date": "2017-07-16T18:17:04.642291Z",
    "featured_in_section": False,
    "featured_in_section_start_date": "2017-07-16T18:17:04.642291Z",
    "featured_in_section_end_date": "2017-07-16T18:17:04.642291Z",
    "featured_in_homepage": True,
    "featured_in_homepage_start_date": "2017-07-16T18:17:04.642291Z",
    "featured_in_homepage_end_date": "2017-07-16T18:17:04.642291Z",
    "feature_as_hero_article": False,
    "promote_date": "2017-07-16T18:17:04.642291Z",
    "demote_date": "2018-07-16T18:17:04.642291Z",
    "metadata_tags": [
        "metadata_tag1",
        "metadata_tag2"
    ],
    "latest_revision_created_at": "2017-07-16T18:17:04.642291Z",
    "image": {
        "id": 1,
        "meta": {
            "type": "wagtailimages.Image",
            "detail_url": "http://localhost:8000/api/v2/images/1/"
        },
        "title": "Mountain"
    },
    "nav_tags": [
        {
            "id": 1,
            "meta": {
                "type": "core.ArticlePageTags"
            },
            "tag": {
                "id": 35,
                "meta": {
                    "type": "core.Tag",
                    "detail_url": "http://localhost:8000/api/v2/pages/35/"
                },
                "title": "NAV TAG 1"
            }
        }
    ],
    "recommended_articles": [
        {
            "id": 1,
            "meta": {
                "type": "core.ArticlePageRecommendedSections"
            },
            "recommended_article": {
                "id": 27,
                "meta": {
                    "type": "core.ArticlePage",
                    "detail_url": "http://localhost:8000/api/v2/pages/27/"
                },
                "title": "Article that is nested"
            }
        },
        {
            "id": 2,
            "meta": {
                "type": "core.ArticlePageRecommendedSections"
            },
            "recommended_article": {
                "id": 22,
                "meta": {
                    "type": "core.ArticlePage",
                    "detail_url": "http://localhost:8000/api/v2/pages/22/"
                },
                "title": "Article to Import 1"
            }
        }
    ],
    "go_live_at": "2017-08-01T13:23:00Z",
    "expire_at": "2017-08-31T13:23:00Z",
    "expired": False,
}

ARTICLE_PAGE_RESPONSE_STREAM_FIELDS = {
    "id": 92,
    "meta": {
        "type": "core.ArticlePage",
        "detail_url": "http://localhost:9000/api/v2/pages/92/",
        "html_url": "http://localhost:9000/sections/test-section/article-all-stream-fields/",  # noqa
        "slug": "article-all-stream-fields",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-08-23T08:56:14.263738Z",
        "parent": {
            "id": 11,
            "meta": {
                "type": "core.SectionPage",
                "detail_url": "http://localhost:9000/api/v2/pages/11/",
                "html_url": "http://localhost:9000/sections/test-section/"
            },
            "title": "Test Section"
        },
        "children": None,
        "translations": [],
        "main_language_children": None
    },
    "title": "ARTICLE WITH ALL THE STREAM FIELDS",
    "subtitle": "",
    "body": [
        {
            "type": "heading",
            "value": "test heading"
        },
        {
            "type": "paragraph",
            "value": "test paragraph"
        },
        {
            "type": "image",
            "value": 297
        },
        {
            "type": "list",
            "value": [
                "list item 1",
                "list item 2",
                "list item 3"
            ]
        },
        {
            "type": "numbered_list",
            "value": [
                "numbered list 1",
                "numbered list 2",
                "numbered list 3"
            ]
        },
        {
            "type": "page",
            "value": 48
        }
    ],
    "tags": [],
    "commenting_state": None,
    "commenting_open_time": None,
    "commenting_close_time": None,
    "social_media_title": "",
    "social_media_description": "",
    "social_media_image": None,
    "related_sections": [],
    "featured_in_latest": False,
    "featured_in_latest_start_date": None,
    "featured_in_latest_end_date": None,
    "featured_in_section": False,
    "featured_in_section_start_date": None,
    "featured_in_section_end_date": None,
    "featured_in_homepage": False,
    "featured_in_homepage_start_date": None,
    "featured_in_homepage_end_date": None,
    "feature_as_hero_article": False,
    "promote_date": None,
    "demote_date": None,
    "metadata_tags": [],
    "latest_revision_created_at": "2017-08-23T08:57:13.824364Z",
    "image": None,
    "nav_tags": [],
    "recommended_articles": []
}


SECTION_PAGE_RESPONSE = {
    "id": 11,
    "meta": {
        "type": "core.SectionPage",
        "detail_url": "http://localhost:8000/api/v2/pages/11/",
        "html_url": "http://localhost:8000/sections/test-section/",
        "slug": "test-section",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-07-07T09:47:34.122769Z",
        "parent": {
            "id": 6,
            "meta": {
                "type": "core.SectionIndexPage",
                "detail_url": "http://localhost:8000/api/v2/pages/6/",
                "html_url": "http://localhost:8000/sections/"
            },
            "title": "Sections"
        },
        "children": {
            "items": [
                12,
                13,
                22,
                26,
                34
            ]
        },
        "translations": [
            {
                "locale": "ve",
                "id": 24
            },
            {
                "locale": "fr",
                "id": 25
            }
        ],
        "main_language_children": [
            12,
            22,
            26,
            34
        ]
    },
    "title": "Test Section",
    "live": True,
    "description": "section description",
    "image": {
        "id": 1,
        "meta": {
            "type": "wagtailimages.Image",
            "detail_url": "http://localhost:8000/api/v2/images/1/"
        },
        "title": "Mountain"
    },
    "extra_style_hints": "blue",
    "commenting_state": "O",
    "commenting_open_time": "2017-07-17T10:00:00Z",
    "commenting_close_time": "2017-08-29T11:07:00Z",
    "time": [
        {
            "type": "time",
            "value": "16:00:00"
        },
        {
            "type": "time",
            "value": "15:00:00"
        }
    ],
    "monday_rotation": True,
    "tuesday_rotation": False,
    "wednesday_rotation": False,
    "thursday_rotation": False,
    "friday_rotation": True,
    "saturday_rotation": False,
    "sunday_rotation": False,
    "content_rotation_start_date": "2017-07-04T13:55:00Z",
    "content_rotation_end_date": "2017-07-17T13:55:00Z",
    "latest_revision_created_at": "2017-07-16T18:04:03.439357Z",
    "section_tags": [
        {
            "id": 1,
            "meta": {
                "type": "core.SectionPageTags"
            },
            "tag": {
                "id": 36,
                "meta": {
                    "type": "core.Tag",
                    "detail_url": "http://localhost:8000/api/v2/pages/36/"
                },
                "title": "NAV TAG 2"
            }
        },
        {
            "id": 2,
            "meta": {
                "type": "core.SectionPageTags"
            },
            "tag": {
                "id": 35,
                "meta": {
                    "type": "core.Tag",
                    "detail_url": "http://localhost:8000/api/v2/pages/35/"
                },
                "title": "NAV TAG 1"
            }
        }
    ],
    "enable_next_section": True,
    "enable_recommended_section": True,
    "go_live_at": "2017-08-09T16:05:00Z",
    "expire_at": "2017-08-26T16:05:00Z",
    "expired": False
}

BANNER_SITE_RESPONSE = {
    "id": 40,
    "meta": {
        "type": "core.BannerPage",
        "detail_url": "http://localhost:8000/api/v2/pages/40/",
        "html_url": "http://localhost:8000/banners/banner-1/",
        "slug": "banner-1",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-07-17T14:04:05.433345Z",
        "parent": {
            "id": 5,
            "meta": {
                "type": "core.BannerIndexPage",
                "detail_url": "http://localhost:8000/api/v2/pages/5/",
                "html_url": "http://localhost:8000/banners/"
            },
            "title": "Banners"
        },
        "children": None,
        "translations": [],
        "main_language_children": None
    },
    "title": "Banner 1",
    "banner": {
        "id": 1,
        "meta": {
            "type": "wagtailimages.Image",
            "detail_url": "http://localhost:8000/api/v2/images/1/"
        },
        "title": "Mountain"
    },
    "banner_link_page": {
        "id": 13,
        "meta": {
            "type": "core.ArticlePage",
            "detail_url": "http://localhost:8000/api/v2/pages/13/"
        },
        "title": "French translation of Article 1"
    },
    "external_link": "https://www.google.co.za/"
}

WAGTAIL_API_LIST_VIEW = {
    "meta": {
        "total_count": 3
    },
    "items": [1, 2, 3]
}

WAGTAIL_API_LIST_VIEW_PAGE_1 = {
    "meta": {
        "total_count": 25
    },
    "items": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
              11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
}

WAGTAIL_API_LIST_VIEW_PAGE_2 = {
    "meta": {
        "total_count": 25
    },
    "items": [21, 22, 23, 24, 25]
}

IMAGE_LIST_RESPONSE = {
    "meta": {
        "total_count": 2
    },
    "items": [
        {
            "id": 97,
            "meta": {
                "type": "wagtailimages.Image",
                "detail_url": "http://localhost:8000/api/v2/images/97/",
                "tags": []
            },
            "title": "GAO_A4qQsiM.jpg"
        },
        {
            "id": 98,
            "meta": {
                "type": "wagtailimages.Image",
                "detail_url": "http://localhost:8000/api/v2/images/98/",
                "tags": []
            },
            "title": "boop.png"
        }
    ]
}

IMAGE_DETAIL_1 = {
    "id": 97,
    "meta": {
        "type": "wagtailimages.Image",
        "detail_url": "http://localhost:8000/api/v2/images/97/",
        "tags": []
    },
    "title": "GAO_A4qQsiM.jpg",
    "width": 640,
    "height": 480,
    "filename": "GAO_A4qQsiM.jpg",
    "file": "http://localhost:8000/media/original_images/GAO_A4qQsiM.jpg",
    "image_url": "/media/images/GAO_A4qQsiM.original.jpg",
    "image_hash": TEST_IMAGE_HASH
}

IMAGE_DETAIL_2 = {
    "id": 98,
    "meta": {
        "type": "wagtailimages.Image",
        "detail_url": "http://localhost:8000/api/v2/images/98/",
        "tags": []
    },
    "title": "uYh_80lp8.png",
    "width": 1080,
    "height": 644,
    "filename": "uYh_80lp8.png",
    "file": "http://localhost:8000/media/original_images/uYh_80lp8.png",
    "image_url": "/media/images/uYh_80lp8.original.jpg",
    "image_hash": '3f7ffffffee00000'
}

IMAGE_DETAIL_1_NO_HASH = {
    "id": 97,
    "meta": {
        "type": "wagtailimages.Image",
        "detail_url": "http://localhost:8000/api/v2/images/97/",
        "tags": []
    },
    "title": "GAO_A4qQsiM.jpg",
    "width": 640,
    "height": 480,
    "filename": "GAO_A4qQsiM.jpg",
    "file": "http://localhost:8000/media/original_images/GAO_A4qQsiM.jpg",
    "image_url": "/media/images/GAO_A4qQsiM.original.jpg",
    "image_hash": None
}

ARTICLE_PAGE_RESPONSE_MAIN_LANG = {
    "id": 12,
    "meta": {
        "type": "core.ArticlePage",
        "detail_url": "http://localhost:8000/api/v2/pages/12/",
        "html_url": "http://localhost:8000/sections/test-section/article-1/",
        "slug": "article-1",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-07-07T09:48:40.807381Z",
        "parent": {
            "id": 11,
            "meta": {
                "type": "core.SectionPage",
                "detail_url": "http://localhost:8000/api/v2/pages/11/",
                "html_url": "http://localhost:8000/sections/test-section/"
            },
            "title": "Test Section"
        },
        "children": None,
        "translations": [
            {
                "locale": "fr",
                "id": 2
            }
        ],
        "main_language_children": None
    },
    "title": "Article 1",
    "subtitle": "Subtitle for article 1",
    "body": [
        {
            "type": "paragraph",
            "value": "Content of Article 1 "
        }
    ],
    "tags": [],
    "commenting_state": None,
    "commenting_open_time": None,
    "commenting_close_time": None,
    "social_media_title": "",
    "social_media_description": "",
    "social_media_image": None,
    "related_sections": [],
    "featured_in_latest": False,
    "featured_in_latest_start_date": None,
    "featured_in_latest_end_date": None,
    "featured_in_section": False,
    "featured_in_section_start_date": None,
    "featured_in_section_end_date": None,
    "featured_in_homepage": False,
    "featured_in_homepage_start_date": None,
    "featured_in_homepage_end_date": None,
    "feature_as_hero_article": False,
    "promote_date": None,
    "demote_date": None,
    "metadata_tags": [],
    "latest_revision_created_at": "2017-07-10T08:52:14.326306Z",
    "image": None,
    "nav_tags": [],
    "recommended_articles": []
}

ARTICLE_PAGE_RESPONSE_FRENCH = {
    "id": 13,
    "meta": {
        "type": "core.ArticlePage",
        "detail_url": "http://localhost:8000/api/v2/pages/13/",
        "html_url": "http://localhost:8000/sections/test-section/french-translation-of-article-1/",  # noqa
        "slug": "french-translation-of-article-1",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-07-10T08:52:14.349610Z",
        "parent": {
            "id": 11,
            "meta": {
                "type": "core.SectionPage",
                "detail_url": "http://localhost:8000/api/v2/pages/11/",
                "html_url": "http://localhost:8000/sections/test-section/"
            },
            "title": "Test Section"
        },
        "children": None,
        "translations": [
            {
                "locale": "en",
                "id": 12
            }
        ],
        "main_language_children": None
    },
    "title": "French translation of Article 1",
    "subtitle": "",
    "body": [
        {
            "type": "paragraph",
            "value": "article 1 content in french"
        }
    ],
    "tags": [],
    "commenting_state": None,
    "commenting_open_time": None,
    "commenting_close_time": None,
    "social_media_title": "",
    "social_media_description": "",
    "social_media_image": None,
    "related_sections": [],
    "featured_in_latest": False,
    "featured_in_latest_start_date": None,
    "featured_in_latest_end_date": None,
    "featured_in_section": False,
    "featured_in_section_start_date": None,
    "featured_in_section_end_date": None,
    "featured_in_homepage": False,
    "featured_in_homepage_start_date": None,
    "featured_in_homepage_end_date": None,
    "feature_as_hero_article": False,
    "promote_date": None,
    "demote_date": None,
    "metadata_tags": [],
    "latest_revision_created_at": "2017-07-10T08:52:14.326306Z",
    "image": None,
    "nav_tags": [],
    "recommended_articles": []
}

BANNER_PAGE_RESPONSE = {
    "id": 40,
    "meta": {
        "type": "core.BannerPage",
        "detail_url": "http://localhost:8000/api/v2/pages/40/",
        "html_url": "http://localhost:8000/banners/banner-1/",
        "slug": "banner-1",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-07-17T14:04:05.433345Z",
        "parent": {
            "id": 5,
            "meta": {
                "type": "core.BannerIndexPage",
                "detail_url": "http://localhost:8000/api/v2/pages/5/",
                "html_url": "http://localhost:8000/banners/"
            },
            "title": "Banners"
        },
        "children": None,
        "translations": [],
        "main_language_children": None
    },
    "title": "Banner 1",
    "banner": {
        "id": 97,
        "meta": {
            "type": "wagtailimages.Image",
            "detail_url": "http://localhost:8000/api/v2/images/97/"
        },
        "title": "GAO_A4qQsiM.jpg"
    },
    "banner_link_page": {
        "id": 13,
        "meta": {
            "type": "core.ArticlePage",
            "detail_url": "http://localhost:8000/api/v2/pages/13/"
        },
        "title": "French translation of Article 1"
    },
    "external_link": "https://www.google.co.za/"
}

TAG_PAGE_RESPONSE = {
    "id": 35,
    "meta": {
        "type": "core.Tag",
        "detail_url": "http://localhost:8000/api/v2/pages/35/",
        "html_url": "http://localhost:8000/tags/nav-tag-1/",
        "slug": "nav-tag-1",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-07-16T17:51:43.179465Z",
        "parent": {
            "id": 8,
            "meta": {
                "type": "core.TagIndexPage",
                "detail_url": "http://localhost:8000/api/v2/pages/8/",
                "html_url": "http://localhost:8000/tags/"
            },
            "title": "Tags"
        },
        "children": None,
        "translations": [],
        "main_language_children": None
    },
    "title": "NAV TAG 1",
    "feature_in_homepage": False,
    "go_live_at": "2017-09-01T16:48:00Z",
    "expire_at": "2017-09-19T16:48:00Z",
    "expired": False
}

SECTION_PAGE_RESPONSE_FRENCH = {
    "id": 25,
    "meta": {
        "type": "core.SectionPage",
        "detail_url": "http://localhost:8000/api/v2/pages/25/",
        "html_url": "http://localhost:8000/sections/french-translation-of-test-section/",  # noqa
        "slug": "french-translation-of-test-section",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-07-13T10:31:18.587366Z",
        "parent": {
            "id": 6,
            "meta": {
                "type": "core.SectionIndexPage",
                "detail_url": "http://localhost:8000/api/v2/pages/6/",
                "html_url": "http://localhost:8000/sections/"
            },
            "title": "Sections"
        },
        "children": None,
        "translations": [
            {
                "locale": "en",
                "id": 11
            },
            {
                "locale": "ve",
                "id": 24
            }
        ],
        "main_language_children": None
    },
    "title": "French translation of Test Section",
    "live": True,
    "description": "",
    "image": None,
    "extra_style_hints": "",
    "commenting_state": None,
    "commenting_open_time": None,
    "commenting_close_time": None,
    "time": [],
    "monday_rotation": False,
    "tuesday_rotation": False,
    "wednesday_rotation": False,
    "thursday_rotation": False,
    "friday_rotation": False,
    "saturday_rotation": False,
    "sunday_rotation": False,
    "content_rotation_start_date": None,
    "content_rotation_end_date": None,
    "section_tags": []
}

TYPE_SECTION_INDEX_PAGE_RESPONSE = {
    "meta": {
        "total_count": 1
    },
    "items": [
        {
            "id": 6,
            "meta": {
                "type": "core.SectionIndexPage",
                "detail_url": "http://localhost:8000/api/v2/pages/6/",
                "html_url": "http://localhost:8000/sections/",
                "slug": "sections",
                "first_published_at": "2017-07-06T14:35:24.673565Z"
            },
            "title": "Sections"
        }
    ]
}

# START
# Integration Test for Recursive Import
# http://localhost:8000/api/v2/pages/6/
SECTION_INDEX_PAGE_RESPONSE = {
    "id": 6,
    "meta": {
        "type": "core.SectionIndexPage",
        "detail_url": "http://localhost:8000/api/v2/pages/6/",
        "html_url": "http://localhost:8000/sections/",
        "slug": "sections",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-07-07T10:48:23.219970Z",
        "parent": {
            "id": 4,
            "meta": {
                "type": "core.Main",
                "detail_url": "http://localhost:8000/api/v2/pages/4/",
                "html_url": "http://localhost:8000/"
            },
            "title": "Main"
        },
        "children": {
            "items": [
                178,
                179,
                180
            ]
        },
        "translations": None,
        "main_language_children": [
            178,
            179
        ]
    },
    "title": "Sections"
}

# First Section Imported
# http://localhost:8000/api/v2/pages/178/
SECTION_RESPONSE_1 = {
    "id": 178,
    "meta": {
        "type": "core.SectionPage",
        "detail_url": "http://localhost:8000/api/v2/pages/178/",
        "html_url": "http://localhost:8000/sections/section-1/",
        "slug": "section-1",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-08-04T10:07:03.947926Z",
        "parent": {
            "id": 6,
            "meta": {
                "type": "core.SectionIndexPage",
                "detail_url": "http://localhost:8000/api/v2/pages/6/",
                "html_url": "http://localhost:8000/sections/"
            },
            "title": "Sections"
        },
        "children": {
            "items": [
                181,
                182,
                183
            ]
        },
        "translations": [
            {
                "locale": "fr",
                "id": 180
            }
        ],
        "main_language_children": [
            181,
            182
        ]
    },
    "title": "Section 1",
    "live": True,
    "description": "Description for Site 1",
    "image": None,
    "extra_style_hints": "",
    "commenting_state": None,
    "commenting_open_time": None,
    "commenting_close_time": None,
    "time": [],
    "monday_rotation": False,
    "tuesday_rotation": False,
    "wednesday_rotation": False,
    "thursday_rotation": False,
    "friday_rotation": False,
    "saturday_rotation": False,
    "sunday_rotation": False,
    "content_rotation_start_date": None,
    "content_rotation_end_date": None,
    "section_tags": []
}

# Translation of Section 1
# http://localhost:8000/api/v2/pages/180/
SECTION_RESPONSE_1_TRANSLATION_1 = {
    "id": 180,
    "meta": {
        "type": "core.SectionPage",
        "detail_url": "http://localhost:8000/api/v2/pages/180/",
        "html_url": "http://localhost:8000/sections/french-translation-of-section-1/",  # noqa
        "slug": "french-translation-of-section-1",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-08-04T10:07:28.164537Z",
        "parent": {
            "id": 6,
            "meta": {
                "type": "core.SectionIndexPage",
                "detail_url": "http://localhost:8000/api/v2/pages/6/",
                "html_url": "http://localhost:8000/sections/"
            },
            "title": "Sections"
        },
        "children": None,
        "translations": [
            {
                "locale": "en",
                "id": 178
            }
        ],
        "main_language_children": None
    },
    "title": "French translation of Section 1",
    "live": True,
    "description": "",
    "image": None,
    "extra_style_hints": "",
    "commenting_state": None,
    "commenting_open_time": None,
    "commenting_close_time": None,
    "time": [],
    "monday_rotation": False,
    "tuesday_rotation": False,
    "wednesday_rotation": False,
    "thursday_rotation": False,
    "friday_rotation": False,
    "saturday_rotation": False,
    "sunday_rotation": False,
    "content_rotation_start_date": None,
    "content_rotation_end_date": None,
    "section_tags": []
}

# Article Page
# http://localhost:8000/api/v2/pages/181/
ARTICLE_RESPONSE_1 = {
    "id": 181,
    "meta": {
        "type": "core.ArticlePage",
        "detail_url": "http://localhost:8000/api/v2/pages/181/",
        "html_url": "http://localhost:8000/sections/section-1/article-1/",
        "slug": "article-1",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-08-04T10:07:58.625958Z",
        "parent": {
            "id": 178,
            "meta": {
                "type": "core.SectionPage",
                "detail_url": "http://localhost:8000/api/v2/pages/178/",
                "html_url": "http://localhost:8000/sections/section-1/"
            },
            "title": "Section 1"
        },
        "children": None,
        "translations": [
            {
                "locale": "fr",
                "id": 183
            }
        ],
        "main_language_children": None
    },
    "title": "Article 1",
    "subtitle": "",
    "body": [],
    "tags": [],
    "commenting_state": None,
    "commenting_open_time": None,
    "commenting_close_time": None,
    "social_media_title": "",
    "social_media_description": "",
    "social_media_image": None,
    "related_sections": [],
    "featured_in_latest": False,
    "featured_in_latest_start_date": None,
    "featured_in_latest_end_date": None,
    "featured_in_section": False,
    "featured_in_section_start_date": None,
    "featured_in_section_end_date": None,
    "featured_in_homepage": False,
    "featured_in_homepage_start_date": None,
    "featured_in_homepage_end_date": None,
    "feature_as_hero_article": False,
    "promote_date": None,
    "demote_date": None,
    "metadata_tags": [],
    "latest_revision_created_at": "2017-08-04T10:07:58.605558Z",
    "image": None,
    "nav_tags": [],
    "recommended_articles": []
}

# http://localhost:8000/api/v2/pages/183/
ARTICLE_RESPONSE_1_TRANSLATION = {
    "id": 183,
    "meta": {
        "type": "core.ArticlePage",
        "detail_url": "http://localhost:8000/api/v2/pages/183/",
        "html_url": "http://localhost:8000/sections/section-1/french-translation-of-article-1-2/",  # noqa
        "slug": "french-translation-of-article-1-2",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-08-04T10:08:14.444885Z",
        "parent": {
            "id": 178,
            "meta": {
                "type": "core.SectionPage",
                "detail_url": "http://localhost:8000/api/v2/pages/178/",
                "html_url": "http://localhost:8000/sections/section-1/"
            },
            "title": "Section 1"
        },
        "children": None,
        "translations": [
            {
                "locale": "en",
                "id": 181
            }
        ],
        "main_language_children": None
    },
    "title": "French translation of Article 1",
    "subtitle": "",
    "body": [],
    "tags": [],
    "commenting_state": None,
    "commenting_open_time": None,
    "commenting_close_time": None,
    "social_media_title": "",
    "social_media_description": "",
    "social_media_image": None,
    "related_sections": [],
    "featured_in_latest": False,
    "featured_in_latest_start_date": None,
    "featured_in_latest_end_date": None,
    "featured_in_section": False,
    "featured_in_section_start_date": None,
    "featured_in_section_end_date": None,
    "featured_in_homepage": False,
    "featured_in_homepage_start_date": None,
    "featured_in_homepage_end_date": None,
    "feature_as_hero_article": False,
    "promote_date": None,
    "demote_date": None,
    "metadata_tags": [],
    "latest_revision_created_at": "2017-08-04T10:08:14.425964Z",
    "image": None,
    "nav_tags": [],
    "recommended_articles": []
}

# http://localhost:8000/api/v2/pages/182/
ARTICLE_RESPONSE_2 = {
    "id": 182,
    "meta": {
        "type": "core.ArticlePage",
        "detail_url": "http://localhost:8000/api/v2/pages/182/",
        "html_url": "http://localhost:8000/sections/section-1/article-2/",
        "slug": "article-2",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-08-04T10:08:08.877299Z",
        "parent": {
            "id": 178,
            "meta": {
                "type": "core.SectionPage",
                "detail_url": "http://localhost:8000/api/v2/pages/178/",
                "html_url": "http://localhost:8000/sections/section-1/"
            },
            "title": "Section 1"
        },
        "children": None,
        "translations": [],
        "main_language_children": None
    },
    "title": "Article 2",
    "subtitle": "",
    "body": [],
    "tags": [],
    "commenting_state": None,
    "commenting_open_time": None,
    "commenting_close_time": None,
    "social_media_title": "",
    "social_media_description": "",
    "social_media_image": None,
    "related_sections": [],
    "featured_in_latest": False,
    "featured_in_latest_start_date": None,
    "featured_in_latest_end_date": None,
    "featured_in_section": False,
    "featured_in_section_start_date": None,
    "featured_in_section_end_date": None,
    "featured_in_homepage": False,
    "featured_in_homepage_start_date": None,
    "featured_in_homepage_end_date": None,
    "feature_as_hero_article": False,
    "promote_date": None,
    "demote_date": None,
    "metadata_tags": [],
    "latest_revision_created_at": "2017-08-04T10:08:08.854104Z",
    "image": None,
    "nav_tags": [],
    "recommended_articles": []
}

# http://localhost:8000/api/v2/pages/179/
SECTION_RESPONSE_2 = {
    "id": 179,
    "meta": {
        "type": "core.SectionPage",
        "detail_url": "http://localhost:8000/api/v2/pages/179/",
        "html_url": "http://localhost:8000/sections/section-2/",
        "slug": "section-2",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-08-04T10:07:14.463717Z",
        "parent": {
            "id": 6,
            "meta": {
                "type": "core.SectionIndexPage",
                "detail_url": "http://localhost:8000/api/v2/pages/6/",
                "html_url": "http://localhost:8000/sections/"
            },
            "title": "Sections"
        },
        "children": {
            "items": [
                184
            ]
        },
        "translations": [],
        "main_language_children": [
            184
        ]
    },
    "title": "Section 2",
    "live": True,
    "description": "Description 2",
    "image": None,
    "extra_style_hints": "",
    "commenting_state": None,
    "commenting_open_time": None,
    "commenting_close_time": None,
    "time": [],
    "monday_rotation": False,
    "tuesday_rotation": False,
    "wednesday_rotation": False,
    "thursday_rotation": False,
    "friday_rotation": False,
    "saturday_rotation": False,
    "sunday_rotation": False,
    "content_rotation_start_date": None,
    "content_rotation_end_date": None,
    "section_tags": []
}

# http://localhost:8000/api/v2/pages/184/
SUB_SECTION_RESPONSE_1 = {
    "id": 184,
    "meta": {
        "type": "core.SectionPage",
        "detail_url": "http://localhost:8000/api/v2/pages/184/",
        "html_url": "http://localhost:8000/sections/section-2/sub-section/",
        "slug": "sub-section",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-08-04T10:08:47.727354Z",
        "parent": {
            "id": 179,
            "meta": {
                "type": "core.SectionPage",
                "detail_url": "http://localhost:8000/api/v2/pages/179/",
                "html_url": "http://localhost:8000/sections/section-2/"
            },
            "title": "Section 2"
        },
        "children": {
            "items": [
                185
            ]
        },
        "translations": [],
        "main_language_children": [
            185
        ]
    },
    "title": "Sub Section",
    "live": True,
    "description": "",
    "image": None,
    "extra_style_hints": "",
    "commenting_state": None,
    "commenting_open_time": None,
    "commenting_close_time": None,
    "time": [],
    "monday_rotation": False,
    "tuesday_rotation": False,
    "wednesday_rotation": False,
    "thursday_rotation": False,
    "friday_rotation": False,
    "saturday_rotation": False,
    "sunday_rotation": False,
    "content_rotation_start_date": None,
    "content_rotation_end_date": None,
    "section_tags": []
}

# http://localhost:8000/api/v2/pages/185/
NESTED_ARTICLE_RESPONSE = {
    "id": 185,
    "meta": {
        "type": "core.ArticlePage",
        "detail_url": "http://localhost:8000/api/v2/pages/185/",
        "html_url": "http://localhost:8000/sections/section-2/sub-section/article-3/",  # noqa
        "slug": "article-3",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-08-04T10:09:01.177880Z",
        "parent": {
            "id": 184,
            "meta": {
                "type": "core.SectionPage",
                "detail_url": "http://localhost:8000/api/v2/pages/184/",
                "html_url": "http://localhost:8000/sections/section-2/sub-section/"  # noqa
            },
            "title": "Sub Section"
        },
        "children": None,
        "translations": [],
        "main_language_children": None
    },
    "title": "Article 3",
    "subtitle": "",
    "body": [],
    "tags": [],
    "commenting_state": None,
    "commenting_open_time": None,
    "commenting_close_time": None,
    "social_media_title": "",
    "social_media_description": "",
    "social_media_image": None,
    "related_sections": [],
    "featured_in_latest": False,
    "featured_in_latest_start_date": None,
    "featured_in_latest_end_date": None,
    "featured_in_section": False,
    "featured_in_section_start_date": None,
    "featured_in_section_end_date": None,
    "featured_in_homepage": False,
    "featured_in_homepage_start_date": None,
    "featured_in_homepage_end_date": None,
    "feature_as_hero_article": False,
    "promote_date": None,
    "demote_date": None,
    "metadata_tags": [],
    "latest_revision_created_at": "2017-08-04T10:09:01.158928Z",
    "image": None,
    "nav_tags": [],
    "recommended_articles": []
}

NESTED_FIELD_NAV_TAG_WITH_NONE = {
    "nav_tags": [
        {
            "id": 10,
            "meta": {
                "type": "core.ArticlePageTags"
            },
            "tag": None
        },
        {
            "id": 11,
            "meta": {
                "type": "core.ArticlePageTags"
            },
            "tag": {
                "id": 28170,
                "meta": {
                    "type": "core.Tag",
                    "detail_url": "http://qa.tuneme.seed.p16n.org/api/v2/pages/28170/"  # noqa
                },
                "title": "18"
            }
        }
    ]
}

ARTICLE_WITH_ONLY_IMAGE_RESPONSE = {
    "id": 93,
    "meta": {
        "type": "core.ArticlePage",
        "detail_url": "http://localhost:9000/api/v2/pages/93/",
        "html_url": "http://localhost:9000/sections/test-section/bare-article/",  # noqa
        "slug": "bare-article",
        "show_in_menus": False,
        "seo_title": "",
        "search_description": "",
        "first_published_at": "2017-08-30T12:45:06.398516Z",
        "parent": {
            "id": 11,
            "meta": {
                "type": "core.SectionPage",
                "detail_url": "http://localhost:9000/api/v2/pages/11/",
                "html_url": "http://localhost:9000/sections/test-section/"
            },
            "title": "Test Section"
        },
        "children": None,
        "translations": [],
        "main_language_children": None
    },
    "title": "Bare Article",
    "subtitle": "",
    "body": [],
    "tags": [],
    "commenting_state": None,
    "commenting_open_time": None,
    "commenting_close_time": None,
    "social_media_title": "",
    "social_media_description": "",
    "social_media_image": None,
    "related_sections": [],
    "featured_in_latest": False,
    "featured_in_latest_start_date": None,
    "featured_in_latest_end_date": None,
    "featured_in_section": False,
    "featured_in_section_start_date": None,
    "featured_in_section_end_date": None,
    "featured_in_homepage": False,
    "featured_in_homepage_start_date": None,
    "featured_in_homepage_end_date": None,
    "feature_as_hero_article": False,
    "promote_date": None,
    "demote_date": None,
    "metadata_tags": [],
    "latest_revision_created_at": "2017-08-30T12:45:06.378020Z",
    "image": {
        "id": 297,
        "meta": {
            "type": "wagtailimages.Image",
            "detail_url": "http://localhost:9000/api/v2/images/297/"
        },
        "title": "and it's more than just attraction."
    },
    "nav_tags": [],
    "recommended_articles": [],
    "go_live_at": None,
    "expire_at": None,
    "expired": False
}

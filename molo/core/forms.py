from django.utils import timezone

from molo.core import constants
from wagtail.wagtailadmin.forms import WagtailAdminPageForm


class ArticlePageForm(WagtailAdminPageForm):

    def clean(self):
        cleaned_data = super(ArticlePageForm, self).clean()

        topic_of_the_day = cleaned_data.get("feature_as_topic_of_the_day")
        promote_date = cleaned_data.get("promote_date")
        demote_date = cleaned_data.get("demote_date")

        # Used to determine if all checks; then comments are enabled
        enable_comments = True

        if topic_of_the_day:
            if not promote_date:
                self.add_error(
                    "promote_date",
                    "Please specify the date and time that you would like "
                    "this article to appear as the Topic of the Day."
                )
                enable_comments = False

            if not demote_date:
                self.add_error(
                    "demote_date",
                    "Please specify the date and time that you would like "
                    "this article to be demoted as the Topic of the Day."
                )
                enable_comments = False

            if promote_date and demote_date:
                if promote_date < timezone.now():
                    self.add_error(
                        "promote_date",
                        "Please select the present date, or a future date."
                    )
                    enable_comments = False

                if demote_date < timezone.now() or demote_date < promote_date:
                    self.add_error(
                        "demote_date",
                        "The article cannot be demoted before it has been "
                        "promoted."
                    )
                    enable_comments = False

                # All date checks met, enable comments
                if enable_comments:
                    cleaned_data["commenting_state"] = \
                        constants.COMMENTING_OPEN

        return cleaned_data

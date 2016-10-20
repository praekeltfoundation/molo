from django.utils import timezone

from wagtail.wagtailadmin.forms import WagtailAdminPageForm


class ArticlePageForm(WagtailAdminPageForm):

    def clean(self):
        cleaned_data = super(ArticlePageForm, self).clean()

        topic_of_the_day = cleaned_data.get("feature_as_topic_of_the_day")
        promote_date = cleaned_data.get("promote_date")
        demote_date = cleaned_data.get("demote_date")

        if topic_of_the_day:
            if not promote_date:
                self.add_error(
                    "promote_date",
                    "Please specify the date and time that you would like "
                    "this article to appear as the Topic of the Day."
                )

            if not demote_date:
                self.add_error(
                    "demote_date",
                    "Please specify the date and time that you would like "
                    "this article to be demoted as the Topic of the Day."
                )

            if promote_date and demote_date:
                if promote_date < timezone.now():
                    self.add_error(
                        "promote_date",
                        "Please select the present date, or a future date."
                    )

                if demote_date < timezone.now() or demote_date < promote_date:
                    self.add_error(
                        "demote_date",
                        "The article cannot be demoted before it has been "
                        "promoted."
                    )

        return cleaned_data

from wagtail.wagtailadmin.forms import WagtailAdminPageForm


class ArticlePageForm(WagtailAdminPageForm):

    def clean(self):
        cleaned_data = super(ArticlePageForm, self).clean()

        topic_of_the_day = cleaned_data["feature_as_topic_of_the_day"]
        promote_date = cleaned_data["promote_date"]
        demote_date = cleaned_data["demote_date"]
        # Error checking for Topic of the Day
        # If the Article has been marked as Topic of the Day,
        # it is also then required to specify when the Article must be
        # promoted.
        if topic_of_the_day:
            if not promote_date:
                self.add_error(
                    "promote_date",
                    "Please specify the date and time that you would like "
                    "this article to appear as the Topic of the Day."
                )
        return cleaned_data

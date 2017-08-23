from rest_framework.filters import BaseFilterBackend


class MainLanguageFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        """
        Returns only pages in the main language for a site
        """
        if 'is_main_language' in request.GET:
            # TODO investigate possible error cases where page
            # does not have language
            return queryset.filter(languages__language__is_main_language=True)
        else:
            return queryset

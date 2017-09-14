Merged CMS
==========

Molo allows you to manage more than one site in a single CMS using wagtail's multi-site functionality.

Sharing a database
------------------

The database is shared between the number of sites you have. It is important to
know this when querying data. One should always make sure the page/s you are querying
for are descendants of the correct Main page.

See wagtail documentation for more on `Multi-Site CMS`_

Copying between sites with multi-language content
-------------------------------------------------

Molo allows you to create content in multiple languages, as well as have sites
in multiple languages. When copying content in language x and y to a site that
has only language x, the content will be copied over as well as language y.
However, language y will be set as inactive as it never existed on the desination
site before the copy.

See help centre docs for more info on copying content and sites
(insert link to helpcentre docs)

.. _`Multi-Site CMS`: https://wagtail.io/blog/multi-site-wagtail/

Copying content with relations to different sites
-------------------------------------------------

An `ArticlePage` has a relation to a `ReactionQuestion`. When copying an article from site one to site two
with a link to a reaction from site one, the article will be copied over to site two.
However, the linked reaction question will still point to the reaction question question in site one.
This is avoided by creating new article reaction question relations after the article has been copied::

    # replace old reaction question with new reaction question
    question_relations = \
        ArticlePageReactionQuestions.objects.filter(page=article)
    for relation in question_relations:
        if relation.reaction_question:
            new_question = ReactionQuestion.objects.descendant_of(
                copied_main).filter(
                    slug=relation.reaction_question.slug).first()
            relation.reaction_question = new_question
            relation.save()

For any new content that has a relation to other content, the same will need to be done.

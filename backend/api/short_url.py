from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from recipes.models import Recipe


def short_url_redirect(request, short_url):
    recipe = get_object_or_404(Recipe, short_url=short_url)
    return HttpResponseRedirect(
        request.build_absolute_uri(f'/recipes/{recipe.id}/'))

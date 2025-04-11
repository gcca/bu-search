from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import GithubRepo


async def SearchPage(request: HttpRequest) -> HttpResponse:
    return render(request, "bum_poc/search.html")


def PartialSearch(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "")
    page = int(request.GET.get("page", 1))
    per_page = int(request.GET.get("per_page", 5))

    query = query.strip()
    if not query:
        return HttpResponse("Empty query")
    query = query.lower()

    qs = GithubRepo.objects.filter(
        Q(full_name__icontains=query)
        | Q(description__icontains=query)
        | Q(readme__icontains=query)
    )

    paginator = Paginator(qs, min(5, per_page))
    page = paginator.get_page(page)

    return render(request, "bum_poc/item.html", {"page": page})

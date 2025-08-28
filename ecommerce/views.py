from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import JsonResponse
from elasticsearch_dsl import Q
from .documents import ProductDocument


def search_products(request):
    """Main search view for products."""
    query = request.GET.get("q", "")
    page = request.GET.get("page", 1)

    if query:
        # Create elasticsearch query
        multi_match_query = Q(
            "multi_match",
            query=query,
            fields=[
                "name^3",  # Boost name field
                "description",  # Standard description field
            ],
            fuzziness="AUTO",  # Handle typos
        )

        response = ProductDocument.search().query(multi_match_query).execute()

        # Prepare results:
        results = []
        for hit in response:
            result = {
                # "id": 0, # TODO: Add ID field in ES
                "name": hit.name,
                "description": hit.description,
                "price": hit.price,
                # "created_at": hit.created_at,
                "score": hit.meta.score,
            }

            # TODO: Add highlights if available

            results.append(result)

        total = response.hits.total.value
    else:
        results = []
        total = 0

    # Pagination
    paginator = Paginator(results, 10)  # 10 results per page
    page_obj = paginator.get_page(page)

    context = {
        "query": query,
        "results": page_obj,
        "total_hits": total,
        "category_filter": "No category",
    }

    return render(request, "ecommerce/search.html", context)


def autocomplete(request):
    """Autocomplete suggestions"""
    query = request.GET.get("q", "")

    if len(query) < 2:
        return JsonResponse({"suggestions": []})


def advanced_search(request):
    pass

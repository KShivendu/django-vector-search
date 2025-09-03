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


# http://localhost:8000/products/autocomplete/?q=descript
# http://localhost:8000/products/autocomplete/?q=product
def autocomplete(request):
    """Autocomplete suggestions"""
    query = request.GET.get("q", "")

    if len(query) < 2:
        return JsonResponse({"suggestions": []})

    # Use completion suggestor
    search = ProductDocument.search()

    # Use suggest API
    search = search.suggest(
        "product_suggest", query, completion={"field": "suggest", "size": 5}
    )

    response = search.execute()

    suggestions = []
    if response.suggest and "product_suggest" in response.suggest:
        for option in response.suggest.product_suggest[0].options:
            suggestions.append(option.text)

    return JsonResponse({"suggestions": suggestions})


# http://localhost:8000/products/advanced-search/?q=product&min_price=20&max_price=40
def advanced_search(request):
    """Advanced search with filters"""
    query = request.GET.get("q", "")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    search = ProductDocument.search()

    queries = []

    # Text search:
    if query:
        queries.append(
            Q(
                "multi_match",
                query=query,
                fields=[
                    "name^3",
                    "description",
                ],
                fuzziness="AUTO",
            )
        )

    # Price range filter:
    if min_price or max_price:
        price_range = {}
        if min_price:
            price_range["gte"] = float(min_price)
        if max_price:
            price_range["lte"] = float(max_price)
        queries.append(Q("range", price=price_range))

    # Combine queries
    if queries:
        combined_query = Q("bool", must=queries)
        search = search.query(combined_query)

    # Add aggregation for faceted search:
    search.aggs.bucket(
        "price_ranges",
        "range",
        field="price",
        ranges=[
            {"to": 50},
            {"from": 50, "to": 100},
            {"from": 100, "to": 200},
            {"from": 200},
        ],
    )

    response = search.execute()

    results = []
    for hit in response:
        result = {
            "name": hit.name,
            "description": hit.description,
            "price": hit.price,
            "score": hit.meta.score,
        }
        results.append(result)

    # Extract aggregation results
    facets = {"price_ranges": response.aggregations.price_ranges.buckets}

    context = {
        "query": query,
        "results": results,
        "facets": facets,
        "total_hits": response.hits.total.value,
    }

    return render(request, "ecommerce/advanced_search.html", context)

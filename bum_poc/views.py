import asyncio
import json
import logging
from typing import Dict, Optional, Set

import httpx
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string


async def SearchPage(request: HttpRequest) -> HttpResponse:
    return render(request, "bum_poc/search.html")


async def PartialSearch(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("query", "")
    page = request.GET.get("page", "1")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.github.com/users/gcca/repos",
            params={"page": page},
        )

        items = response.json()

        item_tasks = []
        item_request_lock = asyncio.Lock()

        async with asyncio.TaskGroup() as tg:
            for item in items:
                item_tasks.append(
                    tg.create_task(ProcessItem(query, item, item_request_lock))
                )

        results = [task.result() for task in item_tasks]

        content = "".join(result for result in results if result)

        return HttpResponse(content)


async def ProcessItem(
    query: str, item: Dict[str, str], item_request_lock: asyncio.Lock
) -> Optional[str]:
    full_name = item["full_name"]

    cached_search_records = cache.get_or_set(f"search:records", "")
    if cached_search_records is not None:
        set_search_records: Set[str] = set(cached_search_records.split(","))
        if full_name in set_search_records:
            cached_search_record = cache.get(f"search:records:{full_name}")
            if cached_search_record is None:
                logging.error(
                    f"Cached search record for {full_name} not found in cache."
                )

                cached_search_records.remove(full_name)
                cache.set(f"search:records", ",".join(cached_search_records))
                cache.delete(f"search:records:{full_name}")
            else:
                try:
                    context = json.loads(cached_search_record)
                    return render_to_string("bum_poc/item.html", context)

                except json.JSONDecodeError:
                    logging.error(
                        f"Failed to decode cached search record for {full_name}."
                    )

                    cached_search_records.remove(full_name)
                    cache.set(
                        f"search:records", ",".join(cached_search_records)
                    )
                    cache.delete(f"search:records:{full_name}")

    description = item["description"]
    html_url = item["html_url"]

    fulltext = f"{full_name} {description} {html_url}"

    if query.lower() not in fulltext.lower():
        return None

    async with item_request_lock:
        await asyncio.sleep(1)
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(
                    f"https://api.github.com/repos/{full_name}/readme",
                    headers={"Accept": "application/vnd.github.html"},
                    follow_redirects=True,
                )

                readme = response.text

            except httpx.RequestError as error:
                logging.error(
                    f"An error (request) occurred while requesting {full_name}: {error}"
                )
                return None

            except httpx.HTTPStatusError as error:
                if error.response.status_code == 404:
                    readme = "No README found"
                else:
                    logging.error(
                        f"An error (status) occurred while requesting {full_name}: {error}"
                    )
                    return None

    context = {
        "full_name": full_name,
        "description": description,
        "html_url": html_url,
        "readme": readme,
    }

    cached_search_records = cache.get_or_set(f"search:records", "")
    if cached_search_records is None:
        cached_search_records = ""
    set_search_records: Set[str] = set(cached_search_records.split(","))
    set_search_records.add(full_name)
    cache.set(f"search:records", ",".join(set_search_records))
    cache.set(f"search:records:{full_name}", json.dumps(context))

    return render_to_string("bum_poc/item.html", context)

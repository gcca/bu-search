import asyncio
from typing import Any, Dict, List

import httpx
from django.core.management.base import BaseCommand

from bum_poc.models import OSMPlace


class Command(BaseCommand):

    async def FetchPlace(
        self, client: httpx.AsyncClient, query: str, lock: asyncio.Lock
    ) -> None:
        try:
            params: Dict[str, Any] = {
                "q": query,
                "format": "jsonv2",
                "addressdetails": 1,
                "extratags": 1,
                "namedetails": 1,
                "limit": 50,
                "countrycodes": "PE",
            }

            data = None

            async with lock:
                res = await client.get(
                    "https://nominatim.openstreetmap.org/search", params=params
                )

                if res.status_code != 200:
                    self.stdout.write(
                        self.style.WARNING(f"No encontrado: {query}")
                    )
                    return

                data = res.json()

            await OSMPlace.objects.abulk_create(
                [OSMPlace(entry=query, data=item) for item in data]
            )

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error en {query}: {error}"))

    def handle(self, *args: Any, **kwargs: Any) -> None:
        _ = args, kwargs
        queries: List[str] = [
            f"{city}, Perú"
            for city in [
                "Lima",
                "Cusco",
                "Arequipa",
                "Trujillo",
                "Chiclayo",
                "Piura",
                "Iquitos",
                "Puno",
                "Huancayo",
                "Tacna",
                "Ica",
                "Chimbote",
                "Huaraz",
                "Ayacucho",
                "Tumbes",
                "Pucallpa",
                "Sullana",
                "Juliaca",
                "Tarapoto",
                "Cajamarca",
            ]
        ]

        async def RunTasks() -> None:
            lock = asyncio.Lock()
            async with httpx.AsyncClient(verify=False) as client:
                async with asyncio.TaskGroup() as tg:
                    for query in queries:
                        tg.create_task(self.FetchPlace(client, query, lock))

        asyncio.run(RunTasks())

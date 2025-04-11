import asyncio
from typing import Any, Dict, List

import httpx
from django.core.management.base import BaseCommand

from bum_poc.models import GithubLake, GithubRepo, GithubUser


class Command(BaseCommand):

    help = "Add GitHub repositories info to the database."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--user",
            type=str,
            help="GitHub username to fetch repositories from.",
        )

    def handle(self, *_, **options) -> None:
        user = options["user"]
        if not user:
            self.stdout.write(
                self.style.ERROR("Please provide a GitHub username.")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"Adding repositories for user: {user}")
        )

        asyncio.run(self.PullUserRepos(user))

    async def PullUserRepos(self, user: str) -> None:
        repo_infos = await self.FetchRepoInfos(user)

        items = [
            {
                "full_name": info["full_name"],
                "description": info["description"],
                "html_url": info["html_url"],
            }
            for info in repo_infos
        ]

        self.stdout.write(
            self.style.SUCCESS(f"Fetched {len(items)} repositories.")
        )

        if not items:
            self.stdout.write(self.style.WARNING("No repositories found."))
            return

        async with asyncio.TaskGroup() as tg:
            for item in items:
                tg.create_task(self.FecthReadme(item))

        github_user, _ = await GithubUser.objects.aget_or_create(name=user)

        github_repos: List[GithubRepo] = [GithubRepo()] * len(items)
        github_lakes: List[GithubLake] = [GithubLake()] * len(items)

        async with asyncio.TaskGroup() as tg:
            for i, item in enumerate(items):
                tg.create_task(
                    self.AddRepos(
                        i, item, github_user, github_repos, github_lakes
                    )
                )

        async with asyncio.TaskGroup() as tg:
            tg.create_task(GithubRepo.objects.abulk_create(github_repos))
            tg.create_task(GithubLake.objects.abulk_create(github_lakes))

    async def AddRepos(
        self,
        i: int,
        item: Dict[str, Any],
        github_user: GithubUser,
        github_repos: List[GithubRepo],
        github_lakes: List[GithubLake],
    ) -> None:
        github_repos[i] = GithubRepo(
            full_name=item["full_name"],
            description=item["description"],
            html_url=item["html_url"],
            readme=item["readme"],
            github_user=github_user,
        )
        github_lakes[i] = GithubLake(data=item)

    async def FecthReadme(self, item: Dict[str, Any]) -> None:
        url = f"https://api.github.com/repos/{item['full_name']}/readme"
        headers = {"Accept": "application/vnd.github.html"}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            item["readme"] = (
                response.text if response.status_code == 200 else "Sin README"
            )

    async def FetchRepoInfos(self, user: str) -> List[Dict[str, Any]]:
        url = f"https://api.github.com/users/{user}/repos"
        repo_infos: List[Dict[str, Any]] = []
        threshold = 6

        while threshold > 0:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)

                if response.status_code == 200:
                    repo_infos.extend(response.json())

                    link = response.headers["Link"]
                    if 'rel="last"' not in link:
                        break

                    url = [
                        nav.split(";")[0][1:-1]
                        for nav in link.split(", ")
                        if 'rel="next"' in nav
                    ][0]
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to fetch repositories for {user}: {response.status_code} {response.text}"
                        )
                    )
                threshold -= 1

        return repo_infos

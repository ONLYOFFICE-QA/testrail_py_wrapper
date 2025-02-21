# -*- coding: utf-8 -*-
import aiohttp
from typing import Optional, Dict, Any

from .api_client import APIClient
from ..auth import Auth

class TestRailAPI:
    def __init__(self) -> None:
        self.testrail_auth = Auth()
        self.base_url = self.testrail_auth.url + '/index.php?/api/v2/'
        self.api_client = APIClient(self.base_url, self.testrail_auth.username, self.testrail_auth.password)

    async def get_run_id_by_name(self, plan_id: int, run_name: str) -> Optional[int]:
        test_plan = await self.get_plan(plan_id)
        if not test_plan or "entries" not in test_plan:
            return None

        for entry in test_plan["entries"]:
            for run in entry.get("runs", []):
                if run["name"] == run_name:
                    return run["id"]

        return None

    async def get_plan(self, plan_id: int) -> Optional[Dict[str, Any]]:
        response = await self.api_client.request("GET", f"get_plan/{plan_id}")
        if response and "id" in response:
            return response
        return None

    async def get_projects(self) -> dict[str, Any]:
        return await self.api_client.request('GET', 'get_projects')

    async def get_project_id_by_name(self, name: str) -> Optional[int]:
        projects = await self.get_projects()
        project = next((p for p in projects if p['name'] == name), None)
        return project['id'] if project else None

    async def get_suites(self, project_id: int) -> dict[str, Any]:
        return await self.api_client.request('GET', f'get_suites/{project_id}')

    async def get_suite_id_by_name(self, project_id: int, suite_name: str) -> Optional[int]:
        suites = await self.get_suites(project_id)
        suite = next((s for s in suites if s['name'] == suite_name), None)
        return suite['id'] if suite else None

    async def get_sections(self, project_id: int, suite_id: int) -> dict[str, Any]:
        return await self.api_client.request('GET', f'get_sections/{project_id}&suite_id={suite_id}')

    async def get_section_id_by_name(self, project_id: int, suite_id: int, section_name: str) -> Optional[int]:
        sections = await self.get_sections(project_id, suite_id)
        section = next((s for s in sections if s['name'] == section_name), None)
        return section['id'] if section else None

    async def get_plans(self, project_id: int) -> dict[str, Any]:
        return await self.api_client.request('GET', f'get_plans/{project_id}')

    async def get_plan_id_by_name(self, project_id: int, plan_name: str) -> Optional[int]:
        plans = await self.get_plans(project_id)
        plan = next((p for p in plans if p['name'] == plan_name), None)
        return plan['id'] if plan else None

    async def get_tests(self, run_id: int) -> dict[str, Any]:
        return await self.api_client.request('GET', f'get_tests/{run_id}')

    async def get_test_id_by_name(self, run_id: int, test_name: str) -> Optional[int]:
        tests = await self.get_tests(run_id)
        test = next((t for t in tests if t['title'] == test_name), None)
        return test['id'] if test else None

    async def create_test_case(self, section_id: int, title: str, description: str) -> Optional[int]:
        new_test_case = await self.api_client.request('POST', f'add_case/{section_id}', {'title': title, 'custom_steps': description})
        return new_test_case.get('id', None)

    async def create_section(self, project_id: int, suite_id: int, section_title: str) -> Dict[str, Any]:
        return await self.api_client.request('POST', 'add_section', {'project_id': project_id, 'suite_id': suite_id, 'name': section_title})

    async def create_suite(self, project_id: int, suite_name: str, description: str = 'Created automatically by script') -> Dict[str, Any]:
        return await self.api_client.request('POST', 'add_suite', {'project_id': project_id, 'name': suite_name, 'description': description})

    async def add_result(self, test_id: int, result: Dict[str, Any]) -> Dict[str, Any]:
        return await self.api_client.request('POST', f'add_result/{test_id}', result)

    async def add_plan(self, project_id: int, plan_name: str, description: str = 'Created automatically by script') -> Optional[int]:
        new_plan = await self.api_client.request('POST', f'add_plan/{project_id}', {'name': plan_name, 'description': description})
        return new_plan.get('id', None)

    async def add_plan_entry(self, plan_id: int, entry_data: Dict[str, Any]) -> Optional[int]:
        new_run = await self.api_client.request('POST', f'add_plan_entry/{plan_id}', entry_data)

        if not new_run or "runs" not in new_run:
            raise ValueError("Failed to add plan entry.")

        return new_run["runs"][0]["id"]

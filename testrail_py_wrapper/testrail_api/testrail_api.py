import aiohttp
import asyncio
import json
from .auth import Auth


class TestRailAPI:
    def __init__(self):
        self.testrail_auth = Auth()
        self.base_url = self.testrail_auth.url + '/index.php?/api/v2/'
        self.user = self.testrail_auth.username
        self.password = self.testrail_auth.password
        self.auth = aiohttp.BasicAuth(self.user, self.password)

    async def _request(self, method, endpoint, data=None):
        async with aiohttp.ClientSession(auth=self.auth) as session:
            url = self.base_url + endpoint
            async with session.request(method, url, json=data) as response:
                return await response.json()

    async def get_projects(self):
        return await self._request('GET', 'get_projects')

    async def get_project_id_by_name(self, name):
        projects = await self.get_projects()
        project = next((p for p in projects if p['name'] == name), None)
        return project['id'] if project else None

    async def get_suites(self, project_id):
        return await self._request('GET', f'get_suites/{project_id}')

    async def get_suite_id_by_name(self, project_id, suite_name):
        suites = await self.get_suites(project_id)
        suite = next((s for s in suites if s['name'] == suite_name), None)
        return suite['id'] if suite else None

    async def get_sections(self, project_id, suite_id):
        return await self._request('GET', f'get_sections/{project_id}&suite_id={suite_id}')

    async def get_section_id_by_name(self, project_id, suite_id, section_name):
        sections = await self.get_sections(project_id, suite_id)
        section = next((s for s in sections if s['name'] == section_name), None)
        return section['id'] if section else None

    async def get_plans(self, project_id):
        return await self._request('GET', f'get_plans/{project_id}')

    async def get_plan_id_by_name(self, project_id, plan_name):
        plans = await self.get_plans(project_id)
        plan = next((p for p in plans if p['name'] == plan_name), None)
        return plan['id'] if plan else None

    async def get_tests(self, run_id):
        return await self._request('GET', f'get_tests/{run_id}')

    async def get_test_id_by_name(self, run_id, test_name):
        tests = await self.get_tests(run_id)
        test = next((t for t in tests if t['title'] == test_name), None)
        return test['id'] if test else None

    async def create_test_case(self, section_id, title, description):
        return await self._request('POST', f'add_case/{section_id}', {'title': title, 'custom_steps': description})

    async def create_section(self, project_id, suite_id, section_title):
        return await self._request('POST', 'add_section', {'project_id': project_id, 'suite_id': suite_id, 'name': section_title})

    async def create_suite(self, project_id, suite_name, description='Created automatically by script'):
        return await self._request('POST', 'add_suite', {'project_id': project_id, 'name': suite_name, 'description': description})

    async def add_result(self, test_id, result):
        return await self._request('POST', f'add_result/{test_id}', result)

    async def add_plan(self, project_id, plan_name, description='Created automatically by script'):
        return await self._request('POST', 'add_plan', {'project_id': project_id, 'name': plan_name, 'description': description})

    async def add_plan_entry(self, plan_id, entry_data):
        return await self._request('POST', f'add_plan_entry/{plan_id}', entry_data)

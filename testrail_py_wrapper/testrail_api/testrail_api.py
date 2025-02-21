# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any, Coroutine

from .api_client import APIClient
from ..auth import Auth

class TestRailAPI:
    def __init__(self) -> None:
        self.testrail_auth = Auth()
        self.base_url = self.testrail_auth.url + '/index.php?/api/v2/'
        self.api_client = APIClient(self.base_url, self.testrail_auth.username, self.testrail_auth.password)

    async def get_run_id_by_name(
            self,
            plan_id: int,
            run_name: str
    ) -> Optional[int]:
        """
        Gets the ID of a test run by name within a Test Plan.

        :param plan_id: The ID of the test plan.
        :param run_name: The name of the test run.
        :return: The ID of the test run or None if not found.
        """
        test_plan = await self.get_plan(plan_id)
        if not test_plan or "entries" not in test_plan:
            return None

        for entry in test_plan["entries"]:
            for run in entry.get("runs", []):
                if run["name"] == run_name:
                    return run["id"]

        return None

    async def get_plan(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """
        Gets a Test Plan by its ID.

        :param plan_id: The ID of the test plan.
        :return: The test plan as a dictionary or None if not found.
        """
        response = await self.api_client.request("GET", f"get_plan/{plan_id}")
        if response and "id" in response:
            return response
        return None

    async def get_projects(self) -> dict[str, Any]:
        """
        Gets all projects.

        :return: List of projects.
        """
        return await self.api_client.request('GET', 'get_projects')

    async def get_project_id_by_name(self, name: str) -> Optional[int]:
        """
        Gets the ID of a project by its name.

        :param name: The name of the project.
        :return: The ID of the project or None if not found.
        """
        projects = await self.get_projects()
        project = next((p for p in projects if p['name'] == name), None)
        return project['id'] if project else None

    async def get_suites(self, project_id: int) -> dict[str, Any]:
        """
        Gets all test suites for a given project ID.

        :param project_id: The ID of the project.
        :return: List of test suites.
        """
        return await self.api_client.request('GET', f'get_suites/{project_id}')

    async def get_suite_id_by_name(
            self,
            project_id: int,
            suite_name: str
    ) -> Optional[int]:
        """
        Gets the ID of a test suite by its name.

        :param project_id: The ID of the project.
        :param suite_name: The name of the test suite.
        :return: The ID of the test suite or None if not found.
        """
        suites = await self.get_suites(project_id)
        suite = next((s for s in suites if s['name'] == suite_name), None)
        return suite['id'] if suite else None

    async def get_sections(
            self,
            project_id: int,
            suite_id: int
    ) -> dict[str, Any]:
        """
        Gets all test sections for a given project and suite ID.

        :param project_id: The ID of the project.
        :param suite_id: The ID of the suite.
        :return: List of test sections.
        """
        return await self.api_client.request('GET', f'get_sections/{project_id}&suite_id={suite_id}')

    async def get_section_id_by_name(
            self,
            project_id: int,
            suite_id: int,
            section_name: str
    ) -> Optional[int]:
        """
        Gets the ID of a test section by its name.

        :param project_id: The ID of the project.
        :param suite_id: The ID of the suite.
        :param section_name: The name of the section.
        :return: The ID of the section or None if not found.
        """
        sections = await self.get_sections(project_id, suite_id)
        section = next((s for s in sections if s['name'] == section_name), None)
        return section['id'] if section else None

    async def get_plans(self, project_id: int) -> dict[str, Any]:
        """
        Gets all test plans for a given project ID.

        :param project_id: The ID of the project.
        :return: List of test plans.
        """
        return await self.api_client.request('GET', f'get_plans/{project_id}')

    async def get_plan_id_by_name(
            self,
            project_id: int,
            plan_name: str
    ) -> Optional[int]:
        """
        Gets the ID of a test plan by its name.

        :param project_id: The ID of the project.
        :param plan_name: The name of the test plan.
        :return: The ID of the test plan or None if not found.
        """
        plans = await self.get_plans(project_id)
        plan = next((p for p in plans if p['name'] == plan_name), None)
        return plan['id'] if plan else None

    async def get_tests(self, run_id: int) -> dict[str, Any]:
        """
        Gets all tests for a given test run ID.

        :param run_id: The ID of the test run.
        :return: List of tests.
        """
        return await self.api_client.request('GET', f'get_tests/{run_id}')

    async def get_test_id_by_name(
            self,
            run_id: int,
            test_name: str
    ) -> Optional[int]:
        """
        Gets the ID of a test by its name.

        :param run_id: The ID of the test run.
        :param test_name: The name of the test.
        :return: The ID of the test or None if not found.
        """
        tests = await self.get_tests(run_id)
        test = next((t for t in tests if t['title'] == test_name), None)
        return test['id'] if test else None

    async def create_test_case(
            self,
            section_id: int,
            title: str,
            description: str
    ) -> Optional[int]:
        """
        Creates a new test case.

        :param section_id: The ID of the section where the test case will be created.
        :param title: The title of the test case.
        :param description: The description or steps for the test case.
        :return: The ID of the new test case or None if not created.
        """

        new_test_case = await self.api_client.request(
            'POST', f'add_case/{section_id}',
            {'title': title, 'custom_steps': description}
        )
        return new_test_case.get('id', None)

    async def create_section(
            self,
            project_id: int,
            suite_id: int,
            section_title: str
    ) -> Optional[int]:
        """
        Creates a new test section.

        :param project_id: The ID of the project.
        :param suite_id: The ID of the suite.
        :param section_title: The title of the section.
        :return: The ID of the new section or None if not created.
        """
        new_section = await self.api_client.request(
            'POST',
            f'add_section/{project_id}',
            {'suite_id': suite_id, 'name': section_title}
        )

        if not new_section or 'id' not in new_section:
            raise ValueError(f'Failed to create section {section_title}')

        return new_section['id']

    async def create_suite(
            self,
            project_id: int,
            suite_name: str,
            description: str = 'Created automatically by script'
    ) -> Optional[int]:
        """
        Creates a new test suite.

        :param project_id: The ID of the project.
        :param suite_name: The name of the suite.
        :param description: The description of the suite.
        :return: The ID of the new suite or None if not created.
        """
        new_suite = await self.api_client.request(
            'POST',
            f'add_suite/{project_id}',
            {'name': suite_name, 'description': description}
        )

        if not new_suite or 'id' not in new_suite:
            raise ValueError(f'Failed to create suite {suite_name}')

        return new_suite['id']

    async def add_result(self, test_id: int, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds a result to a test.

        :param test_id: The ID of the test.
        :param result: The result data to be added.
        :return: Response from the API.
        """
        print(test_id)
        return await self.api_client.request('POST', f'add_result/{test_id}', result)

    async def add_plan(
            self,
            project_id: int,
            plan_name: str,
            description: str = 'Created automatically by script'
    ) -> Optional[int]:
        """
        Adds a new test plan.

        :param project_id: The ID of the project.
        :param plan_name: The name of the test plan.
        :param description: The description of the test plan.
        :return: The ID of the new test plan or None if creation failed.
        """
        new_plan = await self.api_client.request(
            'POST',
            f'add_plan/{project_id}',
            {'name': plan_name, 'description': description}
        )
        return new_plan.get('id', None)

    async def add_plan_entry(
            self,
            plan_id: int,
            entry_data: Dict[str, Any]
    ) -> Optional[int]:
        """
        Adds a new entry to a test plan.

        :param plan_id: The ID of the test plan.
        :param entry_data: The data for the new entry.
        :return: The ID of the new test run or raises an error if it fails.
        """
        print(entry_data)
        new_run = await self.api_client.request(
            'POST',
            f'add_plan_entry/{plan_id}',
            entry_data
        )
        print(new_run)

        if not new_run or "runs" not in new_run:
            raise ValueError("Failed to add plan entry.")

        return new_run["runs"][0]["id"]

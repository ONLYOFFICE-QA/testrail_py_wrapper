# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any

from .api_client import APIClient
from ..auth import Auth

class TestRailAPI:
    __cache = {}

    def __init__(self) -> None:
        self.testrail_auth = Auth()
        self.base_url = self.testrail_auth.url + '/index.php?/api/v2/'
        self.api_client = APIClient(self.base_url, self.testrail_auth.username, self.testrail_auth.password)

    async def get_run_id_by_name(
            self,
            plan_id: int,
            run_name: str,
            no_cache: bool = False
    ) -> Optional[int]:
        """
        Gets the ID of a test run by name within a Test Plan.

        :param plan_id: The ID of the test plan.
        :param run_name: The name of the test run.
        :param no_cache: If True, bypasses cache.
        :return: The ID of the test run or None if not found.
        """
        cache_key = (plan_id, run_name)

        if not no_cache and cache_key in self.__cache:
            return self.__cache[cache_key]

        test_plan = await self.get_plan(plan_id, no_cache=no_cache)
        if not test_plan or "entries" not in test_plan:
            return None

        for entry in test_plan["entries"]:
            for run in entry.get("runs", []):
                if run["name"] == run_name:
                    run_id = run["id"]
                    self.__cache[cache_key] = run_id
                    return run_id

        return None

    async def get_plan(self, plan_id: int, no_cache: bool = False) -> Optional[Dict[str, Any]]:
        """
        Gets a Test Plan by its ID.

        :param plan_id: The ID of the test plan.
        :param no_cache: If True, bypasses cache.
        :return: The test plan as a dictionary or None if not found.
        """
        response = await self.api_client.request("GET", f"get_plan/{plan_id}", no_cache=no_cache)
        if response and "id" in response:
            return response
        return None

    async def get_projects(self, no_cache: bool = False) -> dict[str, Any]:
        """
        Gets all projects.

        :param no_cache: If True, bypasses cache.
        :return: List of projects.
        """
        return await self.api_client.request('GET', 'get_projects', no_cache=no_cache)

    async def get_project_id_by_name(self, name: str, no_cache: bool = False) -> Optional[int]:
        """
        Gets the ID of a project by its name.

        :param name: The name of the project.
        :param no_cache: If True, bypasses cache.
        :return: The ID of the project or None if not found.
        """
        if not no_cache and name in self.__cache:
            return self.__cache[name]

        projects = await self.get_projects(no_cache=no_cache)

        if not projects:
            return None

        project = next((p for p in projects if p and p.get('name') == name), None)
        project_id = project.get('id', None) if isinstance(project, dict) else None

        if project_id is not None:
            self.__cache[name] = project_id

        return project_id


    async def get_suites(self, project_id: int, no_cache: bool = False) -> dict[str, Any]:
        """
        Gets all test suites for a given project ID.

        :param project_id: The ID of the project.
        :param no_cache: If True, bypasses cache.
        :return: List of test suites.
        """
        return await self.api_client.request('GET', f'get_suites/{project_id}', no_cache=no_cache)

    async def get_suite_id_by_name(
            self,
            project_id: int,
            suite_name: str,
            no_cache: bool = False
    ) -> Optional[int]:
        """
        Gets the ID of a test suite by its name.

        :param project_id: The ID of the project.
        :param suite_name: The name of the test suite.
        :param no_cache: If True, bypasses cache.
        :return: The ID of the test suite or None if not found.
        """
        cache_key = (project_id, suite_name)

        if not no_cache and cache_key in self.__cache:
            return self.__cache[cache_key]

        suites = await self.get_suites(project_id, no_cache=no_cache)

        if not suites:
            return None
        
        suite = next((s for s in suites if s and s.get('name') == suite_name), None)
        suite_id = suite.get('id') if isinstance(suite, dict) else None

        if suite_id is not None:
            self.__cache[cache_key] = suite_id

        return suite_id

    async def get_sections(
            self,
            project_id: int,
            suite_id: int,
            no_cache: bool = False
    ) -> dict[str, Any]:
        """
        Gets all test sections for a given project and suite ID.

        :param project_id: The ID of the project.
        :param suite_id: The ID of the suite.
        :param no_cache: If True, bypasses cache.
        :return: List of test sections.
        """
        return await self.api_client.request(
            'GET',
            f'get_sections/{project_id}&suite_id={suite_id}',
            no_cache=no_cache
        )

    async def get_section_id_by_name(
            self,
            project_id: int,
            suite_id: int,
            section_name: str,
            no_cache: bool = False
    ) -> Optional[int]:
        """
        Gets the ID of a test section by its name.

        :param project_id: The ID of the project.
        :param suite_id: The ID of the suite.
        :param section_name: The name of the section.
        :param no_cache: If True, bypasses cache.
        :return: The ID of the section or None if not found.
        """
        cache_key = (project_id, suite_id, section_name)

        if not no_cache and cache_key in self.__cache:
            return self.__cache[cache_key]

        sections = await self.get_sections(project_id, suite_id, no_cache=no_cache)

        if not sections:
            return None

        section = next((s for s in sections if s and s.get('name') == section_name), None)
        section_id = section.get('id') if isinstance(section, dict) else None

        if section_id is not None:
            self.__cache[cache_key] = section_id

        return section_id

    async def get_plans(self, project_id: int, no_cache: bool = False) -> dict[str, Any]:
        """
        Gets all test plans for a given project ID.

        :param project_id: The ID of the project.
        :param no_cache: If True, bypasses cache.
        :return: List of test plans.
        """
        return await self.api_client.request('GET', f'get_plans/{project_id}', no_cache=no_cache)

    async def get_plan_id_by_name(
            self,
            project_id: int,
            plan_name: str,
            no_cache: bool = False
    ) -> Optional[int]:
        """
        Gets the ID of a test plan by its name with caching.

        :param project_id: The ID of the project.
        :param plan_name: The name of the test plan.
        :param no_cache: If True, bypasses cache.
        :return: The ID of the test plan or None if not found.
        """
        cache_key = (project_id, plan_name)

        if not no_cache and cache_key in self.__cache:
            return self.__cache[cache_key]

        plans = await self.get_plans(project_id, no_cache=no_cache)

        if not plans:
            return None

        plan = next((p for p in plans if p and p.get('name') == plan_name), None)
        plan_id = plan.get('id') if isinstance(plan, dict) else None

        if plan_id is not None:
            self.__cache[cache_key] = plan_id

        return plan_id

    async def get_tests(
            self,
            run_id: int,
            no_cache: bool = False
    ) -> dict[str, Any]:
        """
        Gets all tests for a given test run ID.

        :param run_id: The ID of the test run.
        :param no_cache: If True, bypasses cache.
        :return: List of tests.
        """
        return await self.api_client.request('GET', f'get_tests/{run_id}', no_cache=no_cache)

    async def get_test_id_by_name(
            self,
            run_id: int,
            test_name: str,
            no_cache: bool = False
    ) -> Optional[int]:
        """
        Gets the ID of a test by its name with caching.

        :param run_id: The ID of the test run.
        :param test_name: The name of the test.
        :param no_cache: If True, bypasses cache.
        :return: The ID of the test or None if not found.
        """
        cache_key = (run_id, test_name)

        if not no_cache and cache_key in self.__cache:
            return self.__cache[cache_key]

        tests = await self.get_tests(run_id, no_cache=no_cache)

        if not tests:
            return None

        test = next((t for t in tests if t and t.get('title') == test_name), None)
        test_id = test.get('id', None) if isinstance(test, dict) else None

        if test_id is not None:
            self.__cache[cache_key] = test_id

        return test_id

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
            {
                'title': title,
                'custom_steps': description
            }
        )
        return new_test_case.get('id', None) if isinstance(new_test_case, dict) else None

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
            print(f'Failed to create section {section_title}')
            return None

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
            print(f'Failed to create suite {suite_name}')
            return None

        return new_suite['id']

    async def add_result(self, test_id: int, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds a result to a test.

        :param test_id: The ID of the test.
        :param result: The result data to be added.
        :return: Response from the API.
        """
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
        return new_plan.get('id', None) if isinstance(new_plan, dict) else None

    async def add_plan_entry(
            self,
            plan_id: int,
            entry_data: Dict[str, Any]
    ) -> Optional[int]:
        """
        Adds a new entry to a test plan.

        :param plan_id: The ID of the test plan.
        :param entry_data: The data for the new entry.
        :return: The ID of the new test run or None if it fails.
        """
        new_run = await self.api_client.request(
            'POST',
            f'add_plan_entry/{plan_id}',
            entry_data
        )

        if not new_run or "runs" not in new_run:
            print("Failed to add plan entry.")
            return None

        return new_run["runs"][0]["id"]

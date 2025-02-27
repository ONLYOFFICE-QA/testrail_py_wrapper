# -*- coding: utf-8 -*-
import logging

from os import getcwd, makedirs
from os.path import join, dirname

from .utils.decorators import singleton
from .testrail_api import TestRailAPI


@singleton
class TestManager:
    """
    A class to manage interactions with the test management system,
    including retrieving project, suite, plan, run, test, and section IDs.
    """

    def __init__(self):
        """
        Initializes the TestManager with an API client instance.
        """
        self.api = TestRailAPI()
        self.log_file = join(getcwd(), "testrail_log", 'test_rail.log')


    async def get_project_id_by_name(self, name: str) -> int | None:
        """
        Gets the project ID by name.

        :param name: The name of the project.
        :return: The project ID or None if not found.
        """
        project_id = await self.api.get_project_id_by_name(name)

        if not project_id:
            raise ValueError(f"❌ Project '{name}' not found.")

        return project_id

    async def get_or_create_suite_id(self, project_id: int, suite_name: str) -> int:
        """
        Gets or creates a Suite ID by name.

        :param project_id: The ID of the project.
        :param suite_name: The name of the suite.
        :return: The suite ID.
        """
        suite_id =(
            await self.api.get_suite_id_by_name(project_id, suite_name) or
            await self.api.create_suite(project_id, suite_name)
        )

        if not suite_id:
            raise ValueError(f"❌ Failed to get or create suite ID for '{suite_name}'")
        
        return suite_id

    async def get_or_create_plan_id(self, project_id: int, plan_name: str) -> int:
        """
        Gets or creates a Plan ID by name.

        :param project_id: The ID of the project.
        :param plan_name: The name of the plan.
        :return: The plan ID.
        """
        plan_id = (
            await self.api.get_plan_id_by_name(project_id, plan_name) or
            await self.api.add_plan(project_id, plan_name)
        )

        if not plan_id:
            raise ValueError(f"❌ Failed to get or create plan ID for '{plan_name}'")
        
        return plan_id

    async def get_or_create_run_id(self, plan_id: int, run_name: str, suite_id: int) -> int:
        """
        Gets or creates a Test Run ID by name.

        :param plan_id: The ID of the plan.
        :param run_name: The name of the run.
        :param suite_id: The ID of the suite.
        :return: The ID of the run.
        """
        run_id = await self.api.get_run_id_by_name(plan_id, run_name)
        if not run_id:
            run_id = await self.api.add_plan_entry(
                plan_id, {
                    "name": run_name,
                    "suite_id": suite_id,
                    "include_all": True,
                    "description": "Created automatically",
                }
            )

            if not run_id:
                raise ValueError(f"❌ Failed to get or create run ID for '{run_name}'")
        
        return run_id

    async def get_or_create_section_id(self, project_id: int, suite_id: int, section_title: str) -> int:
        """
        Gets or creates a Section ID by title.

        :param project_id: The ID of the project.
        :param suite_id: The ID of the suite.
        :param section_title: The title of the section.
        :return: The ID of the section.
        """
        section_id = (
            await self.api.get_section_id_by_name(project_id, suite_id, section_title) or 
            await self.api.create_section(project_id, suite_id, section_title)
        )

        if not section_id:
            raise ValueError(f"❌ Failed to get or create section ID for '{section_title}'")
        
        return section_id

    async def get_or_create_test_id(
            self,
            run_id: int, 
            case_title: str, 
            project_id: int, 
            suite_id: int, 
            section_title: str
        ) -> int:
        """
        Gets or creates a Test ID by title.

        :param run_id: The ID of the run.
        :param case_title: The title of the test case.
        :param project_id: The ID of the project.
        :param suite_id: The ID of the suite.
        :param section_title: The title of the section.
        :return: The ID of the test.
        """
        test_id = await self.api.get_test_id_by_name(run_id, case_title, no_cache=False)
        if not test_id:
            section_id = await self.get_or_create_section_id(project_id, suite_id, section_title)
            if not section_id:
                raise ValueError(f"❌ Failed to get or create section ID for '{section_title}'")

            await self.api.create_test_case(section_id, case_title, case_title)
            test_id = await self.api.get_test_id_by_name(run_id, case_title, no_cache=True)

            if not test_id:
                raise ValueError(f"❌ Failed to get test ID for '{case_title}'")

        return test_id

    async def add_result_to_case(
            self,
            project_name: str,
            plan_name: str,
            suite_name: str,
            case_title: str,
            result: dict,
            section_title: str = "All Test Cases"
    ) -> None:
        """
        Adds a result to a test case.

        :param project_name: The name of the project.
        :param plan_name: The name of the plan.
        :param suite_name: The name of the suite.
        :param case_title: The title of the test case.
        :param result: The result to add.
        :param section_title: The title of the section.
        :return: None
        """
        try:
            project_id = await self.get_project_id_by_name(project_name)
            plan_id = await self.get_or_create_plan_id(project_id, plan_name)
            suite_id = await self.get_or_create_suite_id(project_id, suite_name)
            run_id = await self.get_or_create_run_id(plan_id, suite_name, suite_id)
            test_id = await self.get_or_create_test_id(run_id, case_title, project_id, suite_id, section_title)
            await self.api.add_result(test_id, result)
            print(f"✅ Result added to test '{case_title}'")

        except (ValueError, RuntimeError) as e:
            await self._write_log(str(e))

    async def _write_log(self, message: str) -> None:
        makedirs(dirname(self.log_file), exist_ok=True)
        logging.basicConfig(filename=self.log_file, level=logging.ERROR, format='%(message)s')
        logging.error(f"❌ {message}")

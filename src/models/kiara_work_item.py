import pandas as pd
import math
from typing import Optional
import logging
from src.exceptions.custom_exceptions import AppRefInvalidValueError

log = logging.getLogger(__name__)

class KiaraWorkItem:
    def __init__(self, day=None, date="", description = "", jira_ref: Optional[str] = None, time_spent=None, project: Optional[str] = None, app_ref: Optional[str] = None):
        self.day = day
        self.date = date
        self.description = description
        self.jira_ref = jira_ref
        self.time_spent = time_spent
        self.project = project
        self.app_ref = app_ref

    @property
    def description(self) -> str:
        return self._description

    @property
    def app_ref(self) -> str:
        return self._app_ref
    
    @property
    def jira_ref(self) -> str:
        return self._jira_ref
    
    @property
    def project(self) -> str:
      return self._project

    @app_ref.setter
    def app_ref(self, value: Optional[str]) -> None:
      if pd.isna(value):
        self._app_ref = ""
        log.debug(f"AppRef for '{self.description}'  is NaN, setting to empty string.")
      else:
        try:
            self._app_ref = str(int(value))
            log.debug(f"AppRef for '{self.description}' is '{self._app_ref}'.")
        except ValueError as e:
            raise AppRefInvalidValueError(f"AppRef for '{self.description}' is not an integer: '{value}'.") from e

    @jira_ref.setter
    def jira_ref(self, value: Optional[str]) -> None:
      if pd.isna(value):
        self._jira_ref = ""
        log.debug(f"JiraRef for '{self.description}'  is NaN, setting to empty string.")
      else:
        self._jira_ref = str(value)


    @project.setter
    def project(self, value: Optional[str]) -> None:
      default_project = "CS0126444 - Wonen Cloudzone - dedicated operationeel projectteam"
      if (isinstance(value, float) and math.isnan(value)) or value == "":
        self._project = default_project
        log.debug(f"Project for '{self.description}' is NaN or empty, setting to default project: '{default_project}'")
      else:
        self._project = str(value)

    @description.setter
    def description(self, value: str) -> None:
      self._description = str(value)

    def __repr__(self):
      return (f"KiaraWorkItem(day={self.day}, date={self.date}, description={self.description}, "
          f"jira_ref={self.jira_ref}, time_spent={self.time_spent}, project={self.project}, "
          f"app_ref={self.app_ref})")
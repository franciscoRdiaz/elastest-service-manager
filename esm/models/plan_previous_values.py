# coding: utf-8

from __future__ import absolute_import
from .base_model_ import Model
from datetime import date, datetime
from typing import List, Dict
from ..util import deserialize_model


class PlanPreviousValues(Model):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, plan_id: str=None, service_id: str=None, organization_id: str=None, space_id: str=None):
        """
        PlanPreviousValues - a model defined in Swagger

        :param plan_id: The plan_id of this PlanPreviousValues.
        :type plan_id: str
        :param service_id: The service_id of this PlanPreviousValues.
        :type service_id: str
        :param organization_id: The organization_id of this PlanPreviousValues.
        :type organization_id: str
        :param space_id: The space_id of this PlanPreviousValues.
        :type space_id: str
        """
        self.swagger_types = {
            'plan_id': str,
            'service_id': str,
            'organization_id': str,
            'space_id': str
        }

        self.attribute_map = {
            'plan_id': 'plan_id',
            'service_id': 'service_id',
            'organization_id': 'organization_id',
            'space_id': 'space_id'
        }

        self._plan_id = plan_id
        self._service_id = service_id
        self._organization_id = organization_id
        self._space_id = space_id

    @classmethod
    def from_dict(cls, dikt) -> 'PlanPreviousValues':
        """
        Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The PlanPreviousValues of this PlanPreviousValues.
        :rtype: PlanPreviousValues
        """
        return deserialize_model(dikt, cls)

    @property
    def plan_id(self) -> str:
        """
        Gets the plan_id of this PlanPreviousValues.
        ID of the plan prior to the update.

        :return: The plan_id of this PlanPreviousValues.
        :rtype: str
        """
        return self._plan_id

    @plan_id.setter
    def plan_id(self, plan_id: str):
        """
        Sets the plan_id of this PlanPreviousValues.
        ID of the plan prior to the update.

        :param plan_id: The plan_id of this PlanPreviousValues.
        :type plan_id: str
        """

        self._plan_id = plan_id

    @property
    def service_id(self) -> str:
        """
        Gets the service_id of this PlanPreviousValues.
        ID of the service for the instance.

        :return: The service_id of this PlanPreviousValues.
        :rtype: str
        """
        return self._service_id

    @service_id.setter
    def service_id(self, service_id: str):
        """
        Sets the service_id of this PlanPreviousValues.
        ID of the service for the instance.

        :param service_id: The service_id of this PlanPreviousValues.
        :type service_id: str
        """

        self._service_id = service_id

    @property
    def organization_id(self) -> str:
        """
        Gets the organization_id of this PlanPreviousValues.
        ID of the organization containing the instance.

        :return: The organization_id of this PlanPreviousValues.
        :rtype: str
        """
        return self._organization_id

    @organization_id.setter
    def organization_id(self, organization_id: str):
        """
        Sets the organization_id of this PlanPreviousValues.
        ID of the organization containing the instance.

        :param organization_id: The organization_id of this PlanPreviousValues.
        :type organization_id: str
        """

        self._organization_id = organization_id

    @property
    def space_id(self) -> str:
        """
        Gets the space_id of this PlanPreviousValues.
        ID of the space containing the instance.

        :return: The space_id of this PlanPreviousValues.
        :rtype: str
        """
        return self._space_id

    @space_id.setter
    def space_id(self, space_id: str):
        """
        Sets the space_id of this PlanPreviousValues.
        ID of the space containing the instance.

        :param space_id: The space_id of this PlanPreviousValues.
        :type space_id: str
        """

        self._space_id = space_id


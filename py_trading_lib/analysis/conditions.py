from abc import ABC, abstractmethod
from typing import Literal, TypeAlias, Union, Callable

import pandas as pd

import py_trading_lib.utils.sanity_checks as sanity

operators: TypeAlias = Literal["<", "<=", ">", ">=", "=="]
comparison_types: TypeAlias = Union[float, int, str]

__all__ = ["Condition", "CheckRelation"]


class Condition(ABC):
    @abstractmethod
    def _perform_sanity_checks(self, data: pd.DataFrame) -> None:
        pass

    @abstractmethod
    def is_condition_true(self, data: pd.DataFrame) -> pd.Series:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


class CheckRelation(Condition):
    def __init__(
        self,
        indicator_name: str,
        operator: Literal["<", "<=", ">", ">=", "=="],
        comparison_value: Union[float, int, str],
    ) -> None:
        if isinstance(comparison_value, (float, int)):
            self.relation = _NumericRelation(indicator_name, operator, comparison_value)
        elif isinstance(comparison_value, str):
            self.relation = _StringRelation(indicator_name, operator, comparison_value)

    def is_condition_true(self, data: pd.DataFrame) -> pd.Series:
        self._perform_sanity_checks(data)
        return self.relation.is_condition_true(data)

    def _perform_sanity_checks(self, data: pd.DataFrame) -> None:
        sanity.check_not_empty(data)
        self.relation._perform_sanity_checks(data)

    def get_name(self) -> str:
        return self.relation.get_name()


class _Relation:
    def __init__(
        self,
        indicator_name: str,
        operator: operators,
        comparison_value: comparison_types,
    ) -> None:
        self.indicator_name = indicator_name
        self.operator = operator
        self.comparison_value = comparison_value
        self.check_relation = self.get_operator_func(operator)
        self.condition_name = (
            f"{self.indicator_name}{self.operator}{self.comparison_value}"
        )

    def get_operator_func(self, operator: operators) -> Callable:
        operators = {
            "<": lambda x, y: x < y,
            "<=": lambda x, y: x <= y,
            ">": lambda x, y: x > y,
            ">=": lambda x, y: x >= y,
            "==": lambda x, y: x == y,
        }
        if operator not in operators:
            raise ValueError(f"Invalid relational operator: {operator}")
        return operators[operator]

    def get_name(self):
        return self.condition_name


class _NumericRelation(_Relation, Condition):
    def is_condition_true(self, data: pd.DataFrame) -> pd.Series:
        result: pd.Series = self.check_relation(
            data[self.indicator_name], self.comparison_value
        )
        result.name = self.get_name()
        return result

    def _perform_sanity_checks(self, data: pd.DataFrame) -> None:
        indicator = [self.indicator_name]
        columns = data.columns.tolist()
        sanity.check_is_list1_in_list2(indicator, columns)


class _StringRelation(_Relation, Condition):
    def is_condition_true(self, data: pd.DataFrame) -> pd.Series:
        result: pd.Series = self.check_relation(
            data[self.indicator_name], data[self.comparison_value]
        )
        result.name = self.get_name()
        return result

    def _perform_sanity_checks(self, data: pd.DataFrame) -> None:
        indicators = [self.indicator_name, self.comparison_value]
        columns = data.columns.tolist()
        sanity.check_is_list1_in_list2(indicators, columns)

from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class ISignal(ABC):
    conditions: pd.DataFrame

    @abstractmethod
    def __init__(self, conditions: pd.DataFrame):
        pass

    @abstractmethod
    def _calculate_signal(self) -> Any:
        pass

    @abstractmethod
    def _sanity_checks(self) -> None:
        pass

    def is_signal_true(self) -> pd.Series:
        self._sanity_checks()

        result = self._try_calculate_signal()

        return result

    def _try_calculate_signal(self) -> pd.Series:
        try:
            signal = self._calculate_signal()
        except Exception as e:
            raise Exception(
                "Someting went wrong during the calculation of the signal." + str(e)
            )

        if not isinstance(signal, pd.Series):
            raise ValueError("The signal was not a pandas Series.")

        return signal

    def _check_conditions_not_empty(self):
        if len(self.conditions) == 0:
            raise ValueError(
                "The conditions must contain values otherwise a signal can not be created."
            )


class SignalAllConditionsTrue(ISignal):
    def __init__(self, conditions: pd.DataFrame):
        self.conditions = conditions

    def _sanity_checks(self) -> None:
        self._check_conditions_not_empty()

    def _check_all_true(self, row: pd.Series):
        if row.hasnans:
            return False

        return row.all()

    def _calculate_signal(self) -> Any:
        return self.conditions.apply(self._check_all_true, axis=1)
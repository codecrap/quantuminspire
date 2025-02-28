""" Quantum Inspire SDK

Copyright 2018 QuTech Delft

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from typing import Any, Dict, List, Optional, Union
from qiskit.exceptions import QiskitError
from qiskit.result import postprocess, Result
from qiskit.result.models import ExperimentResult

from quantuminspire.exceptions import QiskitBackendError


class QIResult(Result):  # type: ignore
    """
    A result object returned by QIJob:
        qi_backend = QI.get_backend('QX single-node simulator')
        job = qi_backend.retrieve_job(job_id)
        qi_result = job.result()
    """
    def __init__(self, backend_name: str, backend_version: str, qobj_id: str, job_id: str, success: bool,
                 results: List[ExperimentResult], date: Any = None, status: Any = None, header: Any = None,
                 **kwargs: Any) -> None:
        """
        Construct a new QIResult object. Not normally called directly, use a QIJob to get the QIResult.

        :param backend_name: backend name.
        :param backend_version: backend version, in the form X.Y.Z.
        :param qobj_id: user-generated Qobj id.
        :param job_id: unique execution id from the backend.
        :param success: True if complete input qobj executed correctly. (Implies each experiment success)
        :param results: corresponding results for array of experiments of the input qobj
        :param date: date to be added to the result object
        :param status: status to be added to the result object
        :param header: header to be added to the result object
        :param kwargs: other parameters (added as metadata to the result object)
        """
        super().__init__(backend_name, backend_version, qobj_id, job_id, success,
                         results, date, status, header, **kwargs)

    def get_probabilities(self, experiment: Any = None) -> Union[Dict[str, float], List[Dict[str, float]]]:

        """Get the probability data of an experiment. The probability data is added as a separate result by
        Quantum Inspire backend. Based on Qiskit get_count method from Result.

        :param experiment (str or QuantumCircuit or Schedule or int or None): the index of the
                experiment, as specified by ``get_data()``.

        :return:
            One or more dictionaries which holds the states and probabilities for each result.

        :raises QiskitBackendError: raised if there are no probabilities in a result for the experiment(s).
        """
        if experiment is None:
            exp_keys = range(len(self.results))
        else:
            exp_keys = [experiment]  # type: ignore

        dict_list: List[Dict[str, float]] = []
        for key in exp_keys:
            exp = self._get_experiment(key)
            try:
                header = exp.header.to_dict()
            except (AttributeError, QiskitError):  # header is not available
                header = None

            if "probabilities" in self.data(key).keys():
                probabilities = self.data(key)["probabilities"]
                dict_list.append(postprocess.format_counts(probabilities, header))
            else:
                raise QiskitBackendError('No probabilities for experiment "{0}"'.format(key))

        # Return first item of dict_list if size is 1
        if len(dict_list) == 1:
            return dict_list[0]

        return dict_list

    def get_calibration(self, experiment: Any = None) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """Get the calibration data of an experiment. The calibration data is added as a separate result item by
        Quantum Inspire backend. Based on Qiskit get_count method from Result.

        :param experiment (str or QuantumCircuit or Schedule or int or None): the index of the
                experiment, as specified by ``get_data()``.

        :return:
            One or more dictionaries which holds the calibration data for each result.
            Exact format depends on the backend. A simulator backend has no calibration data (None is returned)

        :raises QiskitBackendError: raised if there is no calibration data in a result for the experiment(s).
        """
        if experiment is None:
            exp_keys = range(len(self.results))
        else:
            exp_keys = [experiment]  # type: ignore

        dict_list: List[Dict[str, float]] = []
        for key in exp_keys:
            exp = self._get_experiment(key)

            if "calibration" in self.data(key).keys():
                calibration = self.data(key)["calibration"]
                dict_list.append(calibration)
            else:
                raise QiskitBackendError('No calibration data for experiment "{0}"'.format(key))

        # Return first item of dict_list if size is 1
        if len(dict_list) == 1:
            return dict_list[0]

        return dict_list

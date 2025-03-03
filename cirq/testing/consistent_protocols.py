# Copyright 2018 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any, Dict, Optional, Sequence, Type, Union

import numpy as np
import sympy

from cirq import ops, protocols
from cirq.testing.circuit_compare import (assert_has_consistent_apply_unitary,
                                          assert_has_consistent_qid_shape)
from cirq.testing.consistent_decomposition import (
        assert_decompose_is_consistent_with_unitary)
from cirq.testing.consistent_phase_by import (
        assert_phase_by_is_consistent_with_unitary)
from cirq.testing.consistent_qasm import (
        assert_qasm_is_consistent_with_unitary)
from cirq.testing.consistent_pauli_expansion import (
        assert_pauli_expansion_is_consistent_with_unitary)
from cirq.testing.equivalent_repr_eval import assert_equivalent_repr


def assert_implements_consistent_protocols(
        val: Any,
        *,
        exponents: Sequence[Any] = (
            0, 1, -1, 0.5, 0.25, -0.5, 0.1, sympy.Symbol('s')),
        qubit_count: Optional[int] = None,
        ignoring_global_phase: bool=False,
        setup_code: str = 'import cirq\nimport numpy as np\nimport sympy',
        global_vals: Optional[Dict[str, Any]] = None,
        local_vals: Optional[Dict[str, Any]] = None
        ) -> None:
    """Checks that a value is internally consistent and has a good __repr__."""
    global_vals = global_vals or {}
    local_vals = local_vals or {}

    _assert_meets_standards_helper(val,
                                   qubit_count,
                                   ignoring_global_phase,
                                   setup_code,
                                   global_vals,
                                   local_vals)

    for exponent in exponents:
        p = protocols.pow(val, exponent, None)
        if p is not None:
            _assert_meets_standards_helper(val**exponent,
                                           qubit_count,
                                           ignoring_global_phase,
                                           setup_code,
                                           global_vals,
                                           local_vals)


def assert_eigengate_implements_consistent_protocols(
        eigen_gate_type: Type[ops.EigenGate],
        *,
        exponents: Sequence[Union[sympy.Basic, float]] = (
            0, 1, -1, 0.25, -0.5, 0.1, sympy.Symbol('s')),
        global_shifts: Sequence[float] = (0, -0.5, 0.1),
        qubit_count: Optional[int] = None,
        ignoring_global_phase: bool=False,
        setup_code: str = 'import cirq\nimport numpy as np\nimport sympy',
        global_vals: Optional[Dict[str, Any]] = None,
        local_vals: Optional[Dict[str, Any]] = None) -> None:
    """Checks that an EigenGate subclass is internally consistent and has a
    good __repr__."""
    for exponent in exponents:
        for shift in global_shifts:
            _assert_meets_standards_helper(
                    eigen_gate_type(exponent=exponent, global_shift=shift),
                    qubit_count,
                    ignoring_global_phase,
                    setup_code,
                    global_vals,
                    local_vals)


def assert_eigen_shifts_is_consistent_with_eigen_components(
        val: ops.EigenGate) -> None:
    assert val._eigen_shifts() == [e[0] for e in val._eigen_components()]


def assert_has_consistent_trace_distance_bound(val: Any) -> None:
    u = protocols.unitary(val, default=None)
    val_from_trace = protocols.trace_distance_bound(val)
    assert 0.0 <= val_from_trace <= 1.0
    if u is not None:

        class Unitary:

            def _unitary_(self):
                return u

        val_from_unitary = protocols.trace_distance_bound(Unitary())

        assert val_from_trace >= val_from_unitary or np.isclose(
            val_from_trace, val_from_unitary)


def _assert_meets_standards_helper(
        val: Any,
        qubit_count: Optional[int],
        ignoring_global_phase,
        setup_code: str,
        global_vals: Optional[Dict[str, Any]],
        local_vals: Optional[Dict[str, Any]]) -> None:
    assert_has_consistent_qid_shape(val, qubit_count=qubit_count)
    assert_has_consistent_apply_unitary(val, qubit_count=qubit_count)
    assert_qasm_is_consistent_with_unitary(val)
    assert_has_consistent_trace_distance_bound(val)
    assert_decompose_is_consistent_with_unitary(val,
        ignoring_global_phase=ignoring_global_phase)
    assert_phase_by_is_consistent_with_unitary(val)
    assert_pauli_expansion_is_consistent_with_unitary(val)
    assert_equivalent_repr(val,
                           setup_code=setup_code,
                           global_vals=global_vals,
                           local_vals=local_vals)
    if isinstance(val, ops.EigenGate):
        assert_eigen_shifts_is_consistent_with_eigen_components(val)

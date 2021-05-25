"""`StepImplementer` for the `unit-test` step using tox, for Python applications.

Step Configuration
------------------
Step configuration expected as input to this step.
Could come from:
* static configuration
* runtime configuration
* previous step results

Configuration Key  | Required? | Default     | Description
-------------------|-----------|-------------|-----------
`tox-env`          | No        | ALL         | Control which tox environment is run. \
                                               Default will be all environments.
Result Artifacts
----------------
Results artifacts output by this step.

Result Artifact Key | Description
--------------------|------------
`tox-output`      | Path to Stdout and Stderr from invoking Maven.
"""
import os
import sys

import sh
from ploigos_step_runner import StepResult, StepImplementer
from ploigos_step_runner.utils.io import create_sh_redirect_to_multiple_streams_fn_callback

DEFAULT_CONFIG = {
    'tox-env': 'all'
}

REQUIRED_CONFIG_OR_PREVIOUS_STEP_RESULT_ARTIFACT_KEYS = [
]


class Tox(StepImplementer):
    """`StepImplementer` for the `unit-test` step using tox, for Python applications
    """

    @staticmethod
    def step_implementer_config_defaults():
        """Getter for the StepImplementer's configuration defaults.

        Returns
        -------
        dict
            Default values to use for step configuration values.

        Notes
        -----
        These are the lowest precedence configuration values.

        """
        return DEFAULT_CONFIG

    @staticmethod
    def _required_config_or_result_keys():
        """Getter for step configuration or previous step result artifacts that are required before
        running this step.

        See Also
        --------
        _validate_required_config_or_previous_step_result_artifact_keys

        Returns
        -------
        array_list
            Array of configuration keys or previous step result artifacts
            that are required before running the step.
        """
        return REQUIRED_CONFIG_OR_PREVIOUS_STEP_RESULT_ARTIFACT_KEYS

    def _run_step(self):
        """Runs the step implemented by this StepImplementer.

        Returns
        -------
        StepResult
            Object containing the dictionary results of this step.
        """
        step_result = StepResult.from_step_implementer(self)

        tox_env = self.get_value('tox-env')
        tox_results_json = 'tox_results.json'
        tox_output_file_path = self.write_working_file('tox_output.txt')
        try:
            with open(tox_output_file_path, 'w') as tox_output_file:
                out_callback = create_sh_redirect_to_multiple_streams_fn_callback([
                    sys.stdout,
                    mvn_output_file
                ])
                err_callback = create_sh_redirect_to_multiple_streams_fn_callback([
                    sys.stderr,
                    mvn_output_file
                ])

                sh.tox( # pylint: disable=no-member
                    '-e', tox_env,
                    '--result-json', tox_results_json,
                    _out=out_callback,
                    _err=err_callback
                )
        except sh.ErrorReturnCode as error:
            step_result.message = "Unit test failures. See 'tox-output'" \
                f" and 'tox-results-json' report artifacts for details: {error}"
            step_result.success = False
        finally:
            step_result.add_artifact(
                description="Standard out and standard error from 'tox'"
                name="tox-output"
                value=tox_output_file_path
            )
            step_result.add_artifact(
                description="Results json from 'tox'",
                name='tox-results-json',
                value=tox_results_json
            )

        return step_result

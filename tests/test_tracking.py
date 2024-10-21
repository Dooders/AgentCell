import unittest
from unittest.mock import Mock, patch

from pyology.reporter import Reporter
from utils.command_data import CommandData
from utils.tracking import CommandExecutionResult, execute_command


class TestExecuteCommand(unittest.TestCase):
    def setUp(self):
        self.mock_obj = Mock()
        self.mock_obj.get_metabolite_quantity = Mock(
            side_effect=lambda attr: getattr(self.mock_obj, attr)
        )
        self.mock_obj.attr1 = 10
        self.mock_obj.attr2 = "initial"
        self.mock_obj.method = Mock(return_value="result")
        self.mock_logger = Mock(spec=Reporter)
        # Add warning and error methods to the mock logger
        self.mock_logger.warning = Mock()
        self.mock_logger.error = Mock()

    def test_simple_tracking(self):
        command_data = CommandData(
            obj=self.mock_obj,
            command=self.mock_obj.method,
            tracked_attributes=["attr1"],
        )
        result = execute_command(command_data, logger=self.mock_logger)
        self.assertIsInstance(result, CommandExecutionResult)
        self.assertEqual(result.result, "result")
        self.assertEqual(result.initial_values["attr1"], 10)
        self.assertEqual(result.final_values["attr1"], 10)

    def test_numeric_and_non_numeric_attributes(self):
        def side_effect(obj):
            obj.attr1 = 15
            return None

        self.mock_obj.method = Mock(side_effect=side_effect)
        command_data = CommandData(
            obj=self.mock_obj,
            command=self.mock_obj.method,
            tracked_attributes=["attr1", "attr2"],
        )
        result = execute_command(command_data, logger=self.mock_logger)
        self.assertEqual(result.initial_values["attr1"], 10)
        self.assertEqual(result.final_values["attr1"], 15)
        self.assertEqual(result.initial_values["attr2"], "initial")
        self.assertEqual(result.final_values["attr2"], "initial")

    def test_no_tracked_attributes(self):
        command_data = CommandData(
            obj=self.mock_obj, command=self.mock_obj.method, tracked_attributes=[]
        )
        result = execute_command(command_data, logger=self.mock_logger)
        self.assertEqual(result.result, "result")
        self.assertEqual(result.initial_values, {})
        self.assertEqual(result.final_values, {})

    def test_invalid_attribute(self):
        self.mock_obj.get_metabolite_quantity.side_effect = ValueError(
            "Invalid metabolite"
        )
        command_data = CommandData(
            obj=self.mock_obj,
            command=self.mock_obj.method,
            tracked_attributes=["invalid_attr"],
        )
        result = execute_command(command_data, logger=self.mock_logger)
        self.assertNotIn("invalid_attr", result.initial_values)
        self.assertNotIn("invalid_attr", result.final_values)
        self.mock_logger.warning.assert_called_with(
            "Error getting quantity for metabolite 'invalid_attr': Invalid metabolite. Skipping."
        )

    def test_validation_pass(self):
        def validation(obj, initial, final):
            return True

        command_data = CommandData(
            obj=self.mock_obj,
            command=self.mock_obj.method,
            tracked_attributes=["attr1"],
            validations=[validation],
        )
        result = execute_command(command_data, logger=self.mock_logger)
        self.assertEqual(result.result, "result")
        self.assertTrue(result.validation_results["validation_1"])

    def test_validation_fail(self):
        def validation(obj, initial, final):
            return False

        command_data = CommandData(
            obj=self.mock_obj,
            command=self.mock_obj.method,
            tracked_attributes=["attr1"],
            validations=[validation],
        )
        result = execute_command(command_data, logger=self.mock_logger)
        self.assertEqual(result.result, "result")
        self.assertFalse(result.validation_results["validation_1"])
        self.mock_logger.warning.assert_called_with("Validation 1 failed: validation")

    def test_multiple_validations(self):
        def validation1(obj, initial, final):
            return True

        def validation2(obj, initial, final):
            return False

        command_data = CommandData(
            obj=self.mock_obj,
            command=self.mock_obj.method,
            tracked_attributes=["attr1"],
            validations=[validation1, validation2],
        )
        result = execute_command(command_data, logger=self.mock_logger)
        self.assertEqual(result.result, "result")
        self.assertTrue(result.validation_results["validation_1"])
        self.assertFalse(result.validation_results["validation_2"])
        self.mock_logger.warning.assert_called_with("Validation 2 failed: validation2")

    def test_error_handling(self):
        self.mock_obj.method = Mock(side_effect=ValueError("Test error"))
        command_data = CommandData(
            obj=self.mock_obj,
            command=self.mock_obj.method,
            tracked_attributes=["attr1"],
        )
        with self.assertRaises(ValueError):
            execute_command(command_data, logger=self.mock_logger)

    def test_callable_command(self):
        def callable_command(obj, *args, **kwargs):
            obj.attr1 += 5
            return "callable result"

        command_data = CommandData(
            obj=self.mock_obj,
            command=callable_command,
            tracked_attributes=["attr1"],
            args=(1, 2),
            kwargs={"key": "value"},
        )
        result = execute_command(command_data, logger=self.mock_logger)

        self.assertEqual(result.result, "callable result")
        self.assertEqual(result.initial_values["attr1"], 10)
        self.assertEqual(result.final_values["attr1"], 15)

    def test_get_metabolite_quantity_error(self):
        self.mock_obj.get_metabolite_quantity.side_effect = AttributeError(
            "No such method"
        )
        command_data = CommandData(
            obj=self.mock_obj,
            command=self.mock_obj.method,
            tracked_attributes=["attr1"],
        )
        result = execute_command(command_data, logger=self.mock_logger)
        self.assertEqual(result.initial_values, {})
        self.assertEqual(result.final_values, {})
        self.mock_logger.error.assert_called()


if __name__ == "__main__":
    unittest.main()

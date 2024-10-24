import unittest
from pyology.tracker import Tracker, EnergyTracker, CO2Tracker

class TestTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = Tracker()

    def test_start_tracking(self):
        self.tracker.start_tracking()
        self.assertEqual(self.tracker.tracked_metrics, {})
        self.assertEqual(self.tracker.simulation_step, 0)

    def test_log_change(self):
        self.tracker.start_tracking()
        self.tracker.log_change("ATP Yield", 10.0)
        self.assertIn("ATP Yield", self.tracker.tracked_metrics)
        self.assertEqual(self.tracker.tracked_metrics["ATP Yield"], [(0, 10.0)])
        self.assertEqual(self.tracker.simulation_step, 1)

    def test_report(self):
        self.tracker.start_tracking()
        self.tracker.log_change("ATP Yield", 10.0)
        self.tracker.log_change("ATP Yield", 20.0)
        report = self.tracker.report()
        self.assertIn("ATP Yield", report)
        self.assertEqual(report["ATP Yield"], 15.0)

    def test_reset(self):
        self.tracker.start_tracking()
        self.tracker.log_change("ATP Yield", 10.0)
        self.tracker.reset()
        self.assertEqual(self.tracker.tracked_metrics, {})
        self.assertEqual(self.tracker.simulation_step, 0)

class TestEnergyTracker(unittest.TestCase):
    def setUp(self):
        self.energy_tracker = EnergyTracker()

    def test_log_energy(self):
        self.energy_tracker.start_tracking()
        self.energy_tracker.log_energy(10.0, 5.0, 2.0)
        self.assertIn("ATP Yield", self.energy_tracker.tracked_metrics)
        self.assertIn("NADH Contribution", self.energy_tracker.tracked_metrics)
        self.assertIn("FADH2 Contribution", self.energy_tracker.tracked_metrics)
        self.assertEqual(self.energy_tracker.tracked_metrics["ATP Yield"], [(0, 10.0)])
        self.assertEqual(self.energy_tracker.tracked_metrics["NADH Contribution"], [(0, 5.0)])
        self.assertEqual(self.energy_tracker.tracked_metrics["FADH2 Contribution"], [(0, 2.0)])
        self.assertEqual(self.energy_tracker.simulation_step, 1)

class TestCO2Tracker(unittest.TestCase):
    def setUp(self):
        self.co2_tracker = CO2Tracker()

    def test_log_co2_production(self):
        self.co2_tracker.start_tracking()
        self.co2_tracker.log_co2_production(10.0)
        self.assertIn("CO2 Production", self.co2_tracker.tracked_metrics)
        self.assertEqual(self.co2_tracker.tracked_metrics["CO2 Production"], [(0, 10.0)])
        self.assertEqual(self.co2_tracker.simulation_step, 1)

if __name__ == '__main__':
    unittest.main()

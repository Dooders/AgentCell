class Tracker:
    def __init__(self):
        self.tracked_metrics = {}
        self.simulation_step = 0

    def start_tracking(self):
        self.tracked_metrics = {}
        self.simulation_step = 0

    def log_change(self, metric: str, value: float):
        if metric not in self.tracked_metrics:
            self.tracked_metrics[metric] = []
        self.tracked_metrics[metric].append((self.simulation_step, value))
        self.simulation_step += 1

    def report(self):
        report_data = {}
        for metric, values in self.tracked_metrics.items():
            report_data[metric] = sum(value for step, value in values) / len(values)
        return report_data

    def reset(self):
        self.start_tracking()


class EnergyTracker(Tracker):
    def __init__(self):
        super().__init__()

    def log_energy(self, atp_yield: float, nadh_contribution: float, fadh2_contribution: float):
        self.log_change("ATP Yield", atp_yield)
        self.log_change("NADH Contribution", nadh_contribution)
        self.log_change("FADH2 Contribution", fadh2_contribution)


class CO2Tracker(Tracker):
    def __init__(self):
        super().__init__()

    def log_co2_production(self, co2_production: float):
        self.log_change("CO2 Production", co2_production)

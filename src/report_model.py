# report_model.py — the probabilistic model of a damage report. Domain vocabulary lives here.
import math
from prob import fit_categorical, fit_conditional, percentile

MATERIALS = ["stone", "ceramic", "metal", "wood", "textile"]
DAMAGE = ["crack", "loose_base", "fading", "rot", "corrosion"]
SEVERITIES = ["none", "minor", "major"]

def bucket(n_damage):
    return min(n_damage, 2)            # 0, 1, or 2+

class ReportModel:
    """P(report) = P(material) * prod_d P(d present | material) * P(severity | #damage bucket)
    A small Bayesian network: material -> each damage type; damage count -> severity."""

    def __init__(self, reports, alpha=1.0):
        self.alpha = alpha
        self.p_material = fit_categorical([r["material"] for r in reports], MATERIALS, alpha)
        self.p_damage = {
            d: fit_conditional([(r["material"], d in r["damage"]) for r in reports],
                               MATERIALS, [True, False], alpha)
            for d in DAMAGE
        }
        self.p_severity = fit_conditional(
            [(bucket(len(r["damage"])), r["severity"]) for r in reports],
            [0, 1, 2], SEVERITIES, alpha)

    def log_likelihood(self, report):
        m = report["material"]
        ll = math.log(self.p_material[m])
        for d in DAMAGE:
            ll += math.log(self.p_damage[d][m][d in report["damage"]])
        ll += math.log(self.p_severity[bucket(len(report["damage"]))][report["severity"]])
        return ll


def calibrate(model, reference_reports, q=0.02):
    """Threshold below which a report is 'improbable': the q-th percentile of the
    log-likelihoods of the trusted reference data itself."""
    return percentile([model.log_likelihood(r) for r in reference_reports], q)

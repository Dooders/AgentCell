from enum import Enum

# Mitochondrion constants
CALCIUM_THRESHOLD = 800
CALCIUM_BOOST_FACTOR = 1.2
MAX_PROTON_GRADIENT = 200
LEAK_RATE = 0.1
LEAK_STEEPNESS = 0.1
LEAK_MIDPOINT = 150

# Krebs Cycle constants
V_MAX_DEFAULT = 1.0
KM_DEFAULT = 0.1

# Electron Transport Chain constants
PROTONS_PER_NADH = 4
PROTONS_PER_FADH2 = 2
PROTONS_PER_ATP = 4

# NADH Shuttle efficiency
SHUTTLE_EFFICIENCY = 0.67

# Metabolite initial and max values
INITIAL_NAD = 10
MAX_METABOLITE = 1000
INITIAL_OXYGEN = 1000
INITIAL_ADP = 100
INITIAL_UBIQUINONE = 100
INITIAL_CYTOCHROME_C = 100

# Simulation constants
TIME_STEP = 0.1
SIMULATION_DURATION = 5


class GlycolysisSteps(Enum):
    STEP1_HEXOKINASE = "step1_hexokinase"
    STEP2_PHOSPHOGLUCOSE_ISOMERASE = "step2_phosphoglucose_isomerase"
    STEP3_PHOSPHOFRUCTOKINASE = "step3_phosphofructokinase"
    STEP4_ALDOLASE = "step4_aldolase"
    STEP5_TRIOSE_PHOSPHATE_ISOMERASE = "step5_triose_phosphate_isomerase"
    STEP6_GLYCERALDEHYDE_3_PHOSPHATE_DEHYDROGENASE = (
        "step6_glyceraldehyde_3_phosphate_dehydrogenase"
    )
    STEP7_PHOSPHOGLYCERATE_KINASE = "step7_phosphoglycerate_kinase"
    STEP8_PHOSPHOGLYCERATE_MUTASE = "step8_phosphoglycerate_mutase"
    STEP9_ENOLASE = "step9_enolase"
    STEP10_PYRUVATE_KINASE = "step10_pyruvate_kinase"

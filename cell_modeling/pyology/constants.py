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
    STEP1_HEXOKINASE = "Hexokinase"
    STEP2_PHOSPHOGLUCOSE_ISOMERASE = "Phosphoglucose Isomerase"
    STEP3_PHOSPHOFRUCTOKINASE = "Phosphofructokinase"
    STEP4_ALDOLASE = "Aldolase"
    STEP5_TRIOSE_PHOSPHATE_ISOMERASE = "Triose Phosphate Isomerase"
    STEP6_GLYCERALDEHYDE_3_PHOSPHATE_DEHYDROGENASE = (
        "Glyceraldehyde 3-Phosphate Dehydrogenase"
    )
    STEP7_PHOSPHOGLYCERATE_KINASE = "Phosphoglycerate Kinase"
    STEP8_PHOSPHOGLYCERATE_MUTASE = "Phosphoglycerate Mutase"
    STEP9_ENOLASE = "Enolase"
    STEP10_PYRUVATE_KINASE = "Pyruvate Kinase"

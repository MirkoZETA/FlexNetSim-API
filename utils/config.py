import logging

# --- Configuration ---
SIMULATION_EXECUTABLE = "./src/simulation.out"
COMPILE_ERROR = None

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Valid Values ---
valid_networks = ["NSFNet", "Cost239", "EuroCore", "GermanNet", "UKNet"]
valid_bitrates = ["fixed-rate", "flex-rate"]

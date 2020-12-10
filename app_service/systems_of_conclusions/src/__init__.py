from app_service.models import SystemOfConclusions
# TODO вынести работа с моделями обратно в манагера

def run_system(system: SystemOfConclusions, input_values: list) -> float:
    # Compute
    return sum(input_values)/len(input_values)
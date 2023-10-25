import yaml
from dataclasses import asdict
from models import Nation, Resources, Combat, ResearchAndDevelopment, EnemyNation
from simulation import Simulation

def create_models_from_yml():
    """
    Reads data from 'models.yml', processes it, and creates model instances.
    
    Returns:
        tuple: A tuple containing instances of Nation, Resources, Combat, 
        ResearchAndDevelopment, and EnemyNation. If any data is missing from the
        YAML, the respective instance will be None.
    """
    print("Loading values from models.yml")
    with open('models.yml', 'r') as file:
        data = yaml.safe_load(file)

        nation_data = data.get("nation")
        resources_data = data.get("resources")
        combat_data = data.get("combat")
        research_and_dev_data = data.get("research_and_dev")
        enemy_nation_data = data.get("enemy_nation")

        nation_instance = Nation(**nation_data) if nation_data else None
        resources_instance = Resources(**resources_data) if resources_data else None
        combat_instance = Combat(**combat_data) if combat_data else None
        research_and_dev_instance = ResearchAndDevelopment(**research_and_dev_data) if research_and_dev_data else None
        enemy_nation_instance = EnemyNation(**enemy_nation_data) if enemy_nation_data else None

        return nation_instance, resources_instance, combat_instance, research_and_dev_instance, enemy_nation_instance

def main():
    """
    Main function to run the script. It fetches model data from 'models.yml' 
    and prints the corresponding instances. This serves as a basic demonstration
    of how the models can be populated from the YAML.
    """
    nation, resources, combat, research_and_dev, enemy_nation = create_models_from_yml()
    simulation = Simulation(nation=nation, resources=resources, combat=combat, research_and_dev=research_and_dev, enemy_nation=enemy_nation)
    simulation.run()

def create_default_yml_file():
    """
    Generates a 'models.yml' file with default data. This can be used as a sample
    or as a reset to a default state.
    """
    nation = Nation("Sample Nation", 0, 100, 20, 80, 0.5, 0.3, 50, 200, 10, 5, 5, 50, 10, [])
    resources = Resources(100, 50, [])
    combat = Combat(200, 100, 300, 250, 10, 7, 400, 300, 6, False)
    research_and_dev = ResearchAndDevelopment(2, 5, 15, 20)
    enemy_nation = EnemyNation(0.6, 0.8, 0.7, 100, 10, 50, 5, 30, 10, 20, 0, 0, 0)

    # Define a dictionary with the instances
    data = {
        "nation": asdict(nation),
        "resources": asdict(resources),
        "combat": asdict(combat),
        "research_and_dev": asdict(research_and_dev),
        "enemy_nation": asdict(enemy_nation)
    }

    # Write the dictionary to a YAML file
    with open('models.yml', 'w') as file:
        yaml.dump(data, file)

if __name__ == "__main__":
    print("Initializating simulation")
    main()
    # create_default_yml_file()
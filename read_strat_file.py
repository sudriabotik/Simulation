file_path = 'fonction_asserv.txt'
#from robot import Robot
import re

def parse_fdd_commands(file_path):
    fdd_commands = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("fdd."):
                # Extraire le nom de la fonction et les arguments
                match = re.match(r"fdd\.(\w+)\((.*)\)", line)
                if match:
                    function_name = match.group(1)  # Nom de la fonction
                    raw_args = match.group(2)      # Arguments bruts
                    # Convertir les arguments en liste, en enlevant les guillemets et espaces
                    args = [arg.strip().strip('"') for arg in raw_args.split(",")]
                    fdd_commands.append((function_name, args))
    return fdd_commands

def execute_fdd_commands(commands, robot_instance):
    for function_name, args in commands:
        if function_name == "avancer":
            # Convertir les arguments en types corrects
            distance = int(args[0])
            ration_vitesse = int(args[1])
            # Appeler la méthode correspondante
            robot_instance.avancer(distance, ration_vitesse, 0.030)  # Ratio de vitesse 1.0, dt fictif
        elif function_name == "cibler":
            # Exemple pour une autre fonction
            print(f"Appel de la fonction cibler avec les arguments : {args}")
        else:
            print(f"Fonction {function_name} non reconnue ou non prise en charge.")


commande = parse_fdd_commands(file_path)
print(commande)

#execute_fdd_commands(commande)
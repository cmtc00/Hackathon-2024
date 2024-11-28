import subprocess
import sys

def check_requirements():
    missing_libraries = []
    
    with open('requirements.txt', 'r') as file:
        for line in file:
            library = line.strip()
            if library:
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'show', library], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except subprocess.CalledProcessError:
                    missing_libraries.append(library)
    
    if missing_libraries:
        print("Missing libraries:")
        for lib in missing_libraries:
            print(lib)
    else:
        print("All libraries are installed.")

# Executia se intampla doar daca scriptul este rulat direct
if __name__ == "__main__":
    check_requirements()
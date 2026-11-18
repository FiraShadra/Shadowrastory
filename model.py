#this here is for the dragon design editor, which is a separate program from the game itself. It is not used by the game, but it is used to create and edit dragon designs. The game loads the design from a JSON file, and this code provides functions to load, save, and normalize the design data.
#
# The editor now lives with all of Shadowra's assets in src/shamodel/ (her modelling kit); this file starts it.
#   python model.py              opens the Shadowra Modeler on src/shamodel/shadowra_design.json (what the game uses)
#   python model.py other.json   opens another design file
from src.shamodel.editor import main


if __name__ == "__main__":
    main()

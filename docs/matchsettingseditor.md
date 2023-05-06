# Interactive MatchSettings Editor

This Editor can be used to create, delete and modify your MatchSettings files. It's meant to assist  you with handling Challenges files and their unique IDs as this is quiet an annoying task.

It can be accessed from the TMNFD-CLI by choosing the option `Open MatchSettings Editor` from there on the interactive mode is started.

## Overview of the interface

The interface is made up of two columns. The left one shows all available Challenges and the right one the content of the opened MatchSettings File.

The name of the MatchSettings File is shown in the header of the right column; underneath that (offset to the right) is the current insert mode reflected (see controls).

On the bottom of the screen you find some helpful controls. Also all dialogs usually tell you with buttons to press to proceed or escape.

## Controls

The MatchSettings Editor can be left by pressing `q` or `<ESC>`. Be aware that nothing gets auto-saved. Just leaving the Editor is going to drop all your unsaved changes without warning.

By pressing the `?` on your keyboard you are getting an overview of all available inputs/controls those are the following:

  * **o**: Opens a MatchSettings File allready present on disk
  * **n**: Creates a new MatchSettings File and opens it (the MatchSettings File is not present on disk just after creation)
  * **s**: Saves a MatchSettings File to disk (the name can't be changed in this step, it is keept as is or has been entered during creation)
  * **a**: Sets a MatchSettings File as active (You can choose a MatchSettings File to be configured as active for TMNFD)
  * **r**: Remove a MatchSettings File (You can choose a MatchSettings File that is going to be deleted from disk)
  * **m**: changes the mode how Challenges are added to the opend MatchSettings.
By default `append` is selected which allways adds new Challenges to the end of the list.
Toggleing the mode to `insert` now adds new Challenges to the position behind the marked Challenge in the right column.
  * **<ENTER\>**: adds marked Challenge in left column to MatchSettings list on the right column (this is only available after opening a MatchSettings File)
  * **<ENTF\>**: removes marked Challenge in right column from MatchSettings (this is only available after opening a MatchSettings File)
  * **<UP\>, <DOWN\>**: Navigate through Lists
  * **<LEFT\>, <RIGHT\>**: Jump between left and right column
  * **<PAGE-UP/DOWN\>**: moves marked Challenge in right column up and down (this is only available after opening a MatchSettings File)

## Step-by-Step usecase

Lets say you would like to have a MatchSettings with all one Challenges (A1, B1, C1, D1, E1).

  * Hit **n** and type in a name like `AllOnes`
  * Hit **<ENTER\>**
  * Scroll through the Challenges and hit **<ENTER\>** on all the one Challenges
  * If you like to chanege the played order; hit **<RIGHT\>** to jump to the right column
    * Scroll to the Challenge you like to move and hit **<PAGE-UP/DOWN\>** to move it to the desired position
  * Now press **s** to save and confirm with **y**
    * The upcomming info can be exited with **<ENTER\>** or **<ESC\>**
  * For also selecting this new MatchSettings as active hit **a**
  * Move the selection to `AllOnes` and hit **<ENTER\>**
  * Confirm with **y** and close the info with **<ENTER\>** or **<ESC\>**
  * Now leave the MatchSettings Editor with **q** or **<ESC\>**
  * Exit TMNFD-CLI
  * Finally restart the stack, to apply the new MatchSettings `tas --restart`
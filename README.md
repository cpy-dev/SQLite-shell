# SQLite-shell
### Lightweight cross platform open source SQLite shell

# Installation

Download the .deb file corresponding with your system. Example: 

    $ curl https://github.com/CargoCodes/SQLite-shell/raw/main/sqliteshell_1.1.3-1_i386.deb -o sqliteshell_1.1.3-1_i386.deb

Then install it via dpkg:

    $ dpkg -i sqliteshell_1.1.3-1_i386.deb

# Setup
    
Before yout start using SQLite-Shell, you need to run "sqliteshellsetup" command, to make sure that the needed dependencies are up to date. 
    
    $ sqliteshellsetup
    
On some systems you may need to gain execution permit, to do that navigate to your /usr/local/bin folder and type:
    
    $ sudo chmod +x sqliteshellsetup

# Usage
    
    $ sqliteshell
     
Remember to enter the full file path of the database in the given space, and to press "Load" before executing any command

Source code is installed in your system at /usr/local/src/sqliteshell. Please don't delete source code, it will cause SQLite-Shell to not run anymore

# Updates
### Version 1.1.0
Added support for multiple commands run, updated rendering system

### Version 1.1.1
Bug fix

### Version 1.1.2
Bug fix and error popup added

### Version 1.1.3
Output cancellation implemented

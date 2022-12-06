import sys
from os.path import exists, expanduser

steam_path = None
dedicated_server_log = None
argument = None
home = expanduser("~")
proton_compat_data = "/steamapps/compatdata/230410/pfx"
proton_bin = "/steamapps/common"
warframe = "/drive_c/users/steamuser/AppData/Local/Warframe"
warframe_exe = "/steamapps/common/Warframe/Warframe.x64.exe"
# get steam dir with Warframe compat files from known possible locations
if exists(home + "/.steam/steam" + proton_compat_data + warframe):
    steam_path = home + "/.steam/steam"
elif exists(home + "/.local/share/steam" + proton_compat_data + warframe):
    steam_path = home + "/.local/share/steam"
elif exists(home + "/.var/app/com.valvesoftware.Steam/.local/share/steam" + proton_compat_data + warframe):
    steam_path = home + "/.var/app/com.valvesoftware.Steam/.local/share/steam"
elif exists(home + "/.steam/Steam" + proton_compat_data + warframe):
    steam_path = home + "/.steam/Steam"
elif exists(home + "/.local/share/Steam" + proton_compat_data + warframe):
    steam_path = home + "/.local/share/Steam"
elif exists(home + "/.var/app/com.valvesoftware.Steam/.local/share/Steam" + proton_compat_data + warframe):
    steam_path = home + "/.var/app/com.valvesoftware.Steam/.local/share/Steam"
# if valid directory was found get dedicated server output and proton version
if steam_path is not None:
    if len(sys.argv) > 1:
        print("Specific proton version requested!")
        argument = sys.argv[1].strip()
    else:
        print("No proton version specified using Proton - Experimental")
        argument = "Experimental"
    # get proton warframe files
    if exists(steam_path + proton_compat_data + warframe):
        print("Found steam proton Warframe files: " + steam_path + proton_compat_data + warframe)
        if exists(steam_path + proton_compat_data + warframe + "/DedicatedServer.log"):
            dedicated_server_log = open(steam_path + proton_compat_data + warframe + "/DedicatedServer.log", "r")
        else:
            print("Warframe dedicated server has to be run at least once through steam for this script to work!")
            exit(0)
    else:
        print("Steam was found but proton Warframe files were not, "
              "make sure Warframe dedicated server was run at least once through steam!")
        exit(0)
else:
    print("Steam files not found!")
    exit(0)
# dedicated server outputs its cmd arguments as the first line of log output
server_arguments = dedicated_server_log.readline().split("Process Command-line:")[1]
print("Harvested arguments: " + server_arguments.strip())
# get proton files
if argument == "Experimental":
    if exists(steam_path + proton_bin + "/Proton - " + argument):
        proton_bin = steam_path + proton_bin + "/Proton\ -\ " + argument + "/proton"
    else:
        print("Requested proton version: Proton - " + argument + " does not exist!")
        exit(0)
else:
    if exists(steam_path + proton_bin + "/Proton " + argument):
        proton_bin = steam_path + proton_bin + "/Proton\ " + argument + "/proton"
    else:
        print("Requested proton version: Proton " + argument + " does not exist!")
        exit(0)
print("Found proton location: " + proton_bin)
# generate shell file that starts the Warframe conclave server
print("Generating shell file!")
shell_out = open("StartWFServer.sh", "w")
shell_out.write('export STEAM_COMPAT_DATA_PATH="' + steam_path + proton_compat_data + '"\n')
shell_out.write('export STEAM_COMPAT_CLIENT_INSTALL_PATH="' + steam_path + '/Steam"\n')
shell_out.write(proton_bin + " waitforexitandrun '" + steam_path + warframe_exe + "'" + server_arguments)
print("Done!")
print("To start Warframe conclave server run 'StartWFServer.sh' and have fun!")

import os
import sys
import subprocess
from os.path import exists, expanduser

steam_path = None
dedicated_server_log = None
argument = None
home = expanduser("~")
proton_compat_data = "/steamapps/compatdata/230410"
proton_bin = "/steamapps/common"
warframe_compat = "/pfx/drive_c/users/steamuser/AppData/Local/Warframe"
warframe_files = "/steamapps/common/Warframe"
log = open("ServerLauncher.log", "w")
# get steam dir with Warframe compat files from known possible locations
if exists(home + "/.steam/steam" + proton_compat_data + warframe_compat):
    steam_path = home + "/.steam/steam"
elif exists(home + "/.local/share/steam" + proton_compat_data + warframe_compat):
    steam_path = home + "/.local/share/steam"
elif exists(home + "/.var/app/com.valvesoftware.Steam/.local/share/steam" + proton_compat_data + warframe_compat):
    steam_path = home + "/.var/app/com.valvesoftware.Steam/.local/share/steam"
elif exists(home + "/.steam/Steam" + proton_compat_data + warframe_compat):
    steam_path = home + "/.steam/Steam"
elif exists(home + "/.local/share/Steam" + proton_compat_data + warframe_compat):
    steam_path = home + "/.local/share/Steam"
elif exists(home + "/.var/app/com.valvesoftware.Steam/.local/share/Steam" + proton_compat_data + warframe_compat):
    steam_path = home + "/.var/app/com.valvesoftware.Steam/.local/share/Steam"

# if valid directory was found get dedicated server output and proton version
if steam_path is not None:
    log.write("Steam: " + steam_path + "\n")
    if len(sys.argv) > 1:
        print("Specific proton version requested!")
        argument = sys.argv[1].strip()
    else:
        print("No proton version specified using Proton - Experimental")
        argument = "Experimental"

    # get proton warframe files
    if exists(steam_path + proton_compat_data + warframe_compat):
        print("Found steam proton Warframe files: " + steam_path + proton_compat_data + warframe_compat)
        log.write("ProtonWF: " + steam_path + proton_compat_data + warframe_compat + "\n")
        if exists(steam_path + proton_compat_data + warframe_compat + "/DedicatedServer.log"):
            dedicated_server_log = open(steam_path + proton_compat_data + warframe_compat + "/DedicatedServer.log", "r")
            log.write("DedicatedServerLog: " + steam_path + proton_compat_data + warframe_compat
                      + "/DedicatedServer.log" + "\n")
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

# get proton files
if argument == "Experimental":
    if exists(steam_path + proton_bin + "/Proton - " + argument):
        proton_bin = steam_path + proton_bin + "/Proton\\ -\\ " + argument + "/proton"
    else:
        print("Requested proton version: Proton - " + argument + " does not exist!")
        exit(0)
else:
    if exists(steam_path + proton_bin + "/Proton " + argument):
        proton_bin = steam_path + proton_bin + "/Proton\\ " + argument + "/proton"
    else:
        print("Requested proton version: Proton " + argument + " does not exist!")
        exit(0)
print("Found proton location: " + proton_bin)
log.write("ProtonLocation: " + proton_bin + "\n")

# dedicated server outputs its cmd arguments as the first line of log output
last_used_arguments = dedicated_server_log.readline().split("Process Command-line:")[1].strip().split("-override:{")
log.write("ServerArguments: " + "-override:{".join(last_used_arguments) + "\n")
server_arguments = last_used_arguments[0].split()
print("Harvested arguments: " + str(server_arguments)[1:-1])

# set dedicated server settings
if len(last_used_arguments) > 1:
    overrides = last_used_arguments[1].replace("\"", "").replace(":", "=").replace("false", "0")\
        .replace("disabled", "0").replace("true", "1").replace("enabled", "1").replace("}", "").split(",")
    with open(steam_path + proton_compat_data + warframe_compat + "/DS.cfg", "r") as config:
        dedicated_server_config = config.readlines()
        log.write("==UsingConfig==\n" + " ".join(dedicated_server_config) + "==EndConfig==\n")

    try:
        launcher_settings = \
            dedicated_server_config.index("[LauncherDedicatedServerSettings,LotusDedicatedServerSettings]\n")
    except ValueError:
        dedicated_server_config.append("[LauncherDedicatedServerSettings,LotusDedicatedServerSettings]\n")
        launcher_settings = None

    if launcher_settings is not None:
        dedicated_server_config = dedicated_server_config[:launcher_settings + 1]

    log.write("ApplyingOverrides: " + " ".join(overrides) + "\n")
    for line in overrides:
        dedicated_server_config.append(line + "\n")

    print("Overrides applied!")
    with open(steam_path + proton_compat_data + warframe_compat + "/DS.cfg", "w") as config:
        config.writelines(dedicated_server_config)
        log.write("Written: " + steam_path + proton_compat_data + warframe_compat + "/DS.cfg" + "\n")

    server_arguments.append("-settings:LauncherDedicatedServerSettings")

# set environment variables
os.environ["STEAM_COMPAT_DATA_PATH"] = steam_path + proton_compat_data
os.environ["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = steam_path
print("Environment variables set!")
# start dedicated server
print("Starting Warframe dedicated server!")
os.chdir(steam_path + proton_compat_data + warframe_compat)
server_command = [proton_bin.replace("\\", ""), "waitforexitandrun", steam_path + warframe_files + "/Warframe.x64.exe"]
log.write("RunningCommand: " + " ".join(server_command + server_arguments) + "\n")
server = subprocess.Popen(server_command + server_arguments, stdout=subprocess.PIPE)

# output the server output until closed
while True:
    output = server.stdout.readline()
    print(output.strip())
    return_code = server.poll()
    if return_code is not None:
        for output in server.stdout.readlines():
            print(output.strip())
        print("Server exited with exit code: " + str(return_code) + " !")
        break

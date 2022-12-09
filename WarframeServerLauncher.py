import os
import sys
import subprocess
import time
from os.path import exists, expanduser

steam_path = None
dedicated_server_log = None
server_instances = 1
arguments = sys.argv
proton_version = "Experimental"
home = expanduser("~")
proton_compat_data = "/steamapps/compatdata/230410"
proton_bin = "/steamapps/common"
warframe_compat = "/pfx/drive_c/users/steamuser/AppData/Local/Warframe"
warframe_files = "/steamapps/common/Warframe"
log = open("ServerLauncher.log", "w")

# get launcher arguments
try:
    proton_version = arguments[arguments.index("--proton") + 1].strip()
    print("Specific proton version requested!")
except ValueError:
    print("No proton version specified using Proton - Experimental!")

try:
    server_instances = int(arguments[arguments.index("--multi") + 1].strip())
    print("Multiple instances requested!")
except ValueError:
    print("Instance number not specified defaulting to 1 instance!")

log.write("Using proton: " + proton_version + "\nRunning: " + str(server_instances) + " instances\n")

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

# if valid directory was found get dedicated server output
if steam_path is not None:
    log.write("Steam: " + steam_path + "\n")

    # get proton warframe files
    if exists(steam_path + proton_compat_data + warframe_compat):
        print("Found steam proton Warframe files: " + steam_path + proton_compat_data + warframe_compat)
        log.write("Warframe compatibility files: " + steam_path + proton_compat_data + warframe_compat + "\n")
        if exists(steam_path + proton_compat_data + warframe_compat + "/DedicatedServer.log"):
            dedicated_server_log = open(steam_path + proton_compat_data + warframe_compat + "/DedicatedServer.log", "r")
            log.write("Dedicated server log: " + steam_path + proton_compat_data + warframe_compat
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
if proton_version == "Experimental":
    if exists(steam_path + proton_bin + "/Proton - " + proton_version):
        proton_bin = steam_path + proton_bin + "/Proton\\ -\\ " + proton_version + "/proton"
    else:
        print("Requested proton version: Proton - " + proton_version + " does not exist!")
        exit(0)
else:
    if exists(steam_path + proton_bin + "/Proton " + proton_version):
        proton_bin = steam_path + proton_bin + "/Proton\\ " + proton_version + "/proton"
    else:
        print("Requested proton version: Proton " + proton_version + " does not exist!")
        exit(0)
print("Found proton location: " + proton_bin)
log.write("Proton location: " + proton_bin + "\n")

# dedicated server outputs its cmd arguments as the first line of log output
last_used_arguments = dedicated_server_log.readline().split("Process Command-line:")[1].strip().split("-override:{")
dedicated_server_log.close()
log.write("Server arguments: " + "-override:{".join(last_used_arguments) + "\n")
server_arguments = last_used_arguments[0].split()
print("Harvested arguments: " + str(server_arguments)[1:-1])

# set dedicated server settings
with open(steam_path + proton_compat_data + warframe_compat + "/DS.cfg", "r") as config:
    dedicated_server_config = config.readlines()
    log.write("==UsingConfig==\n" + " ".join(dedicated_server_config) + "==EndConfig==\n")

if len(last_used_arguments) > 1:
    overrides = last_used_arguments[1].replace("\"", "").replace(":", "=").replace("false", "0")\
        .replace("disabled", "0").replace("true", "1").replace("enabled", "1").replace("}", "").split(",")

    try:
        launcher_settings = \
            dedicated_server_config.index("[LauncherDedicatedServerSettings,LotusDedicatedServerSettings]\n")
    except ValueError:
        dedicated_server_config.append("[LauncherDedicatedServerSettings,LotusDedicatedServerSettings]\n")
        launcher_settings = None

    if launcher_settings is not None:
        dedicated_server_config = dedicated_server_config[:launcher_settings + 1]

    log.write("Applying overrides: " + " ".join(overrides) + "\n")
    for line in overrides:
        dedicated_server_config.append(line + "\n")

    print("Overrides applied!")
    with open(steam_path + proton_compat_data + warframe_compat + "/DS.cfg", "w") as config:
        config.writelines(dedicated_server_config)
        log.write("Written: " + steam_path + proton_compat_data + warframe_compat + "/DS.cfg" + "\n")

# set environment variables
os.environ["STEAM_COMPAT_DATA_PATH"] = steam_path + proton_compat_data
os.environ["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = steam_path
print("Environment variables set!")
# start dedicated server
print("Starting Warframe dedicated server!")
os.chdir(steam_path + proton_compat_data + warframe_compat)
server_command = [proton_bin.replace("\\", ""), "run", steam_path + warframe_files + "/Warframe.x64.exe"]
server_arguments.pop([server_arguments.index(i) for i in server_arguments if i.startswith("-log:")][0])
servers = []
for i in range(server_instances):
    command = server_command + ["-log:DedicatedServer" + str(i) + ".log", ] + \
              server_arguments + ["-instance:" + str(i), "-settings:LauncherDedicatedServerSettings"]
    log.write("Running command: " + " ".join(command) + "\n")
    servers.append(subprocess.Popen(command))

# hold process until server closed
while True:
    time.sleep(0.5)
    for i, server in enumerate(servers):
        return_code = server.poll()
        if return_code is not None:
            print("Server " + str(i) + " exited with exit code: " + str(return_code) + " !")
            log.write("Server " + str(i) + " exited with exit code: " + str(return_code) + "\n")

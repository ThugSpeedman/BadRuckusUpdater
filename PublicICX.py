import os
import time
from datetime import datetime
from netmiko import ConnectHandler
import logging
from getpass import getpass
logging.basicConfig(filename="log.txt", level=logging.DEBUG)
host = input("Enter your hostname: ")


device = {
    'device_type': 'brocade_fastiron',
    'host': host,
    "username": "USERNAME", #add username
    "password": getpass(),
    'global_delay_factor': 2,
}

cmd = 'copy scp flash **IP ADDRESS* SPS08095kufi.bin secondary'
scp_rest = 250
flash_rest = 400
reset_counter = 0

# Define instruction sets for each reset_counter value
def reset_counter_1(ssh_connection):
    print(f"Uploading Firmware and Changing Boot Priority - reset_counter = {reset_counter}")
    # Output Flash Upload
    ssh_connection.send_command(cmd,expect_string=r'User name')
    ssh_connection.send_command_timing('USERNAME',delay_factor=2)   #SCP CREDS
    ssh_connection.send_command_timing('PASSWORD\n',delay_factor=2) #SCP CREDS
    print()
    print()
    print("##########################################################")    
    print(f"Waiting For Flash Upload...Configured for {scp_rest} seconds")
    print("##########################################################") 
    print()
    print()
    time.sleep(scp_rest)
    print()
    print()
    print("################################################")
    print("Times Up! Showing Flash...These Should NOT Match")
    print("################################################")
    print()
    print()
    time.sleep(2)
    output = ssh_connection.send_command('sh flash',delay_factor=2)
    time.sleep(5)
    print(output)
    time.sleep(1)
    output = ssh_connection.send_command('sh ver',delay_factor=2)
    time.sleep(5)
    print(output)
    print()
    print()
    print("WARNING : Booting to Secondary Flash...Expect disconnects...")
    print()
    print()
    ssh_connection.send_command('wr mem',delay_factor=2)
    time.sleep(2)
    ssh_connection.send_command("boot system flash secondary yes")



def reset_counter_2(ssh_connection):
    print(f"Copying Flash - reset_counter = {reset_counter}")
    time.sleep(5)
#   Short Pause then swapping flash
    print()
    print()
    print("#######################################################################")
    print(f"Copying Secondary Flash to Primary...Configured for {flash_rest} seconds")
    print("#######################################################################")
    print()
    print()
    ssh_connection.send_command("copy flash flash primary")
    time.sleep(flash_rest)

#
def reset_counter_3(ssh_connection):
    print(f"Changing Boot Priority - reset_counter = {reset_counter}")
    print()
    print()
    print("#############################################")
    print("Times Up! Showing Flash...These SHOULD Match")
    print("#############################################")
    print()
    print()
    time.sleep(2)
    output = ssh_connection.send_command_timing('sh flash',delay_factor=2)
    time.sleep(5)
    output += ssh_connection.send_command('sh ver',delay_factor=2)
    time.sleep(5)
    ssh_connection.send_command('wr mem',delay_factor=2)
    print(output)
    print()
    print()
    print("WARNING : Booting to Primary Flash. Expect disconnects. This will take a while...")
    print()
    print()
    output = ssh_connection.send_command("boot system flash primary yes")

def reset_counter_4(ssh_connection):
    print(f"Confirming Upgrade...Reset Count : {reset_counter}")
#    Confirming Updated Flash
    time.sleep(5)
    print()
    print()
    print("##############################################")
    print("BOTH Should List Updated Version...")
    print("Show Version Should Show Primary Boot Device...")
    print("##############################################")
    print()
    print()
    output = ssh_connection.send_command("sh flash")
    print(output)
    time.sleep(2)
    output = ssh_connection.send_command("sh ver")
    print(output)




while reset_counter <= 3:
    try:
        # Create a Netmiko SSH connection
        ssh_connection = ConnectHandler(**device)
        ssh_connection.enable()
        print('Connecting to Switch...')
        # Execute the corresponding function based on reset_counter value
        if reset_counter == 0:
            reset_counter += 1
            print(f"Reset Counter : {reset_counter}")
            reset_counter_1(ssh_connection)
        elif reset_counter == 1:
            reset_counter += 1
            print(f"Reset Counter : {reset_counter}")
            reset_counter_2(ssh_connection)
        elif reset_counter == 2:
            reset_counter += 1
            print(f"Reset Counter : {reset_counter}")
            reset_counter_3(ssh_connection)
        elif reset_counter == 3:
            reset_counter += 1
            print(f"Reset Counter : {reset_counter}")
            reset_counter_4(ssh_connection)


        # Send the reload command
#        ssh_connection.send_command("reload")
        
        # Reboot process and sh flash for current config
#        print("showing flash")
#        output = ssh_connection.send_command_timing('sh flash',delay_factor=2)
#        print(output)
#        ssh_connection.send_command_timing('wr mem',delay_factor=2)
#        time.sleep(3)
#       print("wr mem/reloading")
#       ssh_connection.send_command_timing('reload',delay_factor=2)
#        time.sleep(1)
#        ssh_connection.clear_buffer()
#        time.sleep(0.25)
#        ssh_connection.write_channel("y")
#        time.sleep(10)
        print(f"Waiting for the device to reboot (reset_counter = {reset_counter})...")
        ssh_connection.disconnect()

        
        # Keep attempting to reconnect until successful
        while True:
            try:
                ssh_connection = ConnectHandler(**device)
                ssh_connection.enable()
                break  # Break the loop if it reconnects
            except Exception as e:
                print(f"Reconnection attempt failed: {str(e)}")
                time.sleep(15)  # Delay Adjust

        
    except Exception as e:
        print(f"Error: {str(e)}")

        
print("###################################################")    
print(f"Update Completed After #{reset_counter - 1}# Resets")
print("###################################################")

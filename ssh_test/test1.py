import random
from ShellHandler import ShellHandler

robot_usr = "robot"
robot_pass = "maker"
robot_ip = "fe80::f413:32ff:fe22:79b6%en4"
script_location = "/home/robot/ssh_test"
script_name = "test2.py"

if __name__ == "__main__":
    arg = random.randint(0, 99999)
    print("program ran with", arg)
    shell = ShellHandler(robot_ip, robot_usr, robot_pass)
    shell.execute("cd " + script_location)
    shell.execute("python3 " + script_name + " " + str(arg))

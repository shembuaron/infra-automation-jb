# Basic imports
import sys
import json
import shutil
import subprocess
from pathlib import Path
from enum import Enum

# <333
from loguru import logger

# Pydantic is just for its methods, prompt-toolkit takes care of user validation.
# Also, separate validation errors between pydantic and prompt_toolkit
from pydantic import BaseModel, ConfigDict, ValidationError as PydanticValidationError

# Main UI library
from prompt_toolkit.validation import Validator, ValidationError as PromptValidationError
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import choice

# This will surely go well and have no unforseen consequences
from prompt_toolkit import print_formatted_text as print

#Pretty :)
import pyfiglet


# Global varibables
available_os = [
            ("amazon_linux_2023", "Amazon Linux 2023"),
            ("macos_tahoe", "macOS Tahoe"),
            ("ubuntu_server_24_04", "Ubuntu Server 24.04 LTS"),
            ("windows_server_2k25", "Microsoft Windows Server 2025 Base"),
            ("red_hat_linux_10", "Red Hat Enterprise Linux 10"),
            ("suse_linux_server_16", "SUSE Linux Enterprise Server 16"),
            ("debian_13", "Debian 13")
        ]
# Create Enum class for later validation
OSChoice = Enum("OSChoice", {key: key for key, _ in available_os})


available_types = [
            ("t2.nano", "t2.nano (1 vCPU, 0.5 GiB Memory)"),
            ("t2.micro", "t2.micro (1 vCPU, 1 GiB Memory)"),
            ("t2.small", "t2.small (1 vCPU, 2 GiB Memory)"),
            ("t2.medium", "t2.medium (2 vCPU, 4 GiB Memory)"),
            ("t2.large", "t2.large (2 vCPU, 8 GiB Memory)"),
            ("t2.xlarge", "t2.xlarge (4 vCPU, 16 GiB Memory)"),
            ("t2.2xlarge", "t2.2xlarge (8 vCPU, 32 GiB Memory)"),
            ("t3.nano", "t3.nano (2 vCPU, 0.5 GiB Memory)"),
            ("t3.micro", "t3.micro (2 vCPU, 1 GiB Memory)"),
            ("t3.small", "t3.small (2 vCPU, 2 GiB Memory)"),
            ("t3.medium", "t3.medium (2 vCPU, 4 GiB Memory)"),
            ("t3.large", "t3.large (2 vCPU, 8 GiB Memory)"),
            ("t3.xlarge", "t3.xlarge (4 vCPU, 16 GiB Memory)"),
            ("t3.2xlarge", "t3.2xlarge (8 vCPU, 32 GiB Memory)")
        ]

TypeChoice = Enum("TypeChoice", {key: key for key, _ in available_types})


# Gives built-in print and model dump methods
# No need for extra machine.py file
class EC2Instance(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    name: str
    os: OSChoice
    type: TypeChoice


# TBD make a global variable in main()
ec2_instances: list[EC2Instance] = []


class NameValidator(Validator):
    def validate(self, document):
        text = document.text
        if not text:
            raise PromptValidationError(
                message=" Name cannot be empty."
            )
        if not text.replace("_","").isalnum():
            raise PromptValidationError(
                message=" Name may only contain letters, numbers and underscores."
            )
        elif any(instance['name'] == text for instance in ec2_instances):
            raise PromptValidationError(
                message=" Name must be unique."
            )


def get_instance_os():
    os = choice(
        message="\nSelect an operating system:",
        options=available_os,
        default="amazon_linux",
        bottom_toolbar=HTML(
        " Press <b>[Up]</b>/<b>[Down]</b> to select, <b>[Enter]</b> to accept."),
    )
    return os


def get_instance_type():
    type = choice(
        message="\nSelect an instance type:",
        options=available_types,
        default="t3.micro",
        bottom_toolbar=HTML(
        " Press <b>[Up]</b>/<b>[Down]</b> to select, <b>[Enter]</b> to accept."),
    )
    return type


def provision_ec2(): 
    name = prompt(f"\n Enter a name for machine no.{len(ec2_instances) + 1}: ", validator = NameValidator())
    os = get_instance_os()
    type = get_instance_type()
    
    try:
        ec2_instance = EC2Instance.model_validate({'name': name, 'os': os, 'type': type})
        return ec2_instance
    except PydanticValidationError as err:
        #this should never really happen
        print(err)
        raise
    
def setup_logger():
    logger.remove()
    logger.add("logs/provisioning.log", level="DEBUG")
    logger.add(sys.stderr, level="INFO", format=" {message}", 
               filter=lambda record: record["level"].name == "INFO")
    logger.add(sys.stderr, level="WARNING", format=" WARNING: {message}",
               filter=lambda record: record["level"].name == "WARNING")
    logger.add(sys.stderr, level="ERROR", format="<light-red><b> ERROR:</b> {message}</light-red>", 
           colorize=True, filter=lambda record: record["level"].name == "ERROR")
    logger.add(sys.stderr, level="SUCCESS", format="<light-green><b> SUCCESS:</b> {message}</light-green>", 
           colorize=True, filter=lambda record: record["level"].name == "SUCCESS")
    

def main() -> None:
    
    print(pyfiglet.figlet_format("Infra Simulator", font="slant"))
    
    Path("configs").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    setup_logger()
    
    while True:
        action = choice(
            message="Select an option:",
            options=[
                ("provision", "Provision EC2 Machines (mock-up)"),
                ("install nginx", "Install Nginx"),
                ("exit", "Exit")
            ],
            default="provision",
            bottom_toolbar=HTML(
            " Press <b>[Up]</b>/<b>[Down]</b> to select, <b>[Enter]</b> to accept."),
        )
                
        if action == "provision":
            logger.debug("Provisioning start.")
            while True:
                ec2_instance = provision_ec2()
                ec2_instances.append(ec2_instance.model_dump())
                provision_again = prompt("\n Provision another machine? [y/N] ")
                if not provision_again.lower() in ["y","ye","yes"]:
                    print(f"\n Provisioning {len(ec2_instances)} machine(s)...\n")
                    break
            
            logger.debug("Saving config files")
            with open("configs/instances.json", "w") as f:
                json.dump(ec2_instances, f, indent=4)
            logger.debug("Provisioning end.")
                
        elif action == "install nginx":
            logger.debug("Entered Nginx install menu.")
            print()
            action = choice(
                message= "WARNING: This will actually install Nginx on your machine. Are you sure?",
                options=[
                    ("install", "Yes, install Nginx."),
                    ("back", "Back")
                ],
                default="back",
                bottom_toolbar=HTML(
                " Press <b>[Up]</b>/<b>[Down]</b> to select, <b>[Enter]</b> to accept."),
            )
            
            if action == "install":
                print()
                logger.info("Installing...")
                if shutil.which("nginx"):
                    logger.warning("Nginx is already installed.")
                    print()
                else:
                    try:    
                        result = subprocess.run(["bash", "scripts/detect_package_manager.sh"], capture_output=True,
                                       text=True, check=True)
                        package_manager = result.stdout.strip()
                    except CalledProcessError:
                        #TBD
                        break
                    logger.info(f"Detected package manager: {package_manager}")
                    subprocess.run(["bash", "scripts/install_nginx.sh", package_manager], check=True)
                    logger.info("Starting service...")
                    subprocess.run(["bash", "scripts/enable_nginx.sh"], check=True)
                    result = subprocess.run(["systemctl", "is-active", "--wait", "--quiet", "nginx"], capture_output=True,
                                            text=True, check=True)
                    logger.info("Nginx is running. Configuring...")
                    if Path("/etc/nginx/nginx.conf").exists():
                        logger.warning("File /etc/nginx/nginx.conf found. Backing up previous config...")
                        subprocess.run(["sudo", "cp", "/etc/nginx/nginx.conf", "/etc/nginx/nginx.conf.bak"], check=True)
                    subprocess.run(["sudo", "cp", "scripts/nginx_example_config.conf", "/etc/nginx/nginx.conf"], check=True)
                    logger.success("Nginx is installed and configured.")
                    logger.debug("Installation end.")
                    print()
            
            elif action == "back":
                print()
                logger.debug("User terminated installation.")
                    
        elif action == "exit":
            print()
            logger.info("Exiting...")
            return
    
    
if __name__ == "__main__":
    main()
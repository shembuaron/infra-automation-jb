import json
from enum import Enum

# Separate validation errors between pydantic and prompt_toolkit
from pydantic import BaseModel, ConfigDict, ValidationError as PydanticValidationError

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import choice
from prompt_toolkit.validation import Validator, ValidationError as PromptValidationError

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


class EC2Instance(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    name: str
    os: OSChoice
    type: TypeChoice


class NameValidator(Validator):
    def validate(self, document):
        text = document.text
        if not text.replace("_","").isalnum():
            i = 0
            for i, c in enumerate(text):
                if not c.isalnum() and c != "_":
                    break

            raise PromptValidationError(
                message="Name cannot be empty and may only conatin letters, numbers and underscores.",
                cursor_position=i
            )


def get_instance_os():
    os = choice(
        message=HTML("\n<b>Select an operating system:</b>"),
        options=available_os,
        default="amazon_linux",
        bottom_toolbar=HTML(
        " Press <b>[Up]</b>/<b>[Down]</b> to select, <b>[Enter]</b> to accept."),
    )
    return os


def get_instance_type():
    type = choice(
        message=HTML("\n<b>Select an instance type:</b>"),
        options=available_types,
        default="t3.micro",
        bottom_toolbar=HTML(
        " Press <b>[Up]</b>/<b>[Down]</b> to select, <b>[Enter]</b> to accept."),
    )
    return type


def provision_ec2():
    name = prompt(HTML("\n<b> Enter a name: </b>"), validator = NameValidator())
    os = get_instance_os()
    type = get_instance_type()
    
    try:
        ec2_instance = EC2Instance.model_validate({'name': name, 'os': os, 'type': type})
#         print(f"\n Provisioned {ec2_instance.name}: {ec2_instance.os}, {ec2_instance.type}")
        return ec2_instance
    except PydanticValidationError as err:
        print(err)
    
    
def main():
    # Pretty :)
    print(pyfiglet.figlet_format("Infra Simulator", font="slant"))
    
    # TBD add type safety
    ec2_instances = []
    
    action = choice(
        message=HTML("<b>Select an option:</b>"),
        options=[
            ("provision", "Provision EC2 Machines"),
            ("exit", "Exit")
        ],
        default="provision",
        bottom_toolbar=HTML(
        " Press <b>[Up]</b>/<b>[Down]</b> to select, <b>[Enter]</b> to accept."),
    )
    
    if action == "provision":
        while True:
            ec2_instance = provision_ec2()
            ec2_instances.append(ec2_instance.model_dump())
            provision_again = prompt(HTML("\n<b> Provision another machine? [y/N] </b>"))
            if not provision_again.lower() in ["y","ye","yes"]:
                print("Exiting...")
                break
        
        with open("configs/instances.json", "w") as f:
            json.dump(ec2_instances, f, indent=4)
        
    elif action == "exit":
        return
    
    
if __name__ == "__main__":
    main()
import logging
from log import setup_logging
import sys
from pydantic import BaseModel, ValidationError
from typing import Literal
import boto3


#Setup logger
setup_logging()
logger = logging.getLogger("infra-auto")


def get_user_input():
    
    # Get number of machines
    while True:
        machine_amount = input("Enter the amount of machines you want to privision:\n>>> ")
        try:
            machine_amount = int(machine_amount)
            if machine_amount > 0:
                break
            else:
                logger.info("Please enter a number greater than 0.")
        except ValueError:
            logger.info("Pleaes enter a valid number.")
    
    machines = []
    
    i = 0
    
    while i < machine_amount:
        machine_name = input(f"Name for machine no. {i+1}:\n>>> ")
        machine_os = input(f"OS for machine no. {i+1}:\n>>> ")
        machine_cpu = input(f"CPU for machine no. {i+1}:\n>>> ")
        machine_ram = input(f"RAM amount for machine no. {i+1}:\n>>> ")
        machine_specs = {"name": machine_name, "os": machine_os, "cpu": machine_cpu, "ram": machine_ram}
        
        try:
            machine = Machine.model_validate(machine_specs)
            machines.append(machine)
            i += 1
        except ValidationError as er:
            logger.error(er.errors()[0]["msg"])
    
    print(machines)


class Machine(BaseModel):
    name: str
    os: Literal["Linux", "Windows"]
    cpu: str
    ram: int


def main():
    
    get_user_input()
#     logger.info("info")
#     logger.debug("debug")
    
    

if __name__ == "__main__":
    main()

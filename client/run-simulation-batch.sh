#!/bin/bash

py-spy record -o  -- python sim_mesa.py 


PROFILE=run-batch-lending-pool-simulation.svg 
PROGRAM=sim_mesa.py

py-spy record -o $PROFILE -- python $PROGRAM

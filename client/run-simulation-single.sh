#!/bin/bash

PROFILE=run-single-lending-pool-simulation.svg
PROGRAM=sim_mesa_simple_case.py

py-spy record -o $PROFILE -- python $PROGRAM

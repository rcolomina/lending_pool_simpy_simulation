from lending_platform import LendingPlatform
import mesa 

## Instances of the simulation for every parameter combinatinos
params = {"n_users":range(20,21),
          "n_coins":range(3,4),
          "airdrop":range(4,5)}

results = mesa.batch_run(
    LendingPlatform,
    parameters=params,
    iterations = 1, # num. iterations for each parameter combination
    max_steps = 5,  #    
    number_processes= 16,
    display_progress = True        
)

import pandas as pd
results_df = pd.DataFrame(results)
ofname = "sim_lending_platform_results_simple_case.csv"
results_df.to_csv(ofname)

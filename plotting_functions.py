import plotly.express as px
import pandas as pd

num_runs = 100
columns1=['date', 'farm_idx', 'exposed', 'infected', 'deceased', 'num_run']
columns2=['date', 'contact_type', 'num_inf_pigs', 'num_run']
# Import data from file
results_all_long = pd.read_csv('output/multiple_runs_farm.csv', names=columns1)
results_by_compart_long = pd.read_csv('output/multiple_runs_pig.csv', names=columns2)

fig = px.line(results_all_long, x="date", y="farm_idx", color="num_run",
              title='Farm Count <br><sup>Number of Simulations: '+ str(num_runs) +'</sup>', template="plotly_white")
fig.show()
fig.write_image('output/' + str(num_runs) + '_farm_count.png')

fig2 = px.line(results_all_long, x="date", y="infected", color="num_run",
              title='Daily Infected Cases <br><sup>Number of Simulations: '+ str(num_runs) +'</sup>',
                    template="plotly_white")
fig2.show()
fig2.write_image('output/' + str(num_runs) + '_daily_inf.png')

fig3 = px.line(results_all_long, x="date", y="deceased", color="num_run",
              title='Daily Deceased <br><sup> Number of Simulations: '+ str(num_runs) +'</sup>',
                    template="plotly_white")
fig3.show()
fig3.write_image('output/' + str(num_runs) + '_daily_dec.png')

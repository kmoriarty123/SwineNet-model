import plotly.express as px
import pandas as pd

inf_tvd_idx = 1095739

# Import data from file
results_all = pd.read_csv('output/' + str(inf_tvd_idx) + '_results_all.csv')
results_all_long = pd.read_csv('output/' + str(inf_tvd_idx) + '_results_all_long.csv')
results_by_compart = pd.read_csv('output/' + str(inf_tvd_idx) + '_results_by_compart.csv')
results_by_compart_long = pd.read_csv('output/' + str(inf_tvd_idx) + '_results_by_compart_long.csv')
results_by_contact = pd.read_csv('output/' + str(inf_tvd_idx) + '_results_by_contact.csv')
results_by_contact_grp = pd.read_csv('output/' + str(inf_tvd_idx) + '_results_by_contact_grp.csv')

fig = px.line(results_all_long, x="date", y="value", color="farm_idx", facet_col="variable",
              title='Individual Farm Pig Counts by Compartment <br><sup> Farm Index Case TVD '
                    'ID: ' + str(inf_tvd_idx) + '</sup>', template="plotly_white")
fig.show()
fig.write_image('output/' + str(inf_tvd_idx) + '_time_series_by_farm.png')

fig_2 = px.line(results_by_compart_long, x="date", y="value", color="variable",
                title='Daily Sum of Number of Pigs in each Compartment<br><sup> Farm Index Case TVD ID: ' +
                      str(inf_tvd_idx) + '</sup>', template="plotly_white")

fig_2.show()
fig_2.write_image('output/' + str(inf_tvd_idx) + '_time_series_by_pigs_per_cat.png')

fig_3 = px.line(results_by_contact_grp, x="date", y="num_inf_pigs", color="contact_type",
                title='Daily Disease Transmission Numbers by Contact Type<br><sup> Farm Index Case TVD ID: ' + str(
                    inf_tvd_idx) + '</sup>', template="plotly_white")

fig_3.show()
fig_3.write_image('output/' + str(inf_tvd_idx) + '_time_series_transmission_by_contact_type.png')

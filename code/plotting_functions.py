import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import datetime

# parameters to change for reading and writing files
num_runs = 1000
start_date = datetime.date.fromisoformat('2014-01-01')

# column headings
columns1 = ['date', 'farm_count', 'exposed', 'infected', 'deceased', 'num_run']
columns2 = ['date', 'contact_type', 'num_inf_pigs', 'num_run']
columns3 = ['tvd_nr', 'year', 'farm_type', 'gde_nr', 'gde_name',
                                                  'pig_stall', 'tot_pigs', 'other_animals', 'which_animals', 'num_run']

# directories
output_dir = "../output/stochastic/" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(start_date.day) + "/"
#index_farm_file = output_dir + 'index_case_all.txt'

# Import data from file
results_all_long = pd.read_csv(output_dir + 'results_by_compart_all.txt', sep=',', names=columns1)
results_by_contact_long = pd.read_csv(output_dir + 'results_by_contact_grp_all.txt', sep=',', names=columns2)
index_farm_df = pd.read_csv(output_dir + 'index_case_all.txt', sep=',', names=columns3)
print(results_all_long)


# To separate the legend into color and line type
# TODO: fix this function so works for 4 categories (only working for g & d)
#def compress_legend(fig):
#    group1_base, group2_base = fig.data[0].name.split(",")
#    lines_marker_name = []
#    for i, trace in enumerate(fig.data):
#        part1, part2 = trace.name.split(',')
#        if part1 == group1_base:
#            lines_marker_name.append(
#                {"line": trace.line.to_plotly_json(), "marker": trace.marker.to_plotly_json(), "mode": trace.mode,
#                 "name": part2.lstrip(" ")})
#        if part2 != group2_base:
#            trace['name'] = ''
#            trace['showlegend'] = False
#        else:
#            trace['name'] = part1

    ## Add the line/markers for the 2nd group
#    for lmn in lines_marker_name:
#        lmn["line"]["color"] = "black"
#        lmn["marker"]["color"] = "black"
#        fig.add_trace(go.Scatter(y=[None], **lmn))
#    fig.update_layout(legend_title_text='',
#                      legend_itemclick=False,
#                      legend_itemdoubleclick=False)


# Line Plots of Counts

fig_farm_count =  px.line(results_all_long, x="date", y="farm_count", color="num_run",
                         title='Daily Number of Infected Farms for Each Simulation <br><sup>Number of Simulations: ' + str(
                             num_runs) + '</sup>', template="plotly_white")
fig_farm_count.show()
print("here")
fig_farm_count.write_image('../output/' + str(num_runs) + '_farm_count.png')

fig_inf_count = px.line(results_all_long, x="date", y="infected", color="num_run",
                        title='Daily Number of Infected Cases <br><sup>Number of Simulations: ' + str(
                            num_runs) + '</sup>',
                        template="plotly_white")
fig_inf_count.show()
fig_inf_count.write_image(output_dir + str(num_runs) + '_daily_inf.png')

fig_dec_count = px.line(results_all_long, x="date", y="deceased", color="num_run",
                        title='Daily Number of Deceased <br><sup> Number of Simulations: ' + str(num_runs) + '</sup>',
                        template="plotly_white")
fig_dec_count.show()
fig_dec_count.write_image(output_dir + str(num_runs) + '_daily_dec.png')

# Find the indicies of the max infected farm count for each simulation run
max_farm_count_idx = results_all_long.groupby(['num_run'])['farm_count'].transform(max) == results_all_long[
    'farm_count']
max_farm_count_dup = results_all_long[max_farm_count_idx]

print(results_all_long[max_farm_count_idx])

# To choose the first date that it occured since there are duplicates
max_farm_count_min_date_idx = max_farm_count_dup.groupby(['num_run'])['date'].transform(min) == max_farm_count_dup[
    'date']
max_farm_count = max_farm_count_dup[max_farm_count_min_date_idx]
print(max_farm_count)

# Max Infected Farm Count and Date of Reach

fig_max_farm = px.histogram(max_farm_count, x='date',
                            marginal="rug",
                            template="plotly_white",
                            nbins=12, )
# xbins=dict(start='2014-01-01', end='2014-03-30',size='D7'))
fig_max_farm.update_xaxes(range=['2014-01-01', '2014-03-30'])
fig_max_farm.show()

fig_max_farm2 = px.histogram(max_farm_count,
                             x='farm_count',
                             template="plotly_white",
                             labels=dict(x="Farm Count", y="Density"))
fig_max_farm2.show()

fig_max_farm3 = px.scatter(max_farm_count,
                           x='date',
                           y='farm_count',
                           template="plotly_white",
                           marginal_x="histogram",
                           marginal_y="histogram",
                           labels={'x': 'Earliest Date', 'y': 'Maximum Number of Infected Farms'},
                           title="Maximum Number of Infected Farms at Earliest Date for Each Simulation")

fig_max_farm3.show()
fig_max_farm3.write_image(output_dir + str(num_runs) + '_max_inf_farm_count.png')

# The proportion of farms reached for each simulation
# Take difference in start_date and date of first occurence at maximum to get "in how many days..."


# Plots by Contact Type

contact_group = results_by_contact_long.groupby(['date', 'contact_type', 'num_run'], as_index=False).agg({
    'num_inf_pigs': sum,
})

fig_contact_type = px.line(contact_group,
                           x='date',
                           y='num_inf_pigs',
                           color='contact_type',
                           line_dash='num_run',
                           template="plotly_white",
                           labels={'x': 'Date', 'y': 'Number of Infected Pigs'},
                           title="Daily Number of Infected Pigs by Contact Type")

# compress_legend(fig_contact_type)
fig_contact_type.show()

fig_contact_type2 = px.line(contact_group[contact_group['contact_type'] != 'f'],
                            x='date',
                            y='num_inf_pigs',
                            facet_row='contact_type',
                            color='num_run',
                            template="plotly_white",
                            labels={'x': 'Date', 'y': 'Number of Infected Pigs'},
                            title="Daily Number of Infected Pigs by Contact Type")

fig_contact_type2.show()
fig_contact_type2.write_image(output_dir + str(num_runs) + '_num_inf_pig_by_contact_type_time.png')

# Percent of Infected Pigs by Contact Type

print(contact_group['contact_type'].value_counts())

contact_group_sum = results_by_contact_long.groupby(['contact_type'], as_index=False).agg({
    'num_inf_pigs': sum,
})

fig_contact_type3 = px.pie(contact_group_sum, values='num_inf_pigs', names='contact_type',
             title='Percent of Infected Pigs by Contact Type')
fig_contact_type3.show()
fig_contact_type3.write_image(output_dir + str(num_runs) + '_num_inf_pig_by_contact_type_pie.png')

# Read in index_case by simulation run file
#index_farm = []  # type: List[str]

#with open(index_farm_file, 'r') as f:
#    for line in f:
#        while line != "":  # To stop when the end of file is reached

            # Ignore first line of each set
#            run_line = f.readline()
#            # Read in run line and store simulation run number
#            run_info = run_line.split(" ")
#            run_num = run_info[1].rstrip("\n")

            # Skip to next line
 #           farm_line = f.readline()
            # Store description line for output file
#            line_info = farm_line.split('[')
#            farm_info = line_info[1].rstrip("\n")
#            farm_info = farm_info.strip(']')
#            index_farm_info = farm_info.split(", ")
#            index_farm_info.append(run_num)

#            index_farm.append(index_farm_info)
            # Read next 2 lines
#            line = f.readline()
#            line = f.readline()

# Convert list to dataframe

# Join summary stats of max infected farms and first date reached with farm_info dataframe
max_farm_count_df = pd.DataFrame(max_farm_count)
max_farm_count['num_run'] = max_farm_count['num_run'].astype(int)
index_farm_df['num_run'] = index_farm_df['num_run'].astype(int)
index_farm_df['tot_pigs'] = index_farm_df['tot_pigs'].astype(float).astype(int)
max_inf_count_merge = pd.merge(index_farm_df, max_farm_count, on='num_run')
print(max_inf_count_merge)

fig_max_farm4 = px.scatter(max_inf_count_merge,
                           x='date',
                           y='farm_count',
                           template="plotly_white",
                           color='farm_type',
                           size='tot_pigs',
                           marginal_x="histogram",
                           marginal_y="histogram",
                           labels={'x': 'Earliest Date', 'y': 'Maximum Number of Infected Farms'},
                           title="Maximum Number of Infected Farms at Earliest Date by Index Case Type & Size ")

fig_max_farm4.show()
fig_max_farm4.write_image(output_dir + str(num_runs) + '_max_inf_farm_by_type_size.png')

# Merge index_farm with simulation data
index_farm_sim_data = pd.merge(index_farm_df, results_all_long, on='num_run')
print(index_farm_sim_data)

fig_max_farm5 = px.line(index_farm_sim_data, x="date", y="farm_count",
                        facet_col="farm_type",
                        color="num_run",
                        facet_col_wrap=3,
                        title='Daily Number of Infected Farms by Index Case Farm Type',
                        template="plotly_white",
                        labels={'x':'Date', 'y':'Number of Infected Farms'},)
fig_max_farm5.show()
fig_max_farm5.write_image(output_dir + str(num_runs) + '_inf_farm_count_by_farm_type.png')

# TODO Incomplete GEMEINDE
# Looking at gemeinde
#fig_contact_type3 = px.pie(index_farm_sim_data, values='num_inf_pigs', names='contact_type',
#             title='Percent of Infected Pigs by Contact Type')
#fig_contact_type3.show()
#fig_contact_type3.write_image(output_dir + str(num_runs) + '_num_inf_pig_by_contact_type_pie.png')


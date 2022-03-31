import plotly.express as px
import pandas as pd


# To separate the legend into color and line type
# TODO: fix this function so works for 4 categories (only working for g & d)
# def compress_legend(fig):
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

# Add the line/markers for the 2nd group
#    for lmn in lines_marker_name:
#        lmn["line"]["color"] = "black"
#        lmn["marker"]["color"] = "black"
#        fig.add_trace(go.Scatter(y=[None], **lmn))
#    fig.update_layout(legend_title_text='',
#                      legend_itemclick=False,
#                      legend_itemdoubleclick=False)

def plot_all_basic(output_dir,
                   num_runs,
                   columns1,
                   columns2,
                   columns3):
    # prepare dataframes for plotting
    results_all_long, results_by_contact_long, results_transmission_daily, \
    index_farm_df, max_farm_count, max_inf_count_merge = prep_dfs_for_plot(output_dir,
                                                                           columns1,
                                                                           columns2,
                                                                           columns3)

    plot_summary(results_all_long, results_transmission_daily, output_dir, num_runs)
    plot_first_date(results_all_long, max_farm_count, output_dir, num_runs)
    plot_contact_type(results_by_contact_long, output_dir, num_runs)
    plot_farm_features(index_farm_df, results_all_long, max_inf_count_merge, output_dir, num_runs)
    # plot_gemeinde()


def prep_dfs_for_plot(output_dir,
                      columns1,
                      columns2,
                      columns3):
    # Import data from file
    results_all_long = pd.read_csv(output_dir + 'results_by_compart_all.txt', sep=',', names=columns1, index_col=False)
    results_contact_type = pd.read_csv(output_dir + 'results_by_contact_grp_all.txt', sep=',', names=columns2)
    index_farm_df = pd.read_csv(output_dir + 'index_case_all.txt', sep=',', names=columns3)

    # Calculate the cumulative sum of the number of infected pigs per day (via within farm, pig2pig, indirect, geo)
    # First remove all the cases of direct transport because that is not a new pig infection case
    results_transmission = results_contact_type[results_contact_type['contact_type'] != 'd']
    # Sum the different types of spread by day per simulation run
    results_transmission_daily = results_transmission.groupby(['date', 'num_run'], as_index=False).agg({
        'num_inf_pigs': sum,
    })
    # Create a cumulative number of infected pigs per day
    results_transmission_daily['cum_inf_pigs'] = results_transmission_daily.groupby(['num_run'])[
        'num_inf_pigs'].cumsum()

    # Find the indicies of the max infected farm count for each simulation run
    max_farm_count_idx = results_all_long.groupby(['num_run'])['farm_count'].transform(max) == results_all_long[
        'farm_count']
    max_farm_count_dup = results_all_long[max_farm_count_idx]

    # To choose the first date that it occured since there are duplicates
    max_farm_count_min_date_idx = max_farm_count_dup.groupby(['num_run'])['date'].transform(min) == max_farm_count_dup[
        'date']
    max_farm_count = max_farm_count_dup[max_farm_count_min_date_idx]

    # Join summary stats of max infected farms and first date reached with farm_info dataframe
    max_farm_count['num_run'] = max_farm_count['num_run'].astype(int)
    index_farm_df['num_run'] = index_farm_df['num_run'].astype(int)
    index_farm_df['tot_pigs'] = index_farm_df['tot_pigs'].astype(float).astype(int)
    max_inf_count_merge = pd.merge(index_farm_df, max_farm_count, on='num_run')

    return results_all_long, results_contact_type, results_transmission_daily, index_farm_df, max_farm_count, max_inf_count_merge


# Plots Basic summary of infected and deceased
def plot_summary(results_all_long,
                 results_transmission_daily,
                 output_dir,
                 num_runs):
    # TODO add cumulative counts plots
    fig_farm_count = px.line(results_all_long,
                             x="date",
                             y="farm_count",
                             color="num_run",
                             title='Daily Number of Infected Farms by Simulation <br><sup>Number of Simulations: ' +
                                   str(num_runs) + '</sup>', template="plotly_white")
    fig_farm_count.show()
    fig_farm_count.write_image(output_dir + 'farm_count.png')

    fig_inf_count = px.line(results_all_long,
                            x="date",
                            y="infected",
                            color="num_run",
                            title='Daily Number of Infected Cases by Simulation <br><sup>Number of Simulations: ' +
                                  str(num_runs) + '</sup>',
                            template="plotly_white")
    fig_inf_count.show()
    fig_inf_count.write_image(output_dir + 'daily_inf.png')

    fig_dec_count = px.line(results_all_long,
                            x="date",
                            y="deceased",
                            color="num_run",
                            title='Daily Number of Deceased by Simulation <br><sup> Number of Simulations: ' +
                                  str(num_runs) + '</sup>',
                            template="plotly_white")
    fig_dec_count.show()
    fig_dec_count.write_image(output_dir + str(num_runs) + '_daily_dec.png')

    fig_cum_daily_inf = px.line(results_transmission_daily,
                                x='date',
                                y='cum_inf_pigs',
                                template="plotly_white",
                                color='num_run',
                                labels={'x': 'Date', 'y': 'Cumulative Number of Infected Pigs'},
                                title="Cumulative Number of Infected Pigs per Day per Simulation")

    fig_cum_daily_inf.show()


def plot_first_date(results_all_long, max_farm_count, output_dir, num_runs):
    # Max Infected Farm Count and Date of Reach
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


# TODO - look into these comments
#  The proportion of farms reached for each simulation
#  Take difference in start_date and date of first occurence at maximum to get "in how many days..."

def plot_contact_type(results_by_contact_long, output_dir, num_runs):
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

    contact_group_sum = results_by_contact_long.groupby(['contact_type'], as_index=False).agg({
        'num_inf_pigs': sum,
    })

    fig_contact_type3 = px.pie(contact_group_sum, values='num_inf_pigs', names='contact_type',
                               title='Percent of Infected Pigs by Contact Type')
    fig_contact_type3.show()
    fig_contact_type3.write_image(output_dir + str(num_runs) + '_num_inf_pig_by_contact_type_pie.png')


def plot_farm_features(index_farm_df, results_all_long, max_inf_count_merge, output_dir, num_runs):

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
                            labels={'x': 'Date', 'y': 'Number of Infected Farms'}, )
    fig_max_farm5.show()
    fig_max_farm5.write_image(output_dir + str(num_runs) + '_inf_farm_count_by_farm_type.png')


def plot_gemeinde():
    # TODO Incomplete GEMEINDE
    # Looking at gemeinde
    # fig_contact_type3 = px.pie(index_farm_sim_data, values='num_inf_pigs', names='contact_type',
    #             title='Percent of Infected Pigs by Contact Type')
    # fig_contact_type3.show()
    # fig_contact_type3.write_image(output_dir + str(num_runs) + '_num_inf_pig_by_contact_type_pie.png')
    return

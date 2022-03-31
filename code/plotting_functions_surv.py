import plotly.express as px
import pandas as pd


def prep_dfs_for_slaughter_plot(output_dir, column_names, results_transmission_daily):
    # Import data from file
    results_detect = pd.read_csv(output_dir + 'results_inspected_farms_all.txt', sep=',', names=column_names)

    # Group detected results by date
    results_detect_daily = results_detect.groupby(['num_run', 'date'], as_index=False).agg({
        'n_detect': sum,
    })

    # calculate the sum of pigs that were detected each day
    # Interested in the first time a pig was detected
    results_detect_daily_grp = results_detect_daily.groupby('num_run')
    results_detect_first = results_detect_daily_grp.first()

    # Combine date of first detect with cumulative infected pigs
    combo_df = pd.merge(results_transmission_daily, results_detect_first, how='inner', on=['num_run', 'date'])
    combo_df["num_run"] = combo_df["num_run"].astype(str)

    return results_detect_daily, results_detect_first, combo_df

def prep_dfs_for_net_plot(output_dir, columns4, results_transmission_daily):
    # Import data from file
    results_detect = pd.read_csv(output_dir + 'results_inspected__all.txt', sep=',', names=columns4)

    # Group detected results by date
    results_detect_daily = results_detect.groupby(['num_run', 'date'], as_index=False).agg({
        'n_detect': sum,
    })

    # calculate the sum of pigs that were detected each day
    # only care about when at least one pig was detected
    # results_detect_daily = results_detect_daily[results_detect_daily['n_dis_inf'] > 0]
    # results_inspect_grp['cum_detect_pigs'] = results_detect_daily.groupby(['num_run'])['n_dis_inf'].cumsum()
    # Interested in the first time a pig was detected
    results_detect_daily_grp = results_detect_daily.groupby('num_run')
    results_detect_first = results_detect_daily_grp.first()

    # Combine date of first detect with cumulative infected pigs
    combo_df = pd.merge(results_transmission_daily, results_detect_first, how='inner', on=['num_run', 'date'])
    combo_df["num_run"] = combo_df["num_run"].astype(str)

    return results_detect_daily, results_detect_first, combo_df


def plot_slaughter_surv(results_detect_daily, results_detect_first, combo_df, start_date, end_date):
    # Plot the number of detected pigs per day
    fig_detect_daily = px.line(results_detect_daily,
                               x='date',
                               y='n_detect',
                               color='num_run',
                               template="plotly_white",
                               labels={'x': 'Date', 'y': 'Number of Detected Pigs'},
                               title="Slaughterhouse Surveillance: Daily Number of Detected Pigs")

    fig_detect_daily.show()

    fig_date_first_detect = px.histogram(results_detect_first,
                                         x='date',
                                         marginal="rug",
                                         template="plotly_white",
                                         title="Slaughterhouse Surveillance: Date of First Detection")

    fig_date_first_detect.update_xaxes(range=[start_date, end_date])
    fig_date_first_detect.show()

    fig_inf_pigs_until_detect = px.scatter(combo_df,
                                           x='date',
                                           y='cum_inf_pigs',
                                           template="plotly_white",
                                           color='num_run',
                                           labels={'x': 'Date', 'y': 'Cumulative Number of Infected Pigs'},
                                           title="Slaughterhouse Surveillance: Cumulative Number of Infected Pigs Until First Detection")

    fig_inf_pigs_until_detect.show()


def prep_dfs_for_farmer_plot(output_dir, columns5, results_transmission_daily):
    # Import data from file
    results_detect = pd.read_csv(output_dir + 'results_inspected_farms_all.txt', sep=',', names=columns5)

    # Group detected results by date
    results_detect_daily = results_detect.groupby(['num_run', 'date'], as_index=False).agg({
        'n_detect': sum,
    })

    # Interested in the first time a pig was detected
    results_detect_daily_grp = results_detect_daily.groupby('num_run')
    results_detect_first = results_detect_daily_grp.first()

    # Combine date of first detect with cumulative infected pigs
    combo_df = pd.merge(results_transmission_daily, results_detect_first, how='inner', on=['num_run', 'date'])
    combo_df["num_run"] = combo_df["num_run"].astype(str)

    return results_detect_daily, results_detect_first, combo_df


def plot_farmer_surv(results_detect_daily, results_detect_first, combo_df, start_date, end_date):
    # Plot the number of detected pigs per day
    fig_detect_daily = px.line(results_detect_daily,
                               x='date',
                               y='n_detect',
                               color='num_run',
                               template="plotly_white",
                               labels={'x': 'Date', 'y': 'Number of Detected Pigs'},
                               title="Farmer Surveillance: Daily Number of Detected Pigs")

    fig_detect_daily.show()

    fig_date_first_detect = px.histogram(results_detect_first,
                                         x='date',
                                         marginal="rug",
                                         template="plotly_white",
                                         title="Farmer Surveillance: Date of First Detection")

    fig_date_first_detect.update_xaxes(range=[start_date, end_date])
    fig_date_first_detect.show()

    fig_inf_pigs_until_detect = px.scatter(combo_df,
                                           x='date',
                                           y='cum_inf_pigs',
                                           template="plotly_white",
                                           color='num_run',
                                           labels={'x': 'Date of First Detection',
                                                   'y': 'Cumulative Number of Infected Pigs'},
                                           title="Farmer Surveillance: Cumulative Number of Infected Pigs at First Detection")

    fig_inf_pigs_until_detect.show()


def plot_compare_surv(slaughter_surv_df,
                      farmer_surv_df,
                      network_surv_df,
                      results_detect_first_slaughter,
                      results_detect_first_farmer,
                      start_date, end_date):
    # add label to dataframes
    slaughter_surv_df['surv_type'] = 'slaughter'
    farmer_surv_df['surv_type'] = 'farmer'

    # combine dataframes
    combo_surv = pd.concat([slaughter_surv_df, farmer_surv_df])

    fig_inf_pigs_until_detect = px.scatter(combo_surv,
                                           x='date',
                                           y='cum_inf_pigs',
                                           template="plotly_white",
                                           color='surv_type',
                                           labels={'x': 'Date of First Detection',
                                                   'y': 'Cumulative Number of Infected Pigs'},
                                           title="Surveillance Comparison: Cumulative Number of Infected Pigs at First Detection")

    fig_inf_pigs_until_detect.show()

    # add label to dataframes
    results_detect_first_slaughter['surv_type'] = 'slaughter'
    results_detect_first_farmer['surv_type'] = 'farmer'
    # combine dataframes
    combo_detect_first = pd.concat([results_detect_first_slaughter, results_detect_first_farmer])

    fig_date_first_detect = px.histogram(combo_detect_first,
                                         x='date',
                                         marginal="rug",
                                         template="plotly_white",
                                         color='surv_type',
                                         title="Surveillance Comparison: Date of First Detection")

    fig_date_first_detect.update_xaxes(range=[start_date, end_date])
    fig_date_first_detect.show()

def summarize_results_comp(output_dir,columns_compart):
    # Import data from file
    results_compart = pd.read_csv(output_dir + 'results_by_compart_all.txt', sep=',', names=columns_compart)

    # Find max number of infected farms to see how many never "took off"
    results_compart_max_farm = results_compart.groupby(['num_run'], as_index=False).agg({
        'farm_count': ['max'],
    })

    results_compart_max_farm.columns = ['date, max_farm_count']

    # Group detected results by date
    results_compart_sum = results_compart.groupby(['date'], as_index=False).agg({
        'farm_count': ['mean', 'std'],
        'infected':['mean','std'],
        'deceased': ['mean', 'std'],
        'detected': ['mean', 'std']
    })

    results_compart_sum.columns = ['date', 'farm_inf_mean', 'farm_inf_std',
                                   'infected_mean', 'infected_std',
                                   'deceased_mean', 'deceased_std',
                                   'detected_mean', 'detected_std']

    results_compart_sum['s_type'] = output_dir.rsplit('/', 2)[1]

    return results_compart_sum, results_compart_max_farm


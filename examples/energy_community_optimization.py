import pandas as pd
from gse.gse import create_model, instantiate_model, solve_model, get_results
from gse.gse_input import create_input
import matplotlib.pyplot as plt
import plotly.express as px


# Get COIN-OR Cbc solver from https://github.com/coin-or/Cbc/releases. Other linear programming solvers can also work.

# Set the solver path
solver = {'name':"cbc", 'path':"Path to solver"}

# Import data
df_load = pd.read_csv('./examples/data/load.csv', index_col = 0, parse_dates = True)
df_pv = pd.read_csv('./examples/data/pv.csv', index_col = 0, parse_dates = True)
df_grid = pd.read_csv('./examples/data/grid.csv', index_col = 0, parse_dates = True)/100 # Convert €¢/kWh --> €/kWh
df_battery = pd.read_csv('./examples/data/battery.csv', index_col = 0)


#%% Data plots

fig = px.line(df_load, x=df_load.index, y=df_load.columns)
fig.update_xaxes(minor=dict(ticks="inside", showgrid=True))
fig.update_layout(
    title = dict(text='Electricity consumption'),
    yaxis_title=dict(text='Load [kWh]'),
    xaxis_title=dict(text='Date'),
    legend_title_text='House'
)
fig.show()
fig.write_html('examples/img/load.html')


fig = px.line(df_pv, x=df_pv.index, y=df_pv.columns)
fig.update_xaxes(minor=dict(ticks="inside", showgrid=True))
fig.update_layout(
    title = dict(text='Solar energy'),
    yaxis_title=dict(text='PV [kWh]'),
    xaxis_title=dict(text='Date'),
    legend_title_text='House'
)
fig.show()
fig.write_html('examples/img/pv.html')


fig = px.line(df_grid, x=df_grid.index, y=df_grid.columns)
fig.update_xaxes(minor=dict(ticks="inside", showgrid=True))
fig.update_layout(
    title = dict(text='Grid costs'),
    yaxis_title=dict(text='Cost [€/kWh]'),
    xaxis_title=dict(text='Date'),
    legend_title_text=''
)
fig.show()
fig.write_html('examples/img/grid_costs.html')

print(df_battery)


#%% Create and solve the energy community optimization model

# Create data input for model
model_data = create_input(df_load,df_pv,df_grid,df_battery)
# Create model
mdl = create_model()
# Instantiate model with data
m = instantiate_model(mdl, model_data)
# Solve model
s = solve_model(m, solver) 
# Get solution as python dictionary
sd = get_results(s)


#%% Get solution into dataframes

df_power_buy = pd.DataFrame(index = df_load.index, columns=sd['power_buy'].keys())
for c in sd['power_buy'].keys():
    df_power_buy.loc[:,c] = sd['power_buy'][c]

df_power_sell = pd.DataFrame(index = df_load.index, columns=sd['power_sell'].keys())
for c in sd['power_sell'].keys():
    df_power_sell.loc[:,c] = sd['power_sell'][c]

df_battery_soc = pd.DataFrame(index = df_load.index, columns=sd['battery_soc'].keys())
for c in sd['battery_soc'].keys():
    df_battery_soc.loc[:,c] = sd['battery_soc'][c]

df_battery_charge = pd.DataFrame(index = df_load.index, columns=sd['battery_charge'].keys())
for c in sd['battery_charge'].keys():
    df_battery_charge.loc[:,c] = sd['battery_charge'][c]

df_battery_discharge = pd.DataFrame(index = df_load.index, columns=sd['battery_discharge'].keys())
for c in sd['battery_discharge'].keys():
    df_battery_discharge.loc[:,c] = sd['battery_discharge'][c]

df_cost_energy = pd.DataFrame(index = df_load.index, data=sd['cost_energy'])
df_cost_grid = pd.DataFrame(index = df_load.index, data=sd['cost_grid'])
df_cost_total = df_cost_energy + df_cost_grid


#%% Plots

# The following plot shows the time-series of the houses energy imports
fig = px.line(df_power_buy, x=df_power_buy.index, y=df_power_buy.columns)
fig.update_xaxes(minor=dict(ticks="inside", showgrid=True))
fig.update_layout(
    title = dict(text='Energy trading - Imports'),
    yaxis_title=dict(text='Energy [kWh]'),
    xaxis_title=dict(text='Date'),
    legend_title_text='House'
)
fig.show()
fig.write_html('examples/img/energy_imports.html')


# The following plot shows the time-series of the houses energy exports
fig = px.line(df_power_sell, x=df_power_sell.index, y=df_power_sell.columns)
fig.update_xaxes(minor=dict(ticks="inside", showgrid=True))
fig.update_layout(
    title = dict(text='Energy trading - Exports'),
    yaxis_title=dict(text='Energy [kWh]'),
    xaxis_title=dict(text='Date'),
    legend_title_text='House'
)
fig.show()
fig.write_html('examples/img/energy_exports.html')


# The following plot shows the time-series of the batteries state-of-charge
fig = px.line(df_battery_soc, x=df_battery_soc.index, y=df_battery_soc.columns)
fig.update_xaxes(minor=dict(ticks="inside", showgrid=True))
fig.update_layout(
    title = dict(text='Battery State-of-Charge'),
    yaxis_title=dict(text='SoC [kWh]'),
    xaxis_title=dict(text='Date'),
    legend_title_text='House'
)
fig.show()
fig.write_html('examples/img/battery_soc.html')


# The following plot shows the time-series of the operation costs. These include the energy cost/profit from buying/selling energy, the cost of the grid and the total cost as the sum of the energy and grid costs.
fig = px.line(df_cost_energy, x=df_cost_energy.index, y=[df_cost_energy[0], df_cost_grid[0], df_cost_total[0]])
fig.update_xaxes(minor=dict(ticks="inside", showgrid=True))
fig.update_layout(
    title = dict(text='Energy trading costs'),
    yaxis_title=dict(text='Cost [€]'),
    xaxis_title=dict(text='Date'),
    legend_title_text=''
)
for i,trace in enumerate (fig.data):
    trace.update(name=['Energy cost','Grid cost','Total cost'][i])
fig.show()
fig.write_html('examples/img/operation_costs.html')


# The total costs over the whole operation period (Oct 2018) are:
print('Energy cost:', df_cost_energy.sum().round(2)[0], '€')
print('Grid cost:', df_cost_grid.sum().round(2)[0], '€')
print('Total cost:', df_cost_total.sum().round(2)[0], '€')
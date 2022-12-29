import numpy as np
import pandas as pd

def temp_set_to_df(temps):
    sorted_temps = list(reversed(sorted(temps)))
    table = pd.DataFrame()
    table["T_high"] = sorted_temps[:-1]
    table["T_low"] = sorted_temps[1:]
    return table

def TI_method(input, min_T, pinch):
    # Calculate delta T and H for given hot and cold streams
    input["delta_T"] = input["T_Hot"] - input["T_Cold"]
    input["C"] = input["delta_H"] / input["delta_T"]

    # Make adjust temp column for TI method
    input["adj_T_Hot"] = np.where(input.Stream.str.contains("H"), input["T_Hot"] - min_T, input["T_Hot"])
    input["adj_T_Cold"] = np.where(input.Stream.str.contains("H"), input["T_Cold"] - min_T, input["T_Cold"])
    input["range"] = list(zip(input.adj_T_Hot, input.adj_T_Cold))
    input["C"] = np.where(input.Stream.str.contains("C"),input["C"] * -1 ,input["C"])

    input = input.set_index("Stream")
    print("INPUT")
    print("--------")
    print(input)
    print("______________________________________________________________________________________")

    # Gather hot and cold temps
    adj_hot_temp = input.adj_T_Hot.tolist()
    adj_cold_temp = input.adj_T_Cold.tolist()

    # combine all temps into one list
    all_temp = set(adj_hot_temp + adj_cold_temp)

    # make template of TI table based on the temperatures
    TI_table = temp_set_to_df(all_temp)
    
    # for every stream determine if within the temp ranges
    for stream in input.index.tolist():
        range = input.loc[stream,"range"]
        TI_table[stream] = np.where((TI_table["T_high"] <= range[0]) & (TI_table["T_low"] >= range[1]), input.loc[stream,"C"], 0)

    # Calculate delta T, C, and delta H
    TI_table["delta_T"] = TI_table["T_high"] - TI_table["T_low"]
    TI_table["C"] = TI_table.iloc[:,2:-1].sum(axis=1)
    TI_table["delta_H"] = TI_table["delta_T"] * TI_table["C"]

    # Calculate residual columns
    TI_table["Residual"] = TI_table.delta_H.cumsum()
    min_residual_index = TI_table[['Residual']].idxmin()
    min_residual = float(TI_table.iloc[min_residual_index,-1])*-1

    TI_table["Residual_ADJ"] = TI_table["Residual"] + min_residual

    # Determine Pinch
    if pinch:
        # Print ultlity information and pinch point
        print("Min Hot Utility:", min_residual)
        print("Min Cold Utility:",TI_table.iloc[-1,-1])
        pinch_cold_temp = float(TI_table.iloc[min_residual_index,1])
        print("Pinch Temps:", (pinch_cold_temp + min_T, pinch_cold_temp))
        print("______________________________________________________________________________________")

    # print("TI Table")
    # print("--------")
    # print(TI_table.replace(0,"_"))
    # print("______________________________________________________________________________________")

    return TI_table

# def CC_setup(stream_data, check_table):
#     temps = set(stream_data["T_Hot"].tolist() + stream_data["T_Cold"].tolist())
#     table = temp_set_to_df(temps)

#     # for every stream determine if within the temp ranges
#     for stream in check_table.index.tolist():
#         range = check_table.loc[stream,"range"]
#         table[stream] = np.where((table["T_high"] <= range[0]) & (table["T_low"] >= range[1]), input.loc[stream,"C"], 0)

#     return table

def CC_method(input):
    # Calculate delta T and H for given hot and cold streams
    input["delta_T"] = input["T_Hot"] - input["T_Cold"]
    input["C"] = input["delta_H"] / input["delta_T"]
    input["range"] = list(zip(input.T_Hot, input.T_Cold))

    hot_streams = input[input.Stream.str.contains("H")].set_index("Stream")
    hot_temps = set(hot_streams["T_Hot"].tolist() + hot_streams["T_Cold"].tolist())

    cold_streams = input[input.Stream.str.contains("C")].set_index("Stream")
    cold_temps = set(cold_streams["T_Hot"].tolist() + cold_streams["T_Cold"].tolist())

    hot_table = temp_set_to_df(hot_temps)
    cold_table = temp_set_to_df(cold_temps)

    # Hot Temp Table
    hot_table["Streams"] = ""
    for stream in hot_streams.index.tolist():
        range = hot_streams.loc[stream,"range"]
        hot_table[stream] = np.where((hot_table["T_high"] <= range[0]) & (hot_table["T_low"] >= range[1]), hot_streams.loc[stream,"C"], 0)
        hot_table["Streams"] = np.where((hot_table["T_high"] <= range[0]) & (hot_table["T_low"] >= range[1]), hot_table["Streams"] + "," + stream, hot_table["Streams"])

    # Cold Temp Table
    cold_table["Streams"] = ""
    for stream in cold_streams.index.tolist():
        range = cold_streams.loc[stream,"range"]
        cold_table[stream] = np.where((cold_table["T_high"] <= range[0]) & (cold_table["T_low"] >= range[1]), cold_streams.loc[stream,"C"], 0)
        cold_table["Streams"] = np.where((cold_table["T_high"] <= range[0]) & (cold_table["T_low"] >= range[1]), cold_table["Streams"] + "," + stream, cold_table["Streams"])

    # Make table combining hot and cold streams
    CC_table = pd.concat([hot_table,cold_table])

    # Calculate delta T, C, and delta H
    CC_table["delta_T"] = CC_table["T_high"] - CC_table["T_low"]
    CC_table["C"] = CC_table.iloc[:,2:-1].sum(axis=1)
    CC_table["delta_H"] = CC_table["delta_T"] * CC_table["C"]

    column_to_move = CC_table.pop("Streams")
    CC_table.insert(len(CC_table.columns), "Streams", column_to_move)

    return CC_table

def calcualte_delta_H(pinch, hot, cold, deltaH):
    frac = (hot-pinch) / (hot-cold)
    HOT = frac*deltaH
    COLD = deltaH - HOT
    print(f"\u0394HOT: {HOT}, \u0394COLD {COLD}")

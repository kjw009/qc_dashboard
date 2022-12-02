# File sharing and data handling modules
import os
import pandas as pd
import numpy as np
import re

"""
Changes directory to product directory in the wishaw enewall network drive
Reads product QC data for the corresponding product passed as the argument
Extracts conforming limits
Removes unwanted columns and rows
Creates a Failure code column and use conforming limits to assign each batch reason of failure
Creates a result column to assign each batch pass or fail result using conforming limits
Returns dataframe of the corresponding product as well as its limits

"""
def process_product_data(filename):
    # Declare the orignal working directory path as a variable
    owd = os.getcwd()
    # Path to product QC spreadsheets
    path = 'G:\Quality Control\Quality Management System\QC Docs\QC\QC Check Sheets\QC Completed Check Sheets\Products'
    # Change working directory
    print(f"\nChanging Directory to {path}")
    os.chdir(path)

    print(f"\nReading {filename}")
    df = pd.read_excel(filename, skiprows=5)
    
    # Extract conforming limits
    conforming_limits = df.iloc[1]
    # Remove non-conforming Limits column and nulls
    conforming_limits.drop([df.columns[0]], inplace=True)
    conforming_limits.dropna(inplace=True)
    # Convert series to dict. Key: Column label => Limits
    conforming_limits.to_dict()
    for key in conforming_limits.keys():
        # Regex matches the numbers only in the cell. Ex: 90-120 => [90,120]
        conforming_limits[key] = re.findall(r'\d+', conforming_limits[key])

    # Remove unwanted columns and rows
    df = df.drop([0, 1]).reset_index(drop=True)
    # Remove columns that have a floating datatype label
    df = df[[col for col in df.columns if not isinstance(col, float)]]
    # Remove unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    # Drop rows where they don't have a date of manufacture/testing recorded
    df.dropna(subset=[df.columns[0]], inplace=True)
    
    # Create a new Failure code column if there isn't one already
    if 'Failure code' not in df.columns:
        df['Failure code'] = pd.Series()

    # Make failure codes all lower case
    try:
        df['Failure code'] = df["Failure code"].str.lower()
    except AttributeError:
        pass

    # Handle missing values.
    df.replace([r'[^\w\s]'], np.nan, regex=True, inplace=True)
    # Spread values equal to 1 results in Fail
    results = []
    for index, spread in enumerate(df['Spread /mm']):
            if spread == 1:
                results.append("Fail")
            else:
                results.append("Pass")
    # Append results to Result column
    df['Result'] = results

    # Assign correct Dtypes to columns. Convert the "Data of manufacture" column to a datetime Dtype
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors="raise")
    # Set "Data of Manufacture" as the index
    df.set_index(df.iloc[:, 0], inplace=True)
    # Assign Material Colour and Result column to category Dtypes
    df['Material Colour'] = df['Material Colour'].str.strip().astype('category')
    df["Material Colour"].fillna(
        df["Material Colour"].mode()[0], inplace=True)
    # Convert Object Dtype columns to float or str.
    df = df.convert_dtypes()

    df['Failure code'] = df['Failure code'].astype("string")

    # Use conforming limits to determine sample failure
    for key in conforming_limits.keys():
        spec = key.split(" ")[0].strip("/")
        # Between an upper and lower limit
        if key in df.columns and len(conforming_limits[key]) == 2:
            for index, value in enumerate(df[key]):
                if not pd.isnull(value) and not pd.isnull(df['Spread /mm'][index]):
                    if (value < float(conforming_limits[key][0])):
                        df['Result'][index] = "Fail"
                        if pd.isnull(df["Failure code"][index]):
                            if spec == "Spread":
                                df["Failure code"][index] = "LOW FLOW"
                            else:
                                df['Failure code'][index] = f"LOW {spec.upper()}"
                        elif f"LOW {spec.upper()}" not in [code.upper() for code in df['Failure code'][index].split(",")]:
                            if spec == "Spread":
                                    if "LOW FLOW" not in [code.upper() for code in df['Failure code'][index].split(",")]:
                                        df["Failure code"][index] = df["Failure code"][index] + ",LOW FLOW"
                            else:
                                df["Failure code"][index] = df["Failure code"][index] + f",LOW {spec.upper()}"
                    elif (value > float(conforming_limits[key][1])):
                        df['Result'][index] = "Fail"
                        if pd.isnull(df["Failure code"][index]):
                            if spec == "Spread":
                                df["Failure code"][index] = "HIGH FLOW"
                            else:
                                df['Failure code'][index] = f"HIGH {spec.upper()}"
                        elif f"HIGH {spec.upper()}" not in [code.upper() for code in df['Failure code'][index].split(",")]:
                            if spec == "Spread":
                                if "HIGH FLOW" not in [code.upper() for code in df['Failure code'][index].split(",")]:
                                    df["Failure code"][index] = df["Failure code"][index] + ",HIGH FLOW"
                            else:
                                df["Failure code"][index] = df["Failure code"][index] + f",HIGH {spec.upper()}"
                # If cells are empty, the value becomes Nan and can't be compared with float using >. Make the error an exception
        elif key in df.columns and len(conforming_limits[key]) == 1:
            for index, value in enumerate(df[key]):
                if not pd.isnull(value) and pd.isnull(df['Spread /mm'][index]):
                    if value < float(conforming_limits[key][0]):
                        df['Result'][index] = "Fail"
                        if pd.isnull(df["Failure code"][index]):
                            df['Failure code'][index] = f"LOW {spec.upper()}"
                        elif f"LOW {spec.upper()}" not in [code.upper() for code in df['Failure code'][index].split(",")]:
                            df["Failure code"][index] = df["Failure code"][index] + f",LOW {spec.upper()}" 
                            
    # Change the result value for each batch if the provision result is different
    if "Provisional result" in df.columns:
        for index, p_result in enumerate(df['Provisional result']):
            if str(p_result).upper() == "FAIL":
                df['Result'][index] = "Fail"
                
    # Change back to original working directory. Allows dash server to run as this file is not found in the wishaw network drive.
    os.chdir(owd)
    
    #df.to_csv("S:\Operations\QC\QE Projects/exp.csv")
    
    # Return df
    return df, conforming_limits.to_dict()
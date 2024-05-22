"""
 Title:         Input / Output
 Description:   Reading / writing functions
 Author:        Janzen Choi

"""

# Libraries
import csv, math, os
import pandas as pd
from itertools import zip_longest
from ebsd_mapper.helper.general import round_sf, try_float

def get_file_path_writable(file_path:str, extension:str):
    """
    Appends a number after a path if it is not writable

    Parameters:
    * `file_path`: Path to file without the extension
    * `extension`: The extension for the file
    """
    new_file_path = f"{file_path}.{extension}"
    if not os.path.exists(new_file_path):
        return new_file_path
    index = 1
    while True:
        try:
            with open(new_file_path, 'a'):
                return new_file_path
        except IOError:
            new_file_path = f"{file_path} ({index}).{extension}"
            index += 1

def get_file_path_exists(file_path:str, extension:str):
    """
    Appends a number after a path if it exists

    Parameters:
    * `file_path`: Path to file without the extension
    * `extension`: The extension for the file
    """
    new_file_path = f"{file_path}.{extension}"
    index = 1
    while os.path.exists(new_file_path):
        new_file_path = f"{file_path} ({index}).{extension}"
        index += 1
    return new_file_path

def csv_to_dict(csv_path:str) -> dict:
    """
    Converts a CSV file into a dictionary
    
    Parameters:
    * `csv_path`:  The path to the CSV file
    
    Returns the dictionary
    """
    data_dict = {}
    with open(csv_path, newline="") as csvfile:
        csvreader = csv.reader(csvfile)
        headers = next(csvreader)
        for header in headers:
            data_dict[header] = []
        for row in csvreader:
            for header, value in zip(headers, row):
                data_dict[header].append(try_float(value))
        for header in headers:
            if len(data_dict[header]) == 1:
                data_dict[header] = data_dict[header][0]
        return data_dict

def dict_to_csv(data_dict:dict, csv_path:str, add_header:bool=True) -> None:
    """
    Converts a dictionary to a CSV file
    
    Parameters:
    * `data_dict`: The dictionary to be converted
    * `csv_path`:  The path that the CSV file will be written to
    * `header`:    Whether to include the header or not
    """
    headers = list(data_dict.keys())
    values = list(zip_longest(*data_dict.values(), fillvalue=""))
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if add_header:
            writer.writerow(headers)
        writer.writerows(values)

def read_excel(excel_path:str, sheet:str, column:int) -> list:
    """
    Reads an excel file

    Parameters:
    * `excel_path`: The path to the excel file
    * `sheet`:      The name of the sheet to read from
    * `column`:     The column index

    Returns a list of values corresponding to that column
    """
    data_frame = pd.read_excel(excel_path, sheet_name=sheet)
    data_list = list(data_frame.iloc[:,column])
    data_list = list(filter(lambda x: not math.isnan(x), data_list))
    data_list = [round_sf(data, 8) for data in data_list]
    return data_list

def safe_mkdir(dir_path:str) -> None:
    """
    For safely making a directory

    Parameters:
    * `dir_path`: The path to the directory
    """
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        pass

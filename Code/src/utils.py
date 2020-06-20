import os

import pandas as pd


def malwares_family(csv_path):
    df = pd.read_excel(csv_path)
    family_dict = {}

    # some excel don't have column names
    family_dict[df.columns.values[0]] = df.columns.values[3]
    for index in range(len(df)):
        family_dict[df.iloc[index, 3]] = df.iloc[index, 0]

    return family_dict


def apts_family(dir):
    family_dict = {}
    for fam_name in os.listdir(dir):
        for sample in os.listdir(os.path.join(dir, fam_name)):
            family_dict[sample] = fam_name
    return family_dict







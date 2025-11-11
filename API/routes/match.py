import pandas as pd
import os

current_dir = os.path.dirname(__file__)  # Directory of the current script
data_file_path = os.path.join(current_dir, "../../Data/fra_cleaned.csv")

df = pd.read_csv(data_file_path, sep=';', encoding='latin-1')

def match_to_perfumes(probable_notes):
    '''Returns perfumes that match the given notes'''
    
    


    
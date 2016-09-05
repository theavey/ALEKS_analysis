# todo figure out how to import without polluting namespace
import pandas as pd
import numpy as np


def hex_to_bin_state(state):
    hex_num = state[1:-3]
    # todo use this domain import?
    domain = state[-1]
    valid_last_digits = int(state[-3])
    if valid_last_digits not in range(1,5):
        raise IndexError('Check digit value was {} but should be between 1 and 4'.format(valid_last_digits))
    length = len(hex_num) * 4 - (4 - valid_last_digits)
    if valid_last_digits == 4:
        end_crop = None
    else:
        end_crop = valid_last_digits - 4
    binary_state = (bin(int(hex_num, 16))[2:end_crop]).zfill(length)
    return binary_state


def domain_to_list(file_name):
    with open(file_name, 'r') as domain:
        domain_list = []
        for item in domain:
            domain_list.append(item.strip())
    return domain_list


def import_domains(base_name):
    import glob
    domain_files = glob.glob(base_name+'*')
    domains_dict = {}
    for domain in domain_files:
        domains_dict[domain] = domain_to_list(domain)
    return domains_dict


def bin_states(dataframe, domain_dict):
    domain_number = dataframe.iat[0,0][-1]
    domain_name = 'genchema.' + domain_number + '.dom'
    domain = domain_dict[domain_name]
    output_array = np.zeros([len(dataframe.index), len(domain)])
    grades = dataframe['grade']
    for row in dataframe.itertuples():
        output_array[row[0]] = list(hex_to_bin_state(row[1]))
    state_frame = pd.DataFrame(output_array.astype(bool), columns=domain)
    return state_frame.join(grades)

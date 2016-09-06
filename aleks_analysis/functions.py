# todo figure out how to import without polluting namespace
import pandas as pd
import numpy as np
import re


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
    num_rows = len(dataframe.index)
    domain_number = dataframe.iat[0,0][-1]
    domain_name = 'genchema.' + domain_number + '.dom'
    index = make_column_multiindex(domain_name, domain_dict)
    other_index = pd.MultiIndex.from_tuples((('other', 'grade', 'grade'),
                                             ('other', 'domain', 'name')))
    output_array = np.zeros([len(dataframe.index), len(index)])
    grades = pd.DataFrame(np.array([dataframe['grade'],[domain_name]*num_rows]).transpose(),
                          columns=other_index)
    for row in dataframe.itertuples():
        output_array[row[0]] = list(hex_to_bin_state(row[1]))
    state_frame = pd.DataFrame(output_array.astype(bool), columns=index)
    return state_frame.join(grades)


def make_column_multiindex(domain_name, domain_dict):
    domain = domain_dict[domain_name]
    topics = []
    item_count = len(domain)
    for item in domain:
        topic_match = re.match('[a-zA-Z]+', item)
        try:
            topic = topic_match.group(0)
        except AttributeError:
            raise InputError('topic not found in item name: {}'.format(item))
        topics.append(topic)
    tuples = list(zip(('state',)*item_count, topics, domain))
    return pd.MultiIndex.from_tuples(tuples, names=['type', 'topic', 'item'])

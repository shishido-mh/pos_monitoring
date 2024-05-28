import pandas as pd

class Pivot:
    @staticmethod
    def pivot_df(df):
        pivoted = df.pivot_table(index='time',
                                 columns='status',
                                 values='f0_', fill_value=0)
        
        pivoted['total'] = pivoted.sum(axis=1)
        pivoted['success_rate'] = pivoted['approved'] / (pivoted['backend_reversed'] + pivoted['reversed'] +
                                                          pivoted['denied'] + pivoted['failed'] + pivoted['approved'])
        pivoted['denial_rate'] = pivoted['denied'] / (pivoted['backend_reversed'] + pivoted['reversed'] +
                                                      pivoted['denied'] + pivoted['failed'] + pivoted['approved'])
        pivoted['reversal_rate'] = (pivoted['reversed'] + pivoted['backend_reversed']) / (pivoted['backend_reversed'] +
                                                                                             pivoted['reversed'] +
                                                                                             pivoted['denied'] +
                                                                                             pivoted['failed'] +
                                                                                             pivoted['approved'])
        pivoted['failure_rate'] = pivoted['failed'] / (pivoted['backend_reversed'] + pivoted['reversed'] +
                                                       pivoted['denied'] + pivoted['failed'] + pivoted['approved'])
        pivoted = pivoted.reset_index(drop=False)
        pivoted['hour'] = pivoted['time'].str[0:2].astype(int)
        pivoted['minute'] = pivoted['time'].str[-2:].astype(int)
        pivoted = pivoted.fillna(0)
        return pivoted

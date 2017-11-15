#  subplotable.py
#  by Behnam Heydarshahi, October 2017
#
#  This class models data needed for a single sub plot

class SubPlotable:
    def __init__(self, label, x_values, y_values, y_std_error_values):
        self.label = label
        self.x_values = x_values
        self.y_values = y_values
        self.y_std_err_values = y_std_error_values

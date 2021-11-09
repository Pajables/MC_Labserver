import re


def remove_column_formatting(columns):
    for i in range(len(columns)):
        column = columns[i]
        match = re.search(r"\$\$", column)
        unit = column[match.span()[1]:]
        column = column[:match.span()[0]]
        column = column.replace('_', ' ')
        columns[i] = column + " [" + unit + "]"


raw_columns = ["saclli_cdadf$$ml", "param2_name$$units"]
print(raw_columns)
remove_column_formatting(raw_columns)
print(raw_columns)
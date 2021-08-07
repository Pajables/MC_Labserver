

def split_results(data, results_per_page):
    i = 0
    split_data = []
    rows = data.fetchall()
    while len(rows) > results_per_page:
        split_data.append(rows[0:results_per_page])
        rows = rows[results_per_page:]
        i += 1
    if len(rows) > 0:
        split_data.append(rows)

    return split_data, i

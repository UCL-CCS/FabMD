import re
import csv

with open('log.lammps', 'r') as f:

    pattern = 'Step.*?\n(.*?)Loop'
    string = f.read()

    extracted_data = []
    for total_data in re.findall(pattern, string, flags=re.DOTALL): 
        for line in total_data.splitlines():
            extracted_data.append(line.split())

with open('output.csv', 'w', newline='') as f:
    write = csv.writer(f)
    write.writerows(extracted_data)

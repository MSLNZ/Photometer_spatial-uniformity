#Created by Neil Swift 2020, modified by Yang Yenn Tan 2025
#Conventional cartesian coordinates.
import math

version = "2025.10.13"

file_path = "O:\\STANDARDS\\Photometry\\Photometers\\2025\\Spatial Uniformity\\R0_Phot8"
input_file = 'R0 input_Phot8.txt'   # file with spatial uniformity data
output_file = 'Out_R0_Phot8.txt'    # if necessary, add parameters, i.e. spot size/position variations

stepspercell = 100
photometer_number = 8
H = -0.0824113
V = -0.0480733
diameter = 1.80618
radius = diameter / 2

def number_of_lines(full_path):
    fg = open(full_path, "r")
    with fg:
        for i, l in enumerate(f):
            pass
    fg.close()
    return i+1


def convert_to_float(line):
    new_list = []
    for value in line:
        numeric = float(value)
        new_list.append(numeric)
    return new_list

####    GET DATA    ####
data_in = [[]]

full_path = file_path + "\\" + input_file
f = open(full_path, "r")

total_lines = int(number_of_lines(full_path))

number_of_repeats = total_lines/8

if number_of_repeats < 1:
    print("waste of time, repeats is zero")

f = open(full_path, "r")
repeat_number = 1
for line_number in range(0, total_lines):
    if line_number/8 >= repeat_number:
        repeat_number += 1
        data_in.append([])
    line = f.readline().split("\t")
    line = convert_to_float(line)
    data_in[repeat_number-1].append(line)
print(data_in)
f.close()

####    PROCESS DATA    ####

imax = 8 * stepspercell - 1

x0 = H
y0 = V
c0 = radius

out_path = file_path + "\\" + output_file
w = open(out_path, "w")
w.write(full_path + "\n")
w.write("steps per cell: " + str(stepspercell) + "\n")
w.write("photometer number: " + str(photometer_number) + "\n")
w.write("H: " + str(H) + "\n")
w.write("V: " + str(V) + "\n")
w.write("diameter: " + str(diameter) + "\n")
w.write("radius: " + str(radius) + "\n")


for k in range(0, int(number_of_repeats)):
    for x in range(0, 7):
        w.write(str(data_in[k][x]) + "\n")

    num = 0
    denom = 0
    for i in range(0, imax+1):
        x = -4.0 + (0.5 + i)/stepspercell
        kx = int((i / stepspercell))
        for j in range(0, imax + 1):
            y = 4.0 - (0.5 + j)/stepspercell
            ky = int((j / stepspercell))
            d = math.sqrt((x-x0)*(x-x0) + (y-y0)*(y-y0))

            m = 0
            if d < c0:
                m = 1
                num = num + 1.0 + data_in[k][ky][kx]
                denom = denom + 1.0
    if denom == 0:
        R0 = 0
    else:
        R0 = num/denom

    w.write("R0 is: " + str(R0) + "\n")

    print("R0 is: " + str(R0) + "\n")

w.close()
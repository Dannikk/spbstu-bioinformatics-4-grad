import math
import os

Q = {"A": 0.2, "C": 0.3, "T": 0.2, "G": 0.3}
first_line = "ACTG"  # aka hor line
cond_to_cond = {"M0": {"M1": 0.61, "I0": 1 / 4, "D1": 0.14},
                "I0": {"M1": 0.46, "I0": 0.27, "D1": 0.27},
                # "D0":{"M1":1/3, "D1":1/3}
                "M1": {"M2": 0.71, "I1": 0.14, "D2": 0.14},
                "I1": {"M2": 1 / 3, "I1": 1 / 3, "D2": 1 / 3},
                "D1": {"M2": 1 / 3, "I2": 1 / 3, "D2": 1 / 3},

                "M2": {"M3": 0.55, "I2": 0.14, "D3": 0.30},
                "I2": {"M3": 1 / 3, "I2": 1 / 3, "D3": 1 / 3},
                "D2": {"M3": 1 / 3, "I3": 1 / 3, "D3": 1 / 3},

                "M3": {"M4": 0.65, "I3": 0.17, "D4": 0.17},
                "I3": {"M4": 1 / 3, "I3": 1 / 3, "D4": 1 / 3},
                "D3": {"M4": 0.51, "I4": 0.24, "D4": 0.24},

                "M4": {"M5": 0.83, "I4": 0.17},
                "I4": {"M5": 1 / 2, "I4": 1 / 2},
                "D4": {"M5": 1 / 2, "I5": 1 / 2},
                }

let_to_cond = {"M0": {"A": 1 / 4, "C": 1 / 4, "T": 1 / 4, "G": 1 / 4},
               "I0": {"A": 0.625, "C": 0.125, "T": 0.125, "G": 0.125},

               "M1": {"A": 0.125, "C": 0.265, "T": 0.485, "G": 0.125},
               "I1": {"A": 1 / 4, "C": 1 / 4, "T": 1 / 4, "G": 1 / 4},

               "M2": {"A": 1 / 8, "C": 1 / 8, "T": 0.53, "G": 0.22},
               "I2": {"A": 1 / 4, "C": 1 / 4, "T": 1 / 4, "G": 1 / 4},

               "M3": {"A": 1 / 8, "C": 0.36, "T": 1 / 8, "G": 0.39},
               "I3": {"A": 1 / 4, "C": 1 / 4, "T": 1 / 4, "G": 1 / 4},

                "M4": {"A": 0.455, "C": 0.125, "T": 0.295, "G": 0.125},
                "I4": {"A": 1 / 4, "C": 1 / 4, "T": 1 / 4, "G": 1 / 4},
               }

cond_size = 4  # 3+0


class log_Cell:
    counter = 0

    def __init__(self, func):
        log_Cell.counter += 1
        self.id = log_Cell.counter
        self.m = "-inf"
        self.m_dir = None
        self.i = "-inf"
        self.i_dir = None
        self.d = "-inf"
        self.d_dir = None
        # self.func = func

    def __repr__(self):
        return f"! (M:{round(self.m, 3) if isinstance(self.m, float) else self.m}-from:{self.m_dir}," \
               f" I:{round(self.i, 3) if isinstance(self.i, float) else self.i}-from:{self.i_dir}," \
               f" D:{round(self.d, 3) if isinstance(self.d, float) else self.d}-from:{self.d_dir})!"

    def sum_calc_i(self, prev_cell, cond, letter):
        pref = math.log(let_to_cond["I" + str(cond)][letter] / Q[letter])
        under_log_sum = 0
        if prev_cell.m != '-inf':
            under_log_sum += cond_to_cond["M" + str(cond)]["I" + str(cond)] * math.exp(prev_cell.m)
        if prev_cell.i != '-inf':
            under_log_sum += cond_to_cond["I" + str(cond)]["I" + str(cond)] * math.exp(prev_cell.i)

        if under_log_sum == 0:
            self.i = '-inf'
        else:
            self.i = pref + math.log(under_log_sum)

    def sum_calc_d(self, prev_cell, cond, letter):
        under_log_sum = 0
        if prev_cell.m != '-inf':
            under_log_sum += cond_to_cond["M" + str(cond - 1)]["D" + str(cond)] * math.exp(prev_cell.m)
        if prev_cell.i != '-inf':
            under_log_sum += cond_to_cond["I" + str(cond - 1)]["D" + str(cond)] * math.exp(prev_cell.i)

        if prev_cell.d != '-inf' and cond > 1:
            under_log_sum += cond_to_cond["D" + str(cond - 1)]["D" + str(cond)] * math.exp(prev_cell.d)
        if under_log_sum == 0:
            self.d = '-inf'
        else:
            self.d = math.log(under_log_sum)

    def sum_calc_m(self, prev_cell, cond, letter):
        pref = math.log(let_to_cond["M" + str(cond)][letter] / Q[letter])
        under_log_sum = 0
        if prev_cell.m != '-inf':
            under_log_sum += cond_to_cond["M" + str(cond - 1)]["M" + str(cond)] * math.exp(prev_cell.m)
        if prev_cell.i != '-inf':
            under_log_sum += cond_to_cond["I" + str(cond - 1)]["M" + str(cond)] * math.exp(prev_cell.i)

        if prev_cell.d != '-inf' and cond > 1:
            under_log_sum += cond_to_cond["D" + str(cond - 1)]["M" + str(cond)] * math.exp(prev_cell.d)
        if under_log_sum == 0:
            self.m = '-inf'
        else:
            self.m = pref + math.log(under_log_sum)

    def max_calc_i(self, cond, letter, prev_cell):
        max_val, max_dir = -100000000, None
        pref = math.log(let_to_cond["I" + str(cond)][letter] / Q[letter])  # ln(eij/q)
        if prev_cell.m != '-inf':
            max_val = prev_cell.m + math.log(cond_to_cond["M" + str(cond)]["I" + str(cond)])
            max_dir = "M"

        if prev_cell.i != '-inf' and prev_cell.i + math.log(
                cond_to_cond["I" + str(cond)]["I" + str(cond)]) > max_val:
            max_val = prev_cell.i + math.log(cond_to_cond["I" + str(cond)]["I" + str(cond)])
            max_dir = "I"
        if max_val > - 10000:
            self.i = max_val + pref
            self.i_dir = max_dir
        else:
            self.i = '-inf'

    def max_calc_d(self, cond, letter, prev_cell):
        max_val, max_dir = -100000000, None
        if prev_cell.m != '-inf':
            max_val = prev_cell.m + math.log(cond_to_cond["M" + str(cond - 1)]["D" + str(cond)])
            max_dir = "M"

        if prev_cell.i != '-inf' and prev_cell.i + math.log(
                cond_to_cond["I" + str(cond - 1)]["M" + str(cond)]) > max_val:
            max_val = prev_cell.i + math.log(cond_to_cond["I" + str(cond - 1)]["D" + str(cond)])
            max_dir = "I"

        if prev_cell.d != '-inf' and cond > 1 and prev_cell.d + math.log(  # D0 doesnt exist
                cond_to_cond["D" + str(cond - 1)]["M" + str(cond)]) > max_val:
            max_val = prev_cell.d + math.log(cond_to_cond["D" + str(cond - 1)]["D" + str(cond)])
            max_dir = "D"
        if max_val > - 10000:
            self.d = max_val
            self.d_dir = max_dir
        else:
            self.d = "-inf"

    def max_calc_m(self, prev_cell, cond, letter):
        max_val, max_dir = -100000000, None
        pref = math.log(let_to_cond["M" + str(cond)][letter] / Q[letter])  # ln(eij/q)
        if prev_cell.m != '-inf':
            max_val = prev_cell.m + math.log(cond_to_cond["M" + str(cond - 1)]["M" + str(cond)])
            max_dir = "M"

        if prev_cell.i != '-inf' and prev_cell.i + math.log(
                cond_to_cond["I" + str(cond - 1)]["M" + str(cond)]) > max_val:
            max_val = prev_cell.i + math.log(cond_to_cond["I" + str(cond - 1)]["M" + str(cond)])
            max_dir = "I"

        if prev_cell.d != '-inf' and cond > 1 and prev_cell.d + math.log(  # D0 doesnt exist
                cond_to_cond["D" + str(cond - 1)]["M" + str(cond)]) > max_val:
            max_val = prev_cell.d + math.log(cond_to_cond["D" + str(cond - 1)]["M" + str(cond)])
            max_dir = "D"
        if max_val > -10000:
            self.m = max_val + pref
            self.m_dir = max_dir
        else:
            self.m = "-inf"


def show_table(table):
    for line in table:
        print(line)


def create_table(size_x, size_y):
    return [[log_Cell(max) for _ in range(size_x + 1)] for _ in range(size_y + 1)]


def init_table_max(size_x, size_y):
    table = create_table(size_x, size_y)
    table[0][0].m = 0
    for i in range(1, size_x + 1):
        table[0][i].max_calc_i(0, first_line[i - 1], table[0][i - 1])
    for i in range(1, size_y + 1):
        table[i][0].max_calc_d(i, " ", table[i - 1][0])
    return table


def init_table_sum(size_x, size_y):
    table = create_table(size_x, size_y)
    table[0][0].m = 0
    for i in range(1, size_x + 1):
        table[0][i].sum_calc_i(table[0][i - 1], 0, first_line[i - 1])
    for i in range(1, size_y + 1):
        table[i][0].sum_calc_d(table[i - 1][0], i, " ")
    return table


def run_viterbi(table, size_x, size_y):
    for i in range(1, size_y + 1):
        for j in range(1, size_x + 1):
            table[i][j].max_calc_i(i, first_line[j - 1], table[i][j - 1])
            table[i][j].max_calc_d(i, " ", table[i - 1][j])
            table[i][j].max_calc_m(table[i - 1][j - 1], i, first_line[j - 1])
    return table


def run_forward(table):
    for i in range(1, size_y + 1):
        for j in range(1, size_x + 1):
            table[i][j].sum_calc_i(table[i][j - 1], i, first_line[j - 1])
            table[i][j].sum_calc_d(table[i - 1][j], i, first_line[j - 1])
            table[i][j].sum_calc_m(table[i - 1][j - 1], i, first_line[j - 1])
    return table


def tex_cell(*args):
    begin = r"\begin{tabular}[c]{@{}l@{}}"
    end = r"\end{tabular}"
    cell = str(args[0])
    for i in args[1::]:
        cell += r"\\ " + str(i)

    return begin+cell+end


def tex_table(table, output: str = "tex_table.tex"):
    preambule = r"\documentclass{article}" + '\n' +\
                r"\usepackage[a4paper,margin=1mm,landscape]{geometry}" + "\n" + \
                r"\begin{document}" + "\n"
    doc_end = r"\end{document}"

    hor = r"\hline"
    rd = 2

    out = open(output, "w")

    begin = r"\begin{table}[]"+"\n"+r"\begin{tabular}{"+("|l"*(len(first_line)+1)) + "|}" + "\n" + r"\hline"
    end = r"\end{tabular}" + "\n" + r"\end{table}"
    # header = "& " + reduce(lambda x, y: x + " & " + y, first_line) + r"\\ \hline"
    header = ""
    for i, letter in enumerate(first_line, start=1):
        cell = table[0][i]
        # TODO: move the construction of a cell string into a wrapper function
        header += "& " + letter + ": " + tex_cell(  f"M={round(cell.m, rd) if isinstance(cell.m, float) else cell.m} ({cell.m_dir})",
                                                    f"I={round(cell.i, rd) if isinstance(cell.i, float) else cell.i} ({cell.i_dir})",
                                                    f"D={round(cell.d, rd) if isinstance(cell.d, float) else cell.d} ({cell.d_dir})")

    header += r"\\ \hline"
    cur_tab = begin + "\n" + header

    for j, letter in enumerate(['1', '2', '3', '4'], start=1):
        cell = table[j][0]
        new_str = letter + ": " + tex_cell( f"M={round(cell.m, rd) if isinstance(cell.m, float) else cell.m} ({cell.m_dir})",
                                            f"I={round(cell.i, rd) if isinstance(cell.i, float) else cell.i} ({cell.i_dir})",
                                            f"D={round(cell.d, rd) if isinstance(cell.d, float) else cell.d} ({cell.d_dir})")
        for i in range(1, len(first_line) + 1):
            cell = table[j][i]
            c = tex_cell(f"M={round(cell.m, rd) if isinstance(cell.m, float) else cell.m} ({cell.m_dir})",
                         f"I={round(cell.i, rd) if isinstance(cell.i, float) else cell.i} ({cell.i_dir})",
                         f"D={round(cell.d, rd) if isinstance(cell.d, float) else cell.d} ({cell.d_dir})")
            new_str += " & " + c

        new_str += r"\\ \hline"
        cur_tab += "\n" + new_str

    cur_tab += "\n" + end

    doc = preambule + cur_tab + "\n" + doc_end
    out.write(doc)
    out.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    size_x = len(first_line)
    size_y = cond_size
    table = init_table_max(size_x, size_y)
    print("INIT TABLE")
    show_table(table)
    res = run_viterbi(table, size_x, size_y)

    tex_table(res)
    os.system("pdflatex -job-name Viterbi_log tex_table.tex")

    print("VITERBI TABLE RESULT")
    show_table(res)
    print("FORWARD TABLE RESULT")
    table = init_table_sum(size_x, size_y)
    result = run_forward(table)

    tex_table(result)
    os.system("pdflatex -job-name Forward_log tex_table.tex")

    show_table(result)

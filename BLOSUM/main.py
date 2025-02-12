from collections import defaultdict
from itertools import combinations
from math import log

# depends on variant
# input_seq_1 = "GKVNVDEV"
# input_seq_2 = "GKVKVDEV"
# d = 2
import numpy as np

input_seq_1 = "WGKVGAHAGE"
input_seq_2 = "WGKVNADN"
d = 6

PATH_FILE = "blosum_62.txt"  # if you have blosum-62 - dont change


class BLOSUM:
    def __init__(self, matrix_path, show=True):
        self.all_words = "ARNDCQEGHILKMFPSTWYV"
        self.words_to_int = {elem: indx for indx, elem in enumerate(self.all_words)}
        self.matrix = self.create_matrix(matrix_path, show)

    def create_matrix(self, matrix_path, show):
        matrix = [[-124 for _ in self.all_words] for _ in self.all_words]
        with open(matrix_path, 'r') as file:
            for indx, line in enumerate(file):
                norm = list(map(int, line.split()))
                for second_indx, elem in enumerate(norm):
                    matrix[indx][second_indx] = elem
                    matrix[second_indx][indx] = elem
                if not norm:
                    break
        if show:
            # for line in matrix:
            #     print(line)
            m = np.array(matrix)
            print(m)
        return matrix


def run_blosum_and_answer():
    blosum = BLOSUM(PATH_FILE)
    path = []
    seq_1 = "X" + input_seq_1  # add fictional character to normal iteration
    seq_2 = "X" + input_seq_2
    table = [[0 for _ in range(len(seq_1))] for _ in range(len(seq_2))]

    for i_indx, i_elem in enumerate(seq_2):
        sub_path = []
        for j_indx, j_elem in enumerate(seq_1):
            if i_indx == j_indx == 0:
                sub_path.append("start")
                continue
            if i_indx == 0:
                table[i_indx][j_indx] = -1 * d * j_indx
                sub_path.append("left")
            elif j_indx == 0:
                table[i_indx][j_indx] = -1 * d * i_indx
                sub_path.append("up")
            else:
                from_diag = table[i_indx - 1][j_indx - 1] + \
                            blosum.matrix[blosum.words_to_int[i_elem]][blosum.words_to_int[j_elem]]
                from_up = table[i_indx - 1][j_indx] - d
                from_left = table[i_indx][j_indx - 1] - d

                from_array = [(from_diag, 'diag'), (from_up, 'up'), (from_left, 'left')]
                cur_max = max(from_array, key=lambda i: i[0])
                table[i_indx][j_indx] = cur_max[0]
                sub_path.append(cur_max[1])
                # if from_diag >= from_up:
                #     if from_diag >= from_left:
                #         table[i_indx][j_indx] = from_diag
                #         sub_path.append("diag")
                #     else:
                #         table[i_indx][j_indx] = from_left
                #         sub_path.append("left")
                # else:
                #     if from_up >= from_left:
                #         table[i_indx][j_indx] = from_up
                #         sub_path.append("up")
                #     else:
                #         table[i_indx][j_indx] = from_left
                #         sub_path.append("left")
        path.append(sub_path)
    return table, path


def calc_S_rand(seq_1, seq_2):
    blosum = BLOSUM(PATH_FILE, show=False)
    f_counter = defaultdict(int)
    s_counter = defaultdict(int)
    for elem in seq_1:
        f_counter[elem] += 1
    for elem in seq_2:
        s_counter[elem] += 1
    res_sum = 0
    # for i in range(0, len(seq_1)):
    #     for j in range(0, len(seq_2)):
    for i, count_i in  f_counter.items():
        for j, count_j in s_counter.items():
            res_sum += blosum.matrix[blosum.words_to_int[i]][blosum.words_to_int[j]] * count_i * count_j
    return res_sum / len(seq_1)
    # add N(g) if you have this, because i dont have


if __name__ == '__main__':

    # res_table, res_path = run_blosum_and_answer()
    # print("values in path")
    # print(np.array(res_table))
    # # for line in res_table:
    # #     print(line)
    # print("path in table")
    # # print(np.array(res_path))
    # for line in res_path:
    #     print(line)

    # S rand stuff 6+ task:
    print("S_rand")
    seq_1 = "VDLEKIGG"
    seq_2 = "VDINEVGP"
    seq_3 = "VDLEKVGG"
    seq_4 = "VNVEHDGH"
    print("1,2", calc_S_rand(seq_1, seq_2))
    print("1,3", calc_S_rand(seq_1, seq_3))
    print("1,4", calc_S_rand(seq_1, seq_4))
    print("2,3", calc_S_rand(seq_2, seq_3))
    print("2,4", calc_S_rand(seq_2, seq_4))
    print("3,4", calc_S_rand(seq_3, seq_4))

    S = {1: {1: 16, 2: 1, 3: 13, 4: 1}, 2: {2: 16, 3: 4, 4: -2}, 3: {3: 16, 4: 1}, 4: {4: 16}}
    S_rand = {1: {2: calc_S_rand(seq_1, seq_2), 3: calc_S_rand(seq_1, seq_3), 4: calc_S_rand(seq_1, seq_4)},
              2: {3: calc_S_rand(seq_2, seq_3), 4: calc_S_rand(seq_2, seq_4)}, 3: {4: calc_S_rand(seq_3, seq_4)}}
    for x, y in combinations([1, 2, 3, 4], 2):
        print(f"D {x, y}")
        up = (S[x][y] - S_rand[x][y])
        down = ((S[x][x] + S[y][y]) / 2) - S_rand[x][y]
        print(up)
        print(down)
        cal = - log(up/down)
        print(cal)
    print("HEHE")

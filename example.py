import matplotlib.pyplot as plt
from lab import Cwiczenie
from math import pi


def x(L, L0): return L - L0
def T(t, n): return t/n
def avg_x(x): return sum(x)/len(x)
def k(m, T): return 4*pow(pi, 2)*m/pow(T, 2)
def F(x, k): return -k*x
def avg_k(k): return sum(k)/len(k)
def k_from_avg(k, avg_k): return abs(k - avg_k)
def avg_k_from_avg(k_from_avg): return sum(k_from_avg)/len(k_from_avg)
def error_k(m, T, NP_M, NP_T, k): return k*(NP_M/m + 2*NP_T/T)
def avg_error_k(error_k): return sum(error_k)/len(error_k)
def max_error_k(error_k): return max(error_k)


workflow = [x, T, k, F,
            [avg_x, True], [avg_k, True],
            k_from_avg, error_k, [max_error_k, True],
            [avg_k_from_avg, True], [avg_error_k, True]]

with open("cwiczenie_32.ods", 'rb') as file:
    cwiczenie = Cwiczenie(file, "Cwiczenie nr. 32")

    cwiczenie.convert_values("L, L0, NP_L, m, NP_M", 1/1000)
    cwiczenie.calculate(workflow)

    cwiczenie.convert_values("m, L, x", 1000)
    cwiczenie.export_data("m, L, x, t, T", filename="data1_mLxtT.ods")
    cwiczenie.export_data("T, k, k_from_avg, error_k", filename="data1_Tkkfromavg.ods")
    cwiczenie.export_data("T, k, error_k", filename="data1_error.ods")

    cwiczenie.get_data("max_error_k")
    cwiczenie.get_data("avg_k, avg_k_from_avg, avg_error_k")

    cwiczenie.convert_values("m, L, x", 1/1000)
    cwiczenie.lin_reg("x", "F", filename="regresja_1.ods", xlabel="x [m]", ylabel="F [N]")
    cwiczenie.plot("x", "k", method="sl", title="Wykres k(x)", ylim=[0, 5], xlabel="x [m]", ylabel="k [N/m]")

    cwiczenie.next_sheet()
    cwiczenie.convert_values("L, L0, NP_L, m, NP_M", 1/1000)
    cwiczenie.calculate(workflow)

    cwiczenie.convert_values("m, L, x", 1000)
    cwiczenie.export_data("m, L, x, t, T", filename="data2_mLxtT.ods")
    cwiczenie.export_data("T, k, k_from_avg, error_k", filename="data2_Tkkfromavg.ods")
    cwiczenie.export_data("T, k, error_k", filename="data2_error.ods")

    cwiczenie.get_data("max_error_k")
    cwiczenie.get_data("avg_k, avg_k_from_avg, avg_error_k")

    cwiczenie.convert_values("m, L, x", 1 / 1000)
    cwiczenie.lin_reg("x", "F", filename="regresja_2.ods", xlabel="x [m]", ylabel="F [N]")
    cwiczenie.plot("x", "k", method="sl", title="Wykres k(x)", ylim=[20, 30], xlabel="x [m]", ylabel="k [N/m]")
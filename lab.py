import types

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


class Cwiczenie:

    def __init__(self, source, title: str, functions: list = None, single_functions: list = None):
        self.title = title
        self.ignored_indices = []
        self._functions = functions
        self._single_functions = single_functions
        self.funcs = {}
        self.source_sheet = source
        self.series = []
        self.current_series = 0
        self.N_Sheets = 0
        self.N = []
        self.read_source()

    def read_source(self):
        file = pd.read_excel(self.source_sheet, sheet_name=None)
        for sheet in file:
            self.N_Sheets = self.N_Sheets + 1
            data = file[sheet]
            cols = data.columns[:2]
            constants = {}
            const_data = data[cols].dropna()
            cnames, cvalues = const_data
            for name, value in zip(const_data[cnames], const_data[cvalues]):
                constants[name] = value

            cols = data.columns[2:]
            measurements = {}
            measurements_data = data[cols]
            calculable = {}
            self.N.append(len(measurements_data))

            for col in measurements_data:
                if not measurements_data[col].isnull().values.any():
                    measurements[str(col)] = list(measurements_data[col])
                else:
                    symbol = str(col)
                    calculable[symbol] = []

            sheet_data = [constants, measurements, calculable, {}]
            self.series.append(sheet_data)
        self.current_series = 0

        func_names = []
        for series in self.series:
            for name in list(series[2].keys()):
                func_names.append(name)

        if self._functions is not None:
            for func in self._functions:
                self.funcs[func.__name__] = func

            for func in self._single_functions:
                self.funcs[func.__name__] = func

    def next_sheet(self):
        if len(self.series) > self.current_series + 1:
            self.current_series = self.current_series + 1
        else:
            print("No more data.")

    def _find_arg_table(self, name):
        for idx, data in enumerate(self.series[self.current_series]):
            if name in data:
                return idx, data[name]

    def calculate(self, target, single_output=False):
        if isinstance(target, list):
            for data in target:
                if isinstance(data, list):
                    self.calculate(*data)
                else:
                    self.calculate(data)
            return
        if isinstance(target, types.FunctionType):
            f = target
            target = f.__name__
        else:
            f = self.funcs[target]
            single_output = True if target in [func.__name__ for func in self._single_functions] else False

        parameters = f.__code__.co_varnames[:f.__code__.co_argcount]

        constants = self.series[self.current_series][0]
        measured = self.series[self.current_series][1]
        calculated = self.series[self.current_series][2]
        single_calculated = self.series[self.current_series][3]

        if single_output:
            data = measured | calculated | single_calculated | constants
            value = f(*[data[name] for name in parameters])
            single_calculated[target] = value
            return value

        values = []
        combined = measured | calculated
        for idx in range(0, self.N[self.current_series]):
            data = constants | single_calculated
            for name in combined:
                if name not in parameters:
                    continue
                if combined[name]:
                    data[name] = combined[name][idx]
                else:
                    data[name] = None
            args = [data[name] for name in parameters]
            values.append(f(*args))
        calculated[target] = values
        return values

    def convert_values(self, names, q):
        if isinstance(names, str):
            names = [name.strip() for name in names.split(',')]
        for name in names:
            idx, col = self._find_arg_table(name)
            if idx == 0:
                self.series[self.current_series][0][name] = q*col
            else:
                self.series[self.current_series][idx][name] = [value*q for value in col]

    def lin_reg(self, X, Y, title=None, filename=None, xlim: list = None, ylim: list = None, xlabel=None, ylabel=None, display_params=True):
        x = self._find_arg_table(X)[1]
        y = self._find_arg_table(Y)[1]
        xy = [val1*val2 for val1, val2 in zip(x, y)]
        x2 = [pow(val, 2) for val in x]
        y2 = [pow(val, 2) for val in y]
        sumx = sum(x)
        sumy = sum(y)
        sumxy = sum(xy)
        sumx2 = sum(x2)
        sumy2 = sum(y2)

        n = len(x)
        P = n*sumx2-pow(sumx, 2)
        a = (1/P) * (n*sumxy - sumx*sumy)
        b = (1/n) * (sumy - a*sumx)

        if display_params:
            print(f"Linear regression:\na = {a}\nb = {b}")

        xs = np.linspace(min(x), max(x), num=100)
        if xlim is not None:
            xs = np.linspace(xlim[0], xlim[1], num=100)
        plt.plot(xs, a*xs+b, color="k", lw=2.5, alpha=0.7)
        plt.scatter(x, y, edgecolors="k")

        if xlim is not None:
            plt.xlim(xlim)
        if ylim is not None:
            plt.ylim(ylim)
        if not xlabel:
            xlabel = X
        if not ylabel:
            ylabel = Y
        if not title:
            title = f"{Y}({X}), a = " + "{:.2f}".format(a)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)

        x.append(sumx)
        y.append(sumy)
        xy.append(sumxy)
        x2.append(sumx2)
        y2.append(sumy2)
        data = {f"x [{X}]": x, f"y [{Y}]": y, "xy": xy, "x^2": x2, "y^2": y2}
        df = pd.DataFrame(data)
        df.index += 1
        df.rename(index={len(x): "Suma"}, inplace=True)
        df.to_excel(filename, index=True, index_label="Pomiar")

        plt.show()

    def get_data(self, data, display=True):
        data = [name.strip() for name in data.split(',')]
        dictionary = {name: self._find_arg_table(name)[1] for name in data}
        set_index = False
        for name in dictionary:
            if not isinstance(dictionary[name], list):
                set_index = True
                break
        if set_index:
            df = pd.DataFrame(dictionary, index=[0])
        else:
            df = pd.DataFrame(dictionary)
        df.index += 1
        if display:
            print(df)
        return df

    def export_data(self, data: str, filename):
        self.get_data(data, False).to_excel(filename)

    def plot(self, X, Y, title=None, xlim: list = None, ylim: list = None, method="s", xlabel=None, ylabel=None):
        data = zip(self._find_arg_table(X)[1], self._find_arg_table(Y)[1])
        data = sorted(data, key=lambda x: x[0])
        xs, ys = [x for x, _ in data], [y for _, y in data]

        if "s" in method:
            plt.scatter(xs, ys)
        if "l" in method:
            plt.plot(xs, ys)
        if xlim is not None:
            plt.xlim(xlim)
        if ylim is not None:
            plt.ylim(ylim)
        if not xlabel:
            xlabel = X
        if not ylabel:
            ylabel = Y
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.show()

import pyvisa
import time


def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

def get_digits(num):
    assert num > 0, f"Number must be greated than zero {num}"
    num_str = str(int(num))
    digits = []
    for num in num_str:
        digits.append(int(num))
    
    return digits


class STFRD_CG635:
    def __init__(self, addr):
        resources = pyvisa.ResourceManager('@py')
        self.inst = resources.open_resource('GPIB::23::INSTR')


    def write(self, cmd):
        self.inst.write(cmd)

    def query(self, cmd, prnt=False):
        ret = self.inst.query(cmd)

        if prnt == True:
            print(ret)

        return ret

    def idn(self):
        idx = self.inst.query('*IDN?', True)
        return idx

    def self_test(self):
        self.write("*TST?")

    def set_display(self, param):
        VALUES = ["Frequency", "Phase", "Q/Q! High", "Q/Q! Low", "CMOS high",\
                "CMOS low", "Frequency step", "Phase step", "Q/Q! high step",\
                "Q/Q! low step", "CMOS high step", "CMOS low step"]

        VALUES = list((map(lambda x: x.lower(), VALUES)))

        if isinstance(param, str):
            param = param.lower()
            try:
                param = VALUES.index(param)
            except ValueError:
                print(f"Parameter '{param}' is not in list {VALUES}")

        elif isinstance(param, int):
            assert param >= 0 and param <= len(VALUES), f"Param {param} is not in range [0, {len(VALUES)}]"


        self.write(f"DISP{param}")

    def get_display(self, prnt=False):
        return self.query("DISP?", prnt)

    def get_frequency(self, prnt=False):
        return self.query(f"FREQ?", True)

    def set_frequency(self, f):
        assert f >= 0 and f <= 2.05e9, f"Freqeuncy must be in range [0, 2.05GHz], set {f}Hz"
        self.write(f"FREQ{f}")

    def step_down(self, param):
        VALUES = ["Frequency", "Phase", "Q/Q! High", "Q/Q! Low", "CMOS high", "CMOS low"]

        VALUES = list((map(lambda x: x.lower(), VALUES)))

        if isinstance(param, str):
            param = param.lower()
            try:
                param = VALUES.index(param)
            except ValueError:
                print(f"Parameter '{param}' is not in list {VALUES}")

        elif isinstance(param, int):
            assert param >= 0 and param <= len(VALUES), f"Param {param} is not in range [0, {len(VALUES)}]"

        self.write(f"STPD {param}")

    def step_up(self, param):
        VALUES = ["Frequency", "Phase", "Q/Q! High", "Q/Q! Low", "CMOS high", "CMOS low"]

        VALUES = list((map(lambda x: x.lower(), VALUES)))

        if isinstance(param, str):
            param = param.lower()
            try:
                param = VALUES.index(param)
            except ValueError:
                print(f"Parameter '{param}' is not in list {VALUES}")

        elif isinstance(param, int):
            assert param >= 0 and param <= len(VALUES), f"Param {param} is not in range [0, {len(VALUES)}]"

        self.write(f"STPU {param}")

    def set_stdq(self, param):
        VALUES = ["ECL", "+7 dBm", "LVDS", "PECL 3.3V", "PECL 5.0V"] 

        VALUES = list((map(lambda x: x.lower(), VALUES)))

        if isinstance(param, str):
            param = param.lower()
            try:
                param = VALUES.index(param)
            except ValueError:
                print(f"Parameter '{param}' is not in list {VALUES}")
        elif isinstance(param, int):
            assert param >= 0 and param <= len(VALUES), f"Param {param} is not in range [0, {len(VALUES)}]"

        self.write(f"STDQ{param}")

    def set_stdq_level(self, values=[]):
        values = list(map(lambda x: int(truncate(x, 2) * 100), values))
        assert values[1] - values[0] >=  20, f"Minimum differential voltage is 0.2V, got lower {values[0]/100}V, higher {values[1]/100}V, diff {(values[1]-values[0])/100}"
        assert values[1] - values[0] <=  100, f"Maxiumum differential voltage is 1.0V, got lower {values[0]/100}V, higher {values[1]/100}V, diff {(values[1]-values[0])/100}"

        self.set_stdq("LVDS")
        lvds_stdq_levels = [107, 143]

        diff = [values[0] - lvds_stdq_levels[0], values[1] - lvds_stdq_levels[1]]

        step = 0.01
        self.set_stps("Q/Q! low", step)
        for d in range(abs(diff[0])):
            if diff[0] < 0:
                self.step_down("Q/Q! low")
            elif diff[0] > 0:
                self.step_up("Q/Q! low")

        if values[0] > lvds_stdq_levels[1]:
            lvds_stdq_levels[1] = values[0] +  20
        elif lvds_stdq_levels[1] - values[0] > 100:
            lvds_stdq_levels[1] = values[0] + 100

        diff[1] = values[1] - lvds_stdq_levels[1]

        step = 0.01
        self.set_stps("Q/Q! high", step)
        for d in range(abs(diff[1])):
            if diff[1] < 0:
                self.step_down("Q/Q! high")
            elif diff[1] > 0:
                self.step_up("Q/Q! high")

    
    def set_stps(self, param, value):
        VALUES = ["Frequency", "Phase", "Q/Q! High", "Q/Q! Low", "CMOS high", "CMOS low"]

        VALUES = list((map(lambda x: x.lower(), VALUES)))

        if isinstance(param, str):
            param = param.lower()
            try:
                param = VALUES.index(param)
            except ValueError:
                print(f"Parameter '{param}' is not in list {VALUES}")

        elif isinstance(param, int):
            assert param >= 0 and param <= len(VALUES), f"Param {param} is not in range [0, {len(VALUES)}]"

        self.write(f"STPS {param},{value}")



# i = STFRD_CG635(23)
#
# i.idn()
# i.set_display("frequency")
#
# i.set_frequency(10e6)
# i.set_display("q/q! high")
# i.set_stdq_level([0.2, 0.60])
# i.set_frequency(1e6)
# i.set_display("q/q! low")

# i.set_stps("Q/Q! High", 0.01)
# for d in range(7):
#     time.sleep(1)
#     i.step_up("q/q! high")
#
# i.set_stps("Q/Q! High", 0.1)
# for d in range(3):
#     time.sleep(1)
#     i.step_up("q/q! high")

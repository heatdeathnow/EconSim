from __future__ import annotations
from dataclasses import dataclass
import enum
from pathlib import Path
from typing import Self, Sequence
from matplotlib.gridspec import GridSpec

from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from source.goods import Goods, Stockpile
from source.pop import Jobs, Pop, Strata
from source.prod import Workforce
from visual import data_dir
from pandas import DataFrame
import pandas as pd
import matplotlib.pyplot as plt

class FileSyncError(Exception): pass

@dataclass
class DataCase:
    """
    Used as a case for data. Population, goods produced data, etc will all be kept in instances of this class.
    """

    name: str
    pop_size = DataFrame(columns = [None] + [job.name for job in Jobs])
    pop_welfare = DataFrame(columns = [stratum.name for stratum in Strata])
    goods = DataFrame(columns = [good.name for good in Goods])

    def __post_init__(self):
        self.data_folder = data_dir / Path(self.name)
        self.pop_size_file = self.data_folder / 'pop_size.csv'
        self.pop_welfare_file = self.data_folder / 'pop_welfare.csv'
        self.goods_file = self.data_folder / 'goods.csv'

    def record_pops(self, pops: Workforce | dict[Jobs, Pop] | Sequence[Pop]) -> None:
        if not isinstance(pops, (Workforce, dict)) and not issubclass(type[pops], Sequence):
            raise TypeError

        if isinstance(pops, Workforce):
            pops = pops.pops
            
        size, welfare = pops_to_df(pops)
        self.pop_size = pd.concat([self.pop_size, size], ignore_index=True)
        self.pop_welfare = pd.concat([self.pop_welfare, welfare], ignore_index=True)

    def record_goods(self, goods: Stockpile | dict[Goods, int | float]) -> None:
        if not isinstance(goods, Stockpile) and not isinstance(goods, dict):
            raise TypeError

        data = {good.name: 0.0 for good in Goods}

        for good, amount in goods.items():
            if isinstance(goods, dict) and (good not in Goods or not isinstance(amount, (int, float))):
                raise TypeError
            
            data[good.name] = amount
        
        self.goods = pd.concat([self.goods, DataFrame(data, index=[0])], ignore_index = True) 

    def __iadd__(self, __value: Workforce | dict[Jobs, Pop] | Sequence[Pop] | Stockpile | dict[Goods, int | float]) -> Self:
        if isinstance(__value, Workforce) or issubclass(type(__value), Sequence):
            self.record_pops(__value)
        
        elif isinstance(__value, Stockpile):
            self.record_goods(__value)
        
        elif isinstance(__value, dict):
            if all([job in Jobs and isinstance(pop, Pop) for job, pop in __value.items()]):
                self.record_pops(__value)
            
            elif all([good in Goods and isinstance(amount, (int | float)) for good, amount in __value.items()]):
                self.record_goods(__value)
            
            else:
                raise ValueError(f'Dictionary passed has mixed or incorrect values: {__value}')

        else:
            raise TypeError

        return self

class DataManager:

    def __init__(self, datacases: Sequence[DataCase]) -> None:
        self.data: dict[str, DataCase] = {}

        for datacase in datacases:
            self.data[datacase.name] = datacase

    def save_csv(self, case: str, overwrite: bool = False) -> None:
        datacase = self.data[case]

        if not datacase.data_folder.exists():
            datacase.data_folder.mkdir()

        if not datacase.pop_size_file.exists():
            with datacase.pop_size_file.open('x+'): pass
        
        if not datacase.pop_welfare_file.exists():
            with datacase.pop_welfare_file.open('x+'): pass
        
        if not datacase.goods_file.exists():
            with datacase.goods_file.open('x+'): pass

        if     (is_empty(datacase.pop_size_file)    and not is_empty(datacase.pop_welfare_file)) \
            or (is_empty(datacase.pop_size_file)    and not is_empty(datacase.goods_file))       \
            or (is_empty(datacase.goods_file)       and not is_empty(datacase.pop_size_file))    \
            or (is_empty(datacase.goods_file)       and not is_empty(datacase.pop_welfare_file)) \
            or (is_empty(datacase.pop_welfare_file) and not is_empty(datacase.pop_size_file))    \
            or (is_empty(datacase.pop_welfare_file) and not is_empty(datacase.goods_file)):
            raise FileSyncError

        if overwrite or (is_empty(datacase.pop_size_file) and is_empty(datacase.goods_file)):  # if file is empty.
            datacase.pop_size.rename(columns = {None: 'NONE'}, inplace = True)
            datacase.pop_size.to_csv(datacase.pop_size_file, sep = ';', index = False)
            datacase.pop_size.rename(columns = {'NONE': None}, inplace = True)

            datacase.pop_welfare.to_csv(datacase.pop_welfare_file, sep = ';', index = False)

            datacase.goods.to_csv(datacase.goods_file, sep = ';', index = False)
        
        else:
            df = pd.read_csv(datacase.pop_size_file, sep = ';')
            df.rename(columns = {'NONE': None}, inplace = True)
            df = pd.concat([df, datacase.pop_size], ignore_index = True)
            df.rename(columns = {None: 'NONE'}, inplace = True)
            df.to_csv(datacase.pop_size_file, sep = ';', index = False)

            df = pd.read_csv(datacase.pop_welfare_file, sep = ';')
            df = pd.concat([df, datacase.pop_welfare], ignore_index = True)
            df.to_csv(datacase.pop_welfare_file, sep = ';', index = False)

            df = pd.read_csv(datacase.goods_file, sep = ';')
            df = pd.concat([df, datacase.goods], ignore_index = True)
            df.to_csv(datacase.goods_file, sep = ';', index = False)

    def load_csv(self, case: str) -> None:
        try:
            datacase = self.data[case]
        
        except KeyError:
            raise KeyError(f'`Datacase` object "{case}" does not exist within this `DataManager` object.')

        datacase.pop_size = pd.read_csv(datacase.pop_size_file, sep = ';', index = False)
        datacase.pop_size.rename(columns = {'NONE': None})

        datacase.goods = pd.read_csv(datacase.goods_file, sep = ';', index = False)
        datacase.goods.rename(columns = {'NONE': None})

    def plot_graph(self, case: str) -> None:

        datacase = self.data[case]

        # Population size
        pop_size_fig, pop_size_ax = plt.subplots()
        pop_size_ax: Axes

        pop_size_ax.set_title('Population change')
        pop_size_ax.set_xlabel('Time')
        pop_size_ax.set_ylabel('Population size')

        size_lines: list[Line2D] = []
        size_labels: list[str] = []
        for job, series in datacase.pop_size.items():
            
            if len(series[series == 0]) == len(series):
                continue

            if job is None:
                job = 'NONE'
            
            moving_mean = series.rolling(2).mean()
            size_lines += pop_size_ax.plot(moving_mean, label = job)
            size_labels.append(job)
        
        pop_size_fig.tight_layout()
        pop_size_fig.legend()
        pop_size_fig.savefig(datacase.data_folder / 'pop_size.png', dpi = 300)
        plt.close()

        # Population welfare
        pop_welfare_fig, pop_welfare_ax = plt.subplots()
        pop_welfare_ax: Axes

        pop_welfare_ax.set_title('Welfare over time')
        pop_welfare_ax.set_xlabel('Time')
        pop_welfare_ax.set_ylabel('Welfare')

        welfare_lines: list[Line2D] = []
        welfare_labels: list[str] = []
        for stratum, series in datacase.pop_welfare.items():
            
            if len(series[series == 0]) == len(series):
                continue
            
            moving_mean = series.rolling(2).mean()
            welfare_lines += pop_welfare_ax.plot(moving_mean, label = stratum)
            welfare_labels.append(stratum)
        
        pop_welfare_fig.tight_layout()
        pop_welfare_fig.legend()
        pop_welfare_fig.savefig(datacase.data_folder / 'pops_welfare.png', dpi = 300)
        plt.close()

        # Goods
        goods_fig, goods_ax = plt.subplots()
        goods_ax: Axes

        goods_ax.set_title('Production')
        goods_ax.set_xlabel('Time')
        goods_ax.set_ylabel('Stockpile size')

        goods_lines: list[Line2D] = []
        goods_labels: list[str] = []
        for good, series in datacase.goods.items():

            if len(series[series == 0]) == len(series):
                continue
            
            moving_mean = series.rolling(2).mean()
            goods_lines += goods_ax.plot(moving_mean, label = good)
            goods_labels.append(good)
        
        goods_fig.tight_layout()
        goods_fig.legend()
        goods_fig.savefig(datacase.data_folder / 'goods.png', dpi = 300)
        plt.close()

        # Show everything on screen.
        fig, axs = plt.subplots(2, 2)

        axs[0, 0].set_title('Size overview')
        for i, line in enumerate(size_lines):
            data = line.get_data()
            axs[0, 0].plot(data[0], data[1], label = size_labels[i])
        axs[0, 0].legend()
        
        axs[0, 1].set_title('Welfare overview')
        for i, line in enumerate(welfare_lines):
            data = line.get_data()
            axs[0, 1].plot(data[0], data[1], label = welfare_labels[i])
        axs[0, 1].legend()
        
        axs[1, 0].set_title('Goods overview')
        for i, line in enumerate(goods_lines):
            data = line.get_data()
            axs[1, 0].plot(data[0], data[1], label = goods_labels[i])
        axs[1, 0].legend()
        
        fig.tight_layout()
        plt.show()
        
def is_empty(path: Path) -> bool:
    size = path.stat().st_size

    if size > 0:
        return False

    else:
        return True

def pops_to_df(pops: dict[Jobs, Pop] | dict[None | Jobs, Pop] | Sequence[Pop]) -> tuple[DataFrame, DataFrame]:
    pop_size: dict[None | str, int | float] = {job.name: 0.0 for job in Jobs}
    pop_size[None] = 0.0

    pop_welfare = {stratum.name: 0.0 for stratum in Strata}

    if isinstance(pops, dict):
        for job, pop in pops.items():
            if (job and job not in Jobs) or not isinstance(pop, Pop):
                raise TypeError
            
            if not job:
                pop_size[None] += pop.size
            
            else:
                pop_size[job.name] += pop.size
            
            pop_welfare[pop.stratum.name] = pop.welfare  # Faster to assign a repeated value than to check for it.

    elif issubclass(type(pops), Sequence):
        for pop in pops:
            if not isinstance(pop, Pop):
                raise TypeError
            
            if pop.job:
                pop_size[pop.job.name] += pop.size
            
            else:
                pop_size[None] += pop.size
            
            pop_welfare[pop.stratum.name] = pop.welfare
    
    else:
        raise TypeError
    
    return DataFrame(pop_size, index = [0]), DataFrame(pop_welfare, index = [0])

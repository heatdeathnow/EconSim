from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from source.goods import Goods, Stockpile
from source.pop import Community, Jobs, Strata
from visual import data_dir
from pandas import DataFrame
import pandas as pd
import matplotlib.pyplot as plt

class FileSyncError(Exception): 
    pass

def is_empty(path: Path) -> bool:
    size = path.stat().st_size

    if size > 0:
        return False

    else:
        return True

@dataclass
class DataCase:
    """
    Used as a case for data. Population, goods produced data, etc will all be kept in instances of this class.
    """

    name: str
    pop_size       = DataFrame(columns = [job.name for job in Jobs])
    pop_welfare    = DataFrame(columns = [job.name for job in Jobs])
    goods_produced = DataFrame(columns = [good.name for good in Goods])
    goods_consumed = DataFrame(columns = [good.name for good in Goods])
    goods_demanded = DataFrame(columns = [good.name for good in Goods])

    def __post_init__(self):
        self.data_folder = data_dir / Path(self.name)

        self.pop_size_file       = self.data_folder / 'pop_size.csv'
        self.pop_welfare_file    = self.data_folder / 'pop_welfare.csv'
        self.goods_produced_file = self.data_folder / 'goods_produced.csv'
        self.goods_consumed_file = self.data_folder / 'goods_consumed.csv'
        self.goods_demanded_file = self.data_folder / 'goods_demanded.csv'

    @property
    def map(self) -> dict[Path, DataFrame]:
        return {
            self.pop_size_file: self.pop_size,
            self.pop_welfare_file: self.pop_welfare,
            self.goods_produced_file: self.goods_produced,
            self.goods_consumed_file: self.goods_consumed,
            self.goods_demanded_file: self.goods_demanded,
        }

    def record_pop_size(self, pops: Community) -> None:
        new_col: dict[str, int | float] = {job.name: 0.0 for job in Jobs}

        for key, pop in pops.items():
            if isinstance(key, tuple):
                new_col[key[1].name] += pop.size
            
            elif key in Jobs:
                new_col[key.name] += pop.size
            
            else:
                raise KeyError
        
        new_df = DataFrame(new_col, index=[0])
        self.pop_size = pd.concat([self.pop_size, new_df], ignore_index=True)
    
    def record_pop_welfare(self, pops: Community) -> None:
        new_col: dict[str, int | float] = {job.name: 0.0 for job in Jobs}

        for key, pop in pops.items():
            if isinstance(key, tuple):
                new_col[key[1].name] += pop.welfare
            
            elif key in Jobs:
                new_col[key.name] += pop.welfare
            
            else:
                raise KeyError
        
        new_df = DataFrame(new_col, index=[0])
        self.pop_welfare = pd.concat([self.pop_welfare, new_df], ignore_index=True)
    
    @staticmethod
    def __stockpile_to_df(stockpile: Stockpile):
        new_col = {good.name: 0.0 for good in Goods}

        for good, amount in stockpile.items():
            new_col[good.name] += amount

        new_df = DataFrame(new_col, index=[0])
        
        return new_df
    
    def record_goods_produced(self, goods: Stockpile):
        self.goods_produced = pd.concat([self.goods_produced, self.__stockpile_to_df(goods)], ignore_index=True)
    
    def record_goods_consumed(self, goods: Stockpile):
        self.goods_consumed = pd.concat([self.goods_consumed, self.__stockpile_to_df(goods)], ignore_index=True)
    
    def record_goods_demanded(self, goods: Stockpile):
        self.goods_demanded = pd.concat([self.goods_demanded, self.__stockpile_to_df(goods)], ignore_index=True)

class DataManager:

    def __init__(self, *datacases: DataCase) -> None:
        self.data = {datacase.name: datacase for datacase in datacases}

    @staticmethod
    def __sync_check(datacase: DataCase) -> None:
        if any(is_empty(file) for file in datacase.map) and not all(is_empty(file) for file in datacase.map):
            raise FileSyncError

    @staticmethod
    def __file_exists_check(datacase: DataCase) -> None:
        if not datacase.data_folder.exists():
            datacase.data_folder.mkdir()
        
        for file in datacase.map:
            if not file.exists():
                with file.open('x'): pass

    def save_csv(self, case: str, overwrite: bool = False) -> None:
        datacase = self.data[case]

        self.__file_exists_check(datacase)
        self.__sync_check(datacase)

        if overwrite or all(is_empty(file) for file in datacase.map):
            for file, df in datacase.map.items():
                df.to_csv(file, sep=';', index=False)
        
        else:
            for file, df in datacase.map.items():
                old_df = pd.read_csv(file, sep=';')
                new_df = pd.concat([old_df, df], ignore_index=True)
                new_df.to_csv(file, sep=';', index=False)

    def load_csv(self, case: str) -> None:
        datacase = self.data[case]

        datacase.pop_size = pd.read_csv(datacase.pop_size_file, sep=';')
        datacase.pop_welfare = pd.read_csv(datacase.pop_welfare_file, sep=';')
        datacase.goods_produced = pd.read_csv(datacase.goods_produced_file, sep=';')
        datacase.goods_consumed = pd.read_csv(datacase.goods_consumed_file, sep=';')
        datacase.goods_demanded = pd.read_csv(datacase.goods_demanded_file, sep=';')

    def plot_graph(self, df: DataFrame, graph_dir: Path, title: str, xlabel: str, ylabel: str):
        
        fig, ax = plt.subplots()
        ax: Axes

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        for col, series in df.items():
            if len(series[series == 0]) == len(series):
                continue

            ax.plot(series, label=col)
        
        fig.tight_layout()
        fig.legend()
        fig.savefig(graph_dir, dpi=300)
        plt.close()

    def plot_all(self, case: str) -> None:
        datacase = self.data[case]

        folder = datacase.data_folder / 'graphs'

        try:
            folder.mkdir()
        except FileExistsError:
            pass

        # Population size
        self.plot_graph(datacase.pop_size, folder / 'pop_size.png', 'Population Size', 'Time', 'Size')

        # Population welfare
        self.plot_graph(datacase.pop_welfare, folder / 'welfare.png', 'Welfare over time', 'Time', 'Welfare')

        # Goods produced
        self.plot_graph(datacase.goods_produced, folder / 'goods_produced.png', 'Goods produced over time', 'Time', 'Amount')

        # Goods produced
        self.plot_graph(datacase.goods_demanded, folder / 'goods_demanded.png', 'Goods demanded over time', 'Time', 'Amount')

        # Goods produced
        self.plot_graph(datacase.goods_consumed, folder / 'goods_consumed.png', 'Goods demanded over time', 'Time', 'Amount')

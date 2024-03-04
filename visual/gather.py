from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, DivisionByZero, DivisionUndefined, InvalidOperation, getcontext
from itertools import chain
from pathlib import Path
from typing import Literal
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from source.goods import Products, Stock, create_stock
from source.pop import Commune, CommuneFactory, Jobs, Strata
from source.prod import Extractor, Industry, Manufactury
from visual import data_dir
from pandas import DataFrame
import pandas as pd
import matplotlib.pyplot as plt
D = getcontext().create_decimal

def is_empty(path: Path) -> bool:
    size = path.stat().st_size

    if size > 0:
        return False

    else:
        return True

type data_key = Literal['pop_size', 'pop_welfare', 'stock', 'goods_produced', 'goods_demanded', 'goods_consumed', 'goods_satisfaction']

class DataManager:
    def __init__(self, name: str, /, *to_be_recorded: Industry | Commune) -> None:
        self.name = name
        self.data: dict[data_key, DataFrame] = {
            'pop_size': DataFrame(columns = [job.name for job in Jobs]),
            'pop_welfare': DataFrame(columns = [job.name for job in Jobs]),
            'stock': DataFrame(columns = [good.name for good in Products]),
            'goods_produced': DataFrame(columns = [good.name for good in Products]),
            'goods_demanded': DataFrame(columns = [good.name for good in Products]),
            'goods_consumed': DataFrame(columns = [good.name for good in Products]),
            'goods_satisfaction': DataFrame(columns = [good.name for good in Products])
        }

        self.manufacturies = tuple(thing for thing in to_be_recorded if isinstance(thing, Manufactury))
        self.extractors = tuple(thing for thing in to_be_recorded if isinstance(thing, Extractor))
        self.communes = tuple(thing for thing in to_be_recorded if isinstance(thing, Commune))

        self.folder = data_dir / self.name

        self.csv_files: dict[data_key, Path] = {
            'pop_size': self.folder / 'pop_size.csv',
            'pop_welfare': self.folder / 'pop_welfare.csv',
            'stock': self.folder / 'stock.csv',
            'goods_produced': self.folder / 'goods_produced.csv',
            'goods_demanded': self.folder / 'goods_demanded.csv',
            'goods_consumed': self.folder / 'goods_consumed.csv',
            'goods_satisfaction': self.folder / 'goods_satisfaction.csv',
        }

        self.graph_folder = self.folder / 'graphs'
        self.graph_files: dict[data_key, Path] = {
            'pop_size': self.folder / self.graph_folder / 'pop_size.png',
            'pop_welfare': self.folder / self.graph_folder / 'pop_welfare.png',
            'stock': self.folder / self.graph_folder / 'stock.png',
            'goods_produced': self.folder / self.graph_folder / 'goods_produced.png',
            'goods_demanded': self.folder / self.graph_folder / 'goods_demanded.png',
            'goods_consumed': self.folder / self.graph_folder / 'goods_consumed.png',
            'goods_satisfaction': self.folder / self.graph_folder / 'goods_satisfaction.png',
        }

    def _get_all_communes(self) -> Commune:
        communes = CommuneFactory.create_by_job()
        
        for industry in chain(self.manufacturies, self.extractors):
            communes += industry.workforce

        for commune in self.communes:
            communes += commune
        
        return communes    

    def record_pop_size(self):
        new_col: dict[str, Decimal] = {job.name: D(0) for job in Jobs}

        for key, pop in self._get_all_communes().items():
            if isinstance(key, tuple):
                new_col[key[1].name] += pop.size
            
            elif key in Jobs:
                new_col[key.name] += pop.size
            
            else:
                raise KeyError
        
        new_df = DataFrame(new_col, index=[0])
        self.data['pop_size'] = pd.concat([self.data['pop_size'], new_df], ignore_index=True) 

    def record_pop_welfare(self) -> None:
        new_col: dict[str, Decimal] = {job.name: D(0) for job in Jobs}
        divisor = 0

        for key, pop in self._get_all_communes().items():
            if isinstance(key, tuple):
                new_col[key[1].name] += pop.welfare
                divisor += 1
            
            elif key in Jobs:
                new_col[key.name] += pop.welfare
            
            else:
                raise KeyError
        
        if divisor != 0:
            new_col[Jobs.UNEMPLOYED.name] /= divisor
            
        new_df = DataFrame(new_col, index=[0])
        self.data['pop_welfare'] = pd.concat([self.data['pop_welfare'], new_df], ignore_index=True)
    
    def record_stockpile(self, stock: Stock, /):
        new_col: dict[str, Decimal] = {product.name: D(0) for product in Products}

        for product, good in stock.items():
            new_col[product.name] += good.amount

        new_df = DataFrame(new_col, index=[0])
        self.data['stock'] = pd.concat([self.data['stock'], new_df], ignore_index=True)

    def record_goods_produced(self, stock_before: Stock, stock_after: Stock, /):
        new_col: dict[str, Decimal] = {product.name: D(0) for product in Products}

        for product in Products:
            new_col[product.name] += stock_after[product].amount - stock_before[product].amount

        new_df = DataFrame(new_col, index=[0])
        self.data['goods_produced'] = pd.concat([self.data['goods_produced'], new_df], ignore_index=True)

    def record_goods_demanded(self):
        new_col: dict[str, Decimal] = {product.name: D(0) for product in Products}
        total_demand = create_stock()

        for manufactury in self.manufacturies:
            total_demand += manufactury.workforce.calc_goods_demand()
            total_demand += manufactury.calc_input_demand()
            
        for extractor in self.extractors:
            total_demand += extractor.workforce.calc_goods_demand()

        for commune in self.communes:
            total_demand += commune.calc_goods_demand()
        
        for product, demand in total_demand.items():
            new_col[product.name] += demand.amount
        
        new_df = DataFrame(new_col, index=[0])
        self.data['goods_demanded'] = pd.concat([self.data['goods_demanded'], new_df], ignore_index=True)

    def record_goods_consumed(self, stock_before: Stock, stock_after: Stock):
        new_col: dict[str, Decimal] = {product.name: D(0) for product in Products}

        for product in Products:
            new_col[product.name] += stock_before[product].amount - stock_after[product].amount

        new_df = DataFrame(new_col, index=[0])
        self.data['goods_consumed'] = pd.concat([self.data['goods_consumed'], new_df], ignore_index=True)

    def record_goods_satisfaction(self, stock_before: Stock):
        new_col: dict[str, Decimal] = {product.name: D(0) for product in Products}
        total_demand = create_stock()

        for manufactury in self.manufacturies:
            total_demand += manufactury.workforce.calc_goods_demand()
            total_demand += manufactury.calc_input_demand()
            
        for extractor in self.extractors:
            total_demand += extractor.workforce.calc_goods_demand()

        for commune in self.communes:
            total_demand += commune.calc_goods_demand()

        for product in Products:
            try:
                satisfaction = min(D(1), stock_before[product].amount / total_demand[product].amount)
            
            except (DivisionByZero, DivisionUndefined, InvalidOperation) as e:
                if isinstance(e, (DivisionUndefined, InvalidOperation)):
                    print(stock_before[product].amount, total_demand[product].amount)
                    raise e

                satisfaction = D(1)

            new_col[product.name] += satisfaction

        new_df = DataFrame(new_col, index=[0])
        self.data['goods_satisfaction'] = pd.concat([self.data['goods_satisfaction'], new_df], ignore_index=True)

    def _prepare_save(self):
        if not self.folder.exists():
            self.folder.mkdir()
        
        for file in self.csv_files.values():
            if not file.exists():
                file.open("x+").close()

    def save_csv(self, overwrite: bool = False) -> None:
        self._prepare_save()

        if overwrite or all(is_empty(file) for file in self.csv_files.values()):
            for key, df in self.data.items():
                df.to_csv(self.csv_files[key], sep=';', index=False)
        
        else:
            for key, df in self.data.items():
                old_df = pd.read_csv(self.csv_files[key], sep=';')
                new_df = pd.concat([old_df, df], ignore_index=True)
                new_df.to_csv(self.csv_files[key], sep=';', index=False)

    def plot_graph(self, which: data_key, /, *, title: str, xlabel: str, ylabel: str):
        
        if not self.graph_folder.exists():
            self.graph_folder.mkdir()
        
        if not self.graph_files[which].exists():
            self.graph_files[which].open('x+').close()

        df = self.data[which]
        
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
        fig.savefig(str(self.graph_files[which]), dpi=300)
        plt.close()

    def plot_all(self) -> None:

        # Population size
        self.plot_graph('pop_size', title='Population Size', xlabel='Time', ylabel='Size')

        # Population welfare
        self.plot_graph('pop_welfare', title='Welfare over time', xlabel='Time', ylabel='Welfare')

        # Population welfare
        self.plot_graph('stock', title='Stock', xlabel='Time', ylabel='Amount')

        # Products produced
        self.plot_graph('goods_produced', title='Products produced over time', xlabel='Time', ylabel='Amount')

        # Products demanded
        self.plot_graph('goods_demanded', title='Products demanded over time', xlabel='Time', ylabel='Amount')

        # Products consumed
        self.plot_graph('goods_consumed', title='Products consumed over time', xlabel='Time', ylabel='Amount')

        # Products satisfaction
        self.plot_graph('goods_satisfaction', title='Demand satisfaction', xlabel='Time', ylabel='Percentage')

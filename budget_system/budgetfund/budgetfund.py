import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

class InsufficientFundsError(Exception):
    """Raised when a fund does not have enough balance for an operation."""
    pass

class budgetfund: #this is the class for the whole budget of the family
    log_title=['action','amount','description','balance','status','date']
    
    def __init__(self,opening_balance,name=''):
        
        self.opening_balance=float(opening_balance)
        self.__balance=float(opening_balance)
        self.household_name=name
        self.__log=[]
        
    def validate(self, amount=0):
        """Check if there is enough balance, raise InsufficientFundsError if not."""
        try:
            if amount < 0:
                raise ValueError("Amount must be non-negative.")

            if amount > self.balance:
                raise InsufficientFundsError(
                    f"Insufficient balance: need {amount}, current {self.balance}"
                )
            return True

        except TypeError as e:
            print(f"[ERROR] Invalid amount type: {e}")
            raise

        except InsufficientFundsError as e:
            print(f"[ERROR] {e}")
            raise
        
    def add(self,amount,desciption='',date=None):
        if date is None:
            date = datetime.today().strftime("%Y-%m-%d")
        self.__balance+=float(amount)
        self.__log.append(['add',amount,desciption,self.get(),'succeeded',date])
        return True
        
    def sub(self, amount, description="", date=None):
        """Subtract an expense from the fund, with error handling."""
        try:
            self.validate(amount)

            # self.balance -= amount
            # self.log.append({...})

        except InsufficientFundsError:
            # self.log.append({... status=False ...})
            print("[ERROR] Transaction failed due to insufficient funds.")
        except Exception as e:
            print(f"[ERROR] Unexpected error in sub(): {e}")
            raise
            
    def get(self):
        return self.__balance
        
    def get_log(self):
        return [self.log_title,self.__log]
        
    def get_df(self, start=None, end=None):
        """Return log as DataFrame within [start, end]."""
        try:
            df = pd.DataFrame(self.log)

            if start is not None:
                start = pd.to_datetime(start)
                df = df[df["date"] >= start]

            if end is not None:
                end = pd.to_datetime(end)
                df = df[df["date"] <= end]

            return df

        except KeyError as e:
            print(f"[ERROR] Missing expected column in log: {e}")
            raise
        except (TypeError, ValueError) as e:
            print(f"[ERROR] Invalid date format for start/end: {e}")
            raise

    def summarize_month(self, start_month, end_month=''):
        if end_month=='':
            end_month=start_month
        df = self.get_df().copy()
        if df.empty:
            print("No transaction records.")
            return None

        df["date"] = pd.to_datetime(df["date"])

        start = pd.to_datetime(start_month)
        end = pd.to_datetime(end_month) + pd.offsets.MonthEnd(0)

        period_df = df[(df["date"] >= start) & (df["date"] <= end)]
        if period_df.empty:
            print("No transactions in this period.")
            return None

        success_df = period_df[period_df["status"] == "succeeded"].sort_values("date")
        if success_df.empty:
            print("No succeeded transaction in this period.")
            return None

        income = success_df[success_df["action"] == "add"]["amount"].sum()
        expense = success_df[success_df["action"] == "sub"]["amount"].sum()

        first = success_df.iloc[0]
        if first["action"] == "add":
            opening_balance = first["balance"] - first["amount"]
        else:
            opening_balance = first["balance"] + first["amount"]

        closing_balance = success_df.iloc[-1]["balance"]

        labels = ["Opening", "Income", "Expense", "Closing"]
        values = [opening_balance, income, expense, closing_balance]

        plt.figure(figsize=(14, 6))

        plt.subplot(1, 2, 1)
        plt.bar(labels, values)
        plt.title(f"Summary for {start_month} → {end_month}")
        plt.ylabel("Amount")
        plt.grid(axis="y", linestyle="--", alpha=0.5)

        df_exp = success_df[success_df["action"] == "sub"]

        plt.subplot(1, 2, 2)
        if df_exp.empty:
            plt.text(0.5, 0.5, "No expenses", ha="center", va="center", fontsize=12)
            plt.title(f"Expense Breakdown {start_month} → {end_month}")
        else:
            category_sum = df_exp.groupby("description")["amount"].sum()
            plt.pie(category_sum, labels=category_sum.index, autopct="%1.1f%%")
            plt.title(f"Expense Breakdown {start_month} → {end_month}")

        plt.tight_layout()
        plt.show()
        


    def __str__(self):
        return('The family budget of '+ self.household_name +' is: '+ str(self.get()))


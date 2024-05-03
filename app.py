from flask import Flask, render_template, request, redirect, url_for, session # type: ignore

app = Flask(__name__)
app.secret_key = 'e40e1abbe38492cd445589fe428be5b47e04588e08a29c57'

class CashMachine:
    def __init__(self):
        self.accounts = [
            {'account_number': '1001', 'PIN': '1234', 'balance': 1000, 'transactions': []},
            {'account_number': '1002', 'PIN': '5678', 'balance': 2000, 'transactions': []},
            {'account_number': '1003', 'PIN': '9012', 'balance': 500, 'transactions': []}
        ]

    def authenticate_pin(self, account_number, entered_pin):
        return any(
            account['account_number'] == account_number
            and account['PIN'] == entered_pin
            for account in self.accounts
        )

    def change_pin(self, account_number, new_pin):
        for account in self.accounts:
            if account['account_number'] == account_number:
                account['PIN'] = new_pin
                return True
        return False

    def cash_withdrawal(self, account_number, entered_pin, withdrawal_amount):
        for account in self.accounts:
            if account['account_number'] == account_number and account['PIN'] == entered_pin:
                if withdrawal_amount <= account['balance']:
                    account['balance'] -= withdrawal_amount
                    account['transactions'].append(f"Withdrawal: £{withdrawal_amount}")
                    return f"Withdrawal of £{withdrawal_amount} successful. Remaining balance: £{account['balance']}"
                else:
                    return "Insufficient balance."
        return "Incorrect PIN or account number."

cash_machine = CashMachine()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account_number = request.form['account_number']
        entered_pin = request.form['pin']
        if cash_machine.authenticate_pin(account_number, entered_pin):
            session['account_number'] = account_number  # Store account number in session
            session['pin'] = entered_pin  # Store PIN in session
            return redirect(url_for('options'))
        else:
            return render_template('login.html', message="Incorrect account number or PIN.")
    return render_template('login.html', message="")

@app.route('/options', methods=['GET', 'POST'])
def options():
    if request.method == 'POST':
        option = request.form['option']
        if option == 'change_pin':
            return redirect(url_for('change_pin'))
        elif option == 'withdraw':
            return redirect(url_for('withdraw'))
    return render_template('options.html')

@app.route('/change_pin', methods=['GET', 'POST'])
def change_pin():
    if request.method == 'POST':
        account_number = session.get('account_number')
        entered_pin = session.get('pin')
        new_pin = request.form['new_pin']
        if cash_machine.authenticate_pin(account_number, entered_pin):
            if cash_machine.change_pin(account_number, new_pin):
                return render_template('success.html', message="PIN changed successfully.")
            else:
                return render_template('error.html', message="Failed to change PIN.")
        else:
            return render_template('error.html', message="Incorrect account number or PIN.")
    return render_template('change_pin.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        account_number = session.get('account_number')
        entered_pin = session.get('pin')
        withdrawal_amount = float(request.form['withdrawal_amount'])
        if cash_machine.authenticate_pin(account_number, entered_pin):
            message = cash_machine.cash_withdrawal(account_number, entered_pin, withdrawal_amount)
            return render_template('success.html', message=message)
        else:
            return render_template('error.html', message="Incorrect account number or PIN.")
    return render_template('withdraw.html')

if __name__ == '__main__':
    app.run(debug=True)

import pdfplumber
import json
import os
import re

# ----------------------------
# File paths
# ----------------------------

BASE_DIR = r"C:\" # Add your directory
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
BUDGETS_FILE = os.path.join(DATA_DIR, "budgets.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
STATEMENTS_FOLD = "Statements" # Change depending on where you are putting your bank statements

# ----------------------------
# Clear console
# ----------------------------
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# ----------------------------
# Load / Save helpers
# ----------------------------
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# ----------------------------
# Load data
# ----------------------------
categories = load_json(CATEGORIES_FILE, ["Food", "Transport", "Entertainment", "Bills"])
budgets = load_json(BUDGETS_FILE, {})
history = load_json(HISTORY_FILE, {})

# ----------------------------
# Income input
# ----------------------------
def get_income():
    income_sources = []

    print("\n--- Enter Income Sources ---")

    while True:
        source = input("Enter income source (or press Enter to finish): ").strip()
        
        if source == "":
            break

        while True:
            amount_input = input(f"Enter amount for {source}: ")
            try:
                amount = float(amount_input)
                break
            except:
                print("Invalid number. Try again.")

        income_sources.append({
            "source": source,
            "amount": amount
        })

    total_income = sum(i["amount"] for i in income_sources)

    return income_sources, total_income

# ----------------------------
# Select PDF
# ----------------------------
def select_pdf_from_folder(folder_path):
    try:
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
    except Exception as e:
        print(f"Error accessing folder: {e}")
        return None

    if not files:
        print("No PDF files found in folder.")
        return None

    while True:
        print("\nAvailable PDF files:\n")

        for i, f in enumerate(files):
            print(f"{i+1}. {f}")

        print("\nEnter number to select file")
        print("R. Refresh list")
        print("Q. Quit")

        choice = input("\nYour choice: ").strip().lower()

        if choice == "q":
            return None

        if choice == "r":
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
            continue

        try:
            index = int(choice) - 1
            if 0 <= index < len(files):
                return os.path.join(folder_path, files[index])
        except:
            pass

        print("Invalid selection. Try again.")

# ----------------------------
# Extract transactions
# ----------------------------
def extract_transactions(pdf_path):
    transactions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if not text:
                continue

            for line in text.split("\n"):
                match = re.match(
                    r"([A-Za-z]{3}\s+\d{1,2})\s+([A-Za-z]{3}\s+\d{1,2})\s+(.*?)\s+(-?\$?\d+\.\d{2})",
                    line
                # Specific format it is looking for, will change depending on bank statement
                )

                if match:
                    try:
                        amount = float(match.group(4).replace("$", ""))
                        transactions.append({
                            "date": match.group(1),
                            "post_date": match.group(2),
                            "description": match.group(3),
                            "amount": amount
                        })
                    except:
                        continue

    return transactions

# ----------------------------
# Category selection
# ----------------------------
def choose_category():
    while True:
        print("\nCategories:")
        for i, cat in enumerate(categories):
            print(f"{i+1}. {cat}")
        print("A. Add new category")

        choice = input("Select category: ").strip()

        if choice.lower() == "a":
            new_cat = input("Enter new category name: ").strip()

            if new_cat and new_cat not in categories:
                categories.append(new_cat)

                while True:
                    try:
                        budgets[new_cat] = float(input(f"Set monthly budget for {new_cat}: "))
                        break
                    except:
                        print("Invalid number.")

            continue

        try:
            return categories[int(choice) - 1]
        except:
            print("Invalid choice.")

# ----------------------------
# Manage categories
# ----------------------------
def manage_categories():
    while True:
        clear_console()
        print("=== Category Manager ===\n")

        for i, cat in enumerate(categories):
            print(f"{i+1}. {cat}")

        print("\nOptions:")
        print("A. Add category")
        print("D. Delete category")
        print("C. Continue")

        choice = input("\nChoice: ").strip().lower()

        if choice == "a":
            new_cat = input("Enter new category name: ").strip()

            if new_cat and new_cat not in categories:
                categories.append(new_cat)

                while True:
                    try:
                        budgets[new_cat] = float(input(f"Set monthly budget for {new_cat}: "))
                        break
                    except:
                        print("Invalid number.")

        elif choice == "d":
            try:
                idx = int(input("Enter category number to delete: ")) - 1
                if 0 <= idx < len(categories):
                    cat = categories.pop(idx)
                    budgets.pop(cat, None)
                    history.pop(cat, None)
            except:
                print("Invalid input.")

        elif choice == "c":
            break

# ----------------------------
# Budget setup
# ----------------------------
def setup_budgets():
    print("\n--- Budget Review ---")

    for cat in categories:
        current = budgets.get(cat)

        if current is not None:
            val = input(f"{cat}: Current = ${current:.2f} (Enter to keep): ")
            if val:
                try:
                    budgets[cat] = float(val)
                except:
                    print("Invalid input.")
        else:
            while True:
                try:
                    budgets[cat] = float(input(f"Set budget for {cat}: "))
                    break
                except:
                    print("Invalid number.")

# ----------------------------
# Categorize transactions
# ----------------------------
def categorize_transactions(transactions):
    categorized = []

    for t in transactions:
        print(f"\n{t['date']} | {t['description']} | ${t['amount']:.2f}")
        t["category"] = choose_category()
        categorized.append(t)
        clear_console()

    return categorized

# ----------------------------
# History helper func
# ----------------------------
def get_last_month_diff(category):
    if category in history and len(history[category]) > 0:
        return history[category][-1]
    return 0

# ----------------------------
# Analyze
# ----------------------------
def analyze(categorized, total_income):
    totals = {}
    total_spent = sum(t["amount"] for t in categorized)

    for t in categorized:
        cat = t["category"]
        totals[cat] = totals.get(cat, 0) + t["amount"]

    report = {}

    for cat in categories:
        spent = totals.get(cat, 0)
        budget = budgets.get(cat, 0)
        diff = budget - spent
        last_diff = get_last_month_diff(cat)

        percent_total = (spent / total_spent * 100) if total_spent > 0 else 0
        percent_income = (spent / total_income * 100) if total_income > 0 else 0

        report[cat] = {
            "spent": spent,
            "budget": budget,
            "difference": diff,
            "percent": percent_total,
            "percent_income": percent_income,
            "last_diff": last_diff
        }

    total_percent_income = (total_spent / total_income * 100) if total_income > 0 else 0
    remaining_income = total_income - total_spent

    return report, total_spent, total_percent_income, remaining_income

# ----------------------------
# Month helpers func
# ----------------------------
def get_month_name(transactions):
    if not transactions:
        return "Unknown_Month"
    return transactions[-1]["date"].split()[0]

def get_month_output_dir(transactions):
    path = os.path.join(BASE_DIR, get_month_name(transactions))
    os.makedirs(path, exist_ok=True)
    return path

# ----------------------------
# Display Labels (Have to be the same in both saved and printed report)
# ----------------------------
LABELS = {
    "income": "Income",
    "total_income": "Total Income",
    "total_spending": "Total Spending",
    "remaining_income": "Remaining Income",
    "percent_income_spent": "% Income Spent",

    "spent": "Spent",
    "budget": "Budget",
    "percent_total": "% of Total Spent",
    "percent_income": "% of Income",
    "difference": "Difference from budg",
    "last_month_diff": "Last Month Diff from budg",

    "category_breakdown": "Category Breakdown",
    "report_title": "Spending Report"
}

# ----------------------------
# Save monthly report
# ----------------------------
def save_monthly_report(categorized, report, total_income, total_spent, total_percent_income, remaining_income):
    month = get_month_name(categorized)
    filename = os.path.join(get_month_output_dir(categorized), "Monthly_Report.txt")

    with open(filename, "w") as f:
        f.write(f"===== {month} {LABELS['report_title']} =====\n\n")

        f.write(f"{LABELS['total_income']}: ${total_income:.2f}\n")
        f.write(f"{LABELS['total_spending']}: ${total_spent:.2f}\n")
        f.write(f"{LABELS['remaining_income']}: ${remaining_income:.2f}\n")
        f.write(f"{LABELS['percent_income_spent']}: {total_percent_income:.2f}%\n\n")

        f.write(f"{LABELS['category_breakdown']}:\n")
        f.write("-------------------\n")

        for cat, data in report.items():
            f.write(f"{cat}\n")
            f.write(f"  {LABELS['spent']}: ${data['spent']:.2f}\n")
            f.write(f"  {LABELS['budget']}: ${data['budget']:.2f}\n")
            f.write(f"  {LABELS['percent_total']}: {data['percent']:.0f}%\n")
            f.write(f"  {LABELS['percent_income']}: {data['percent_income']:.2f}%\n")
            f.write(f"  {LABELS['difference']}: ${data['difference']:.2f}\n")
            f.write(f"  {LABELS['last_month_diff']}: ${data['last_diff']:.2f}\n\n")

# ----------------------------
# Save categorized transactions
# ----------------------------
def save_outputs(categorized):
    filename = os.path.join(get_month_output_dir(categorized), "Categorized_Spending.txt")

    with open(filename, "w") as f:
        for t in categorized:
            f.write(f"{t['date']} | {t['description']} | ${t['amount']} | {t['category']}\n")

# ----------------------------
# Update history
# ----------------------------
def update_history(report):
    for cat, data in report.items():
        history.setdefault(cat, []).append(data["difference"])

# ----------------------------
# Main
# ----------------------------
def main():
    folder_path = os.path.join(BASE_DIR, STATEMENTS_FOLD)

    pdf_path = select_pdf_from_folder(folder_path)
    if not pdf_path:
        return

    transactions = extract_transactions(pdf_path)
    print(f"\nFound {len(transactions)} transactions.")

    if not transactions:
        print("No transactions found.")
        return

    manage_categories()
    setup_budgets()

    income_sources, total_income = get_income() # May use income source in the future

    categorized = categorize_transactions(transactions)

    report, total_spent, total_percent_income, remaining_income = analyze(categorized, total_income)


    print("\n--- Summary ---")

    print(f"\n{LABELS['total_income']}: ${total_income:.2f}")
    print(f"{LABELS['total_spending']}: ${total_spent:.2f}")
    print(f"{LABELS['remaining_income']}: ${remaining_income:.2f}")
    print(f"{LABELS['percent_income_spent']}: {total_percent_income:.2f}%\n")

    for cat, data in report.items():
        print(
            f"{cat}: "
            f"{LABELS['spent']} ${data['spent']:.2f} | "
            f"{LABELS['budget']} ${data['budget']:.2f} | "
            f"{LABELS['percent_total']}: {data['percent']:.2f}% | "
            f"{LABELS['percent_income']}: {data['percent_income']:.2f}% | "
            f"{LABELS['difference']} ${data['difference']:.2f} | "
            f"{LABELS['last_month_diff']}: ${data['last_diff']:.2f}\n"
        )

    
    save_outputs(categorized)
    save_monthly_report(categorized, report, total_income, total_spent, total_percent_income, remaining_income)
    update_history(report)

    save_json(CATEGORIES_FILE, categories)
    save_json(BUDGETS_FILE, budgets)
    save_json(HISTORY_FILE, history)

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()

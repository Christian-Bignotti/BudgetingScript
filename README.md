# BudgetingScript
Simple bare bones budgeting script. Wrote it to keep track of my own spending. Takes bank statement as an input and outputs a report of the monthly report. Also keeps a history of the previous months data (if there was a previous months report), to compare with the current month spending, as well as saving and giving the option to reuse and edit last months budgets and categories.

If one wants to use this, edit the "BASE_DIR" and "STATEMENTS_FOLD" to match the directory and folder your bank statements are saved in. Addititonally, depending on how you bank statement prints out each transactiion, you may have to edit the "extract_transactions" function. 

Example output:


--- Summary ---

Total Income: $12345.00
Total Spending: $2409.35
Remaining Income: $9935.65
% Income Spent: 19.52%

Food: Spent $447.75 | Budget $300.00 | % of Total Spent: 18.58% | % of Income: 3.63% | Difference from budg $-147.75 | Last Month Diff from budg: $-110.17

Transport: Spent $1443.68 | Budget $300.00 | % of Total Spent: 59.92% | % of Income: 11.69% | Difference from budg $-1143.68 | Last Month Diff from budg: $-1069.94

Entertainment: Spent $491.77 | Budget $300.00 | % of Total Spent: 20.41% | % of Income: 3.98% | Difference from budg $-191.77 | Last Month Diff from budg: $-196.64

Bills: Spent $26.15 | Budget $300.00 | % of Total Spent: 1.09% | % of Income: 0.21% | Difference from budg $273.85 | Last Month Diff from budg: $167.40



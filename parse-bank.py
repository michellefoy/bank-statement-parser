import PyPDF2
import csv
import re

def extract_text_from_pdf(pdf_path):
    pdf_file = open(pdf_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    pdf_file.close()
    return text

def get_post_date(date_info):
    # Extract the post date from the date_info
    if 'Ý' in date_info[3]:
        return f"{date_info[2]} {date_info[3].split('Ý')[0]}"
    
    return f"{date_info[2]} {date_info[3]}"

def get_description(date_info):
    # Extract the description from the line
    description = " ".join(date_info[4:])
    if 'Ý' in date_info[3]:
        return f"{date_info[3].split('Ý')[1]} {description}"
    
    return description


def parse_bank_statement_raw(text):
    # This function should be customized based on the structure of your bank statement
    lines = text.split('\n')
    transactions = []
    for line in lines:
        # Example parsing logic (customize as needed)
        if "DATE" in line and "DESCRIPTION" in line and "AMOUNT" in line:
            continue # Skip header line
        parts = line.split()
        if len(parts) >= 3:
            date = parts[0]
            description = " ".join(parts[1:-1])
            amount = parts[-1]
            transactions.append([date, description, amount])
    return transactions


def parse_bank_statement(text):
    # Regular expression to match the transaction format
    transaction_pattern = re.compile(r'(\w{3} \d{2} \w{3} \d{2}.*?\n.*?\d+\.\d{2})')
    transactions = transaction_pattern.findall(text)
    print(f"Found {len(transactions)} transactions")
    parsed_transactions = []
    for transaction in transactions:
        lines = transaction.split('\n')
        date_info = lines[0].split()
        transaction_date = f"{date_info[0]} {date_info[1]}"
        post_date = get_post_date(date_info)
        description = get_description(date_info)
        category_amount = lines[1].rsplit(' ', 1)
        category = category_amount[0]
        amount = category_amount[1] if len(category_amount) > 1 else "0.00"
        if category != "Total payments":
            parsed_transactions.append([transaction_date, post_date, description, category, amount])
    return parsed_transactions

def save_to_csv(transactions, csv_path):
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Transaction Date", "Post Date", "Description", "Category", "Amount"])
        writer.writerows(transactions)

if __name__ == "__main__":
    pdf_path = './statements/2025_04_April_Account_Statement.pdf'
    csv_path = './output.csv'
    
    text = extract_text_from_pdf(pdf_path)
    transactions = parse_bank_statement(text)
    save_to_csv(transactions, csv_path)
    print(f"Bank statement has been parsed and saved to {csv_path}")

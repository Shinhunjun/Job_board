import pandas as pd
import re

# Load the Excel file
file_path = '/Users/hunjunsin/Desktop/box/Introduction_DMB/project/ddanielhasan.github.io/data/company_data.xlsx'  # Update this path
data = pd.read_excel(file_path)


# Preprocess the 'num_employee' column to remove line breaks and extra spaces
data['num_employee'] = data['num_employee'].apply(lambda x: re.sub(r'\s+', ' ', str(x).strip()))

# Function to clean up and categorize the 'num_employee' column
def categorize_num_employee(num_employee_text):
    # Check if it contains a year or unknown information
    if re.search(r'\b\d{4}\b', num_employee_text):  # Four-digit number likely represents a year
        return "Unknown"
    
    # Extract numeric value and categorize
    match = re.search(r'(\d+)', num_employee_text)
    if match:
        num_employees = int(match.group(1).replace(",", ""))  # Remove commas for larger numbers
        # Categorize based on employee count
        if num_employees >= 1000:
            return "many (1000+)"
        elif 100 <= num_employees < 1000:
            return "normal (100-999)"
        else:
            return "less (<100)"
    return "Unknown"

# Apply the function to 'num_employee' column
data['num_employee_category'] = data['num_employee'].apply(lambda x: categorize_num_employee(str(x)))

# Simplify 'company_category' by selecting the primary category if there are multiple
def primary_category(categories_text):
    categories = categories_text.splitlines()  # Splitting by line breaks
    return categories[0] if categories else "Unknown"

# Apply the function to 'company_category' column
data['primary_company_category'] = data['company_category'].apply(lambda x: primary_category(str(x)))

# Clean up 'company_overview' to remove extra whitespace and line breaks
data['company_overview_cleaned'] = data['company_overview'].apply(lambda x: re.sub(r'\s+', ' ', str(x).strip()))

# Drop unnecessary columns, including links and links-href
data.drop(columns=['pagination', 'web-scraper-order', 'web-scraper-start-url', 'links', 'links-href'], inplace=True)

# Save or display the cleaned data
output_path = '/Users/hunjunsin/Desktop/box/Introduction_DMB/project/ddanielhasan.github.io/data/cleaned_company_data.xlsx'
data.to_excel(output_path, index=False)

print("Data cleaned and saved to:", output_path)
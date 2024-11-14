import pandas as pd
import re

# Load the Excel file
file_path = '/Users/hunjunsin/Desktop/box/Introduction_DMB/project/ddanielhasan.github.io/data/company_data.xlsx'
data = pd.read_excel(file_path)

# Drop unnecessary columns
data.drop(columns=['pagination', 'web-scraper-order', 'web-scraper-start-url', 'links', 'links-href'], inplace=True)

# Preprocess the 'num_employee' column to remove line breaks and extra spaces
data['num_employee'] = data['num_employee'].apply(lambda x: re.sub(r'\s+', ' ', str(x).strip()))

# Function to clean up and categorize the 'num_employee' column
def categorize_num_employee(num_employee_text):
    if re.search(r'\b\d{4}\b', num_employee_text):  # Detects a year
        return "Unknown"
    match = re.search(r'(\d+)', num_employee_text)
    if match:
        num_employees = int(match.group(1).replace(",", ""))
        if num_employees >= 1000:
            return "many (1000+)"
        elif 100 <= num_employees < 1000:
            return "normal (100-999)"
        else:
            return "less (<100)"
    return "Unknown"

# Apply categorization to 'num_employee' column
data['num_employee_category'] = data['num_employee'].apply(lambda x: categorize_num_employee(str(x)))

# Simplify 'company_category' to primary category
def primary_category(categories_text):
    categories = categories_text.splitlines()
    return categories[0] if categories else "Unknown"

# Apply the function to 'company_category' column
data['primary_company_category'] = data['company_category'].apply(lambda x: primary_category(str(x)))

# Clean up 'company_overview'
data['company_overview_cleaned'] = data['company_overview'].apply(lambda x: re.sub(r'\s+', ' ', str(x).strip()))

# Drop original columns after processing
data.drop(columns=['num_employee', 'company_category', 'company_overview'], inplace=True)

# Rename columns to match SQL and keep only final required columns
data = data.rename(columns={
    'primary_company_category': 'industry_name',
    'company_overview_cleaned': 'description',
    'num_employee_category': 'employee_count',
    'company_title': 'name',
    'company_logo-src': 'logo_url',
    'company_location': 'location',
    'company_website-href': 'website' 
})

# Keep the required columns in the final output
final_columns = ['name', 'logo_url', 'location', 'industry_name', 'description', 'employee_count','website']
data = data[final_columns]



# Save the cleaned data
output_path = '/Users/hunjunsin/Desktop/box/Introduction_DMB/project/ddanielhasan.github.io/data/cleaned_company_data.xlsx'
data.to_excel(output_path, index=False)

print("Data cleaned and saved to:", output_path)
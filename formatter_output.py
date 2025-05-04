import csv
import io
import re

input_file_path = 'csv abosult path'
output_report_file_path = 'formatted_output.csv'
file_encoding = 'utf-8'

def format_hungarian_phone(phone_str):
    if not phone_str: # Handle empty input
        return ""
    digits = re.sub(r'[\s\(\)\-\/]', '', phone_str)

    if phone_str.strip().startswith('(061)') or phone_str.strip().startswith('(06 1)'):
         num_part = digits[3:] # Get digits after (061)
         if len(num_part) == 7:
              return f"06 1 {num_part[:3]} {num_part[3:]}"

    if digits.startswith('06'):
        if len(digits) == 11:
            return f"06 {digits[2:4]} {digits[4:7]} {digits[7:]}"
    elif digits.startswith('+36'):
        temp_digits = '06' + digits[3:]
        if len(temp_digits) == 11:
             return f"06 {temp_digits[2:4]} {temp_digits[4:7]} {temp_digits[7:]}"
    elif len(digits) == 9 and (digits.startswith('20') or digits.startswith('30') or digits.startswith('70') or digits.startswith('52') or digits.startswith('1')): # Mobile, Debrecen, Budapest prefix check
         temp_digits = '06' + digits
         if len(temp_digits) == 11:
              if digits.startswith('1'):
                    return f"06 1 {temp_digits[3:6]} {temp_digits[6:]}"
              else:
                    return f"06 {temp_digits[2:4]} {temp_digits[4:7]} {temp_digits[7:]}"
    if digits.isdigit() and len(digits) > 5:
        return digits
    cleaned_original = phone_str.strip()
    return cleaned_original if cleaned_original else ""


parsed_records = []

print(f"Attempting to read semicolon-delimited data from: {input_file_path}")

try:
    with open(input_file_path, mode='r', encoding=file_encoding) as infile:
        reader = csv.reader(infile, delimiter=';')
        for row in reader:
            if len(row) == 4:
                name, type_info, address, phone = row
                formatted_phone = format_hungarian_phone(phone)
                parsed_records.append({
                    "Name": name.strip(),
                    "Type": type_info.strip(),
                    "Address": address.strip(),
                    "Phone": formatted_phone
                })
            else:
                print(f"Skipping row, unexpected number of fields: {row}")


except FileNotFoundError:
    print(f"ERROR: Input file not found: {input_file_path}")
    exit()
except Exception as e:
    print(f"Error reading input file: {e}")
    exit()

print(f"Parsed {len(parsed_records)} records. Writing formatted report to: {output_report_file_path}")

try:
    with open(output_report_file_path, mode='w', encoding=file_encoding) as outfile:
        if not parsed_records:
            outfile.write("No records found in the input file.\n")
        else:
            for i, record in enumerate(parsed_records):
                outfile.write("-" * 50 + "\n")
                outfile.write(f"Record:  {i + 1}\n")
                outfile.write(f"Name:    {record['Name']}\n")
                outfile.write(f"Type:    {record['Type']}\n")
                outfile.write(f"Address: {record['Address']}\n")
                outfile.write(f"Phone:   {record['Phone']}\n")

            outfile.write("-" * 50 + "\n")

    print(f"Formatted report successfully saved to {output_report_file_path}")

except Exception as e:
    print(f"An error occurred while writing the report file: {e}")
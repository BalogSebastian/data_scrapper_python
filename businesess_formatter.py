import csv
import io
import re

input_csv_file_path = 'absolut path csv'
output_file_path = ('first_step.csv')
ignored_content = {'', '·', '', '', '', '', 'Webhely', 'Útvonalterv', 'Nincs vélemény', 'Helyszíni szolgáltatások', 'Helyben vásárlás', 'Átvétel az üzletben', 'Online időpontok'} # Added more common non-data words
output_delimiter = ';'
file_encoding = 'utf-8'

def format_hungarian_phone(phone_str):
    digits = re.sub(r'[\s\(\)\-\/]', '', phone_str)
    if digits.startswith('06'):
        if len(digits) == 11:
            return f"06 {digits[2:4]} {digits[4:]}"
    elif digits.startswith('+36'):
        temp_digits = '06' + digits[3:]
        if len(temp_digits) == 11:
             return f"06 {temp_digits[2:4]} {temp_digits[4:]}"
    elif len(digits) == 9 and (digits.startswith('20') or digits.startswith('30') or digits.startswith('70') or digits.startswith('52')):
         temp_digits = '06' + digits
         if len(temp_digits) == 11:
              return f"06 {temp_digits[2:4]} {temp_digits[4:]}"
    elif len(digits) == 6 and phone_str.startswith('(06 52)'):
        temp_digits = '0652' + digits
        if len(temp_digits) == 11:
             return f"06 {temp_digits[2:4]} {temp_digits[4:]}"

    if len(digits) < 6:
         return None
    return phone_str

parsed_data = []
header_keywords = ["qBF1Pd", "MW4etd"]

print(f"Attempting to read data from: {input_csv_file_path}")
try:
    with open(input_csv_file_path, mode='r', newline='', encoding=file_encoding) as infile:
        reader = csv.reader(infile, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in reader:
            if not row or all(field.strip() == '' for field in row) or (row and row[0].strip() in header_keywords):
                continue
            parsed_data.append([field.strip() for field in row])
except FileNotFoundError:
    print(f"ERROR: Input file not found: {input_csv_file_path}")
    exit()
except Exception as e:
    print(f"Error reading input file: {e}")
    exit()

print(f"Parsed {len(parsed_data)} data rows. Processing and writing selected fields to: {output_file_path}")

address_keywords = {' u.', ' utca', ' út', ' tér', ' krt.', ' sor', ' köz'}
type_keywords = {'iroda', 'bolt', 'szobor', 'iskola', 'gimnázium', 'étterem', 'kávézó', 'szolgáltató', 'központ', 'ügyvéd', 'tanácsadó', 'kozmetikus', 'fényképész', 'bőrgyógyász', 'ingatlan', 'ház', 'gyógyszertár'}

try:
    with open(output_file_path, mode='w', encoding=file_encoding) as outfile:
        records_written = 0
        for i, data_row in enumerate(parsed_data):
            cleaned_fields = [field for field in data_row if field not in ignored_content]

            if not cleaned_fields:
                 continue

            found_name = cleaned_fields[0]
            found_type = ""
            found_address = ""
            found_phone = ""
            processed_indices = {0}

            for idx, field in enumerate(cleaned_fields[1:], start=1):
                if not found_phone and (re.search(r'(\d{2,}[\s\(\)\-]?){3,}', field) or field.startswith('+')):
                    formatted_num = format_hungarian_phone(field)
                    if formatted_num:
                        found_phone = formatted_num
                        processed_indices.add(idx)
                        continue

                if not found_address and any(kw in field.lower() for kw in address_keywords) and re.search(r'\d', field): # Contains keyword and a digit
                    found_address = field
                    processed_indices.add(idx)
                    continue

                if not found_type and any(kw in field.lower() for kw in type_keywords):
                     if len(field.split()) < 4 and 'http' not in field:
                          found_type = field
                          processed_indices.add(idx)
                          continue
            output_fields = [
                found_name,
                found_type,
                found_address,
                found_phone
            ]

            if output_fields[0]:
                 output_line = output_delimiter.join(output_fields)
                 outfile.write(output_line + "\n")
                 records_written += 1


    print(f"{records_written} records successfully processed and saved to {output_file_path}")
    if len(parsed_data) > records_written:
         print(f"{len(parsed_data) - records_written} original rows might have been skipped due to filtering or lack of identifiable name.")

except Exception as e:
    print(f"An error occurred during processing or writing the output file: {e}")
from modules.cleaner import (
    clean_company_name,
    clean_phone,
    clean_website,
)

print(clean_company_name("ABC SECURITY (PTY) LTD"))
print(clean_company_name("Guardian Security CC"))

print(clean_phone("011 555 1234"))
print(clean_phone("+27 (11) 555-1234"))

print(clean_website("https://www.abc.co.za/"))
print(clean_website("http://guardian.co.za"))
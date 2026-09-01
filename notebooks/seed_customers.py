"""
Seed the customers table with fake data using Faker.

Run:  python notebooks/seed_customers.py
"""

import random
import string

from faker import Faker

from backend.db.queries import insert_customer, get_customer_by_pan


NUM_CUSTOMERS = 50
EMPLOYMENT_TYPES = ["Salaried", "Self-Employed", "Business Owner", "Government", "Freelancer"]


def fake_pan():
    letters = "".join(random.choices(string.ascii_uppercase, k=5))
    digits = "".join(random.choices(string.digits, k=4))
    last = random.choice(string.ascii_uppercase)
    return letters + digits + last


def fake_aadhaar_masked():
    last_four = "".join(random.choices(string.digits, k=4))
    return "XXXX-XXXX-" + last_four


def main():
    fake = Faker("en_IN")
    inserted = 0

    for _ in range(NUM_CUSTOMERS):
        pan = fake_pan()

        # Skip if PAN already exists
        if get_customer_by_pan(pan):
            continue

        name = fake.name()
        dob = fake.date_of_birth(minimum_age=21, maximum_age=65)
        mobile = "9" + "".join(random.choices(string.digits, k=9))
        email = fake.email()
        monthly_income = random.randint(15000, 200000)
        employment_type = random.choice(EMPLOYMENT_TYPES)

        insert_customer(
            name=name,
            pan=pan,
            aadhaar_masked=fake_aadhaar_masked(),
            dob=dob,
            mobile=mobile,
            email=email,
            monthly_income=monthly_income,
            employment_type=employment_type,
        )
        inserted += 1

    print(f"{inserted} customers seeded.")


if __name__ == "__main__":
    main()

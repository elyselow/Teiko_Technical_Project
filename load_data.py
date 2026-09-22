import csv
import sqlite3


DB_FILE = "cell_counts.db"


def main():
    # Create the SQLite database
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # Create subjects table
    cursor.execute("""
        CREATE TABLE subjects (
            subject TEXT PRIMARY KEY,
            project TEXT NOT NULL,
            condition TEXT NOT NULL,
            age INTEGER NOT NULL,
            sex TEXT NOT NULL,
            treatment TEXT NOT NULL,
            response TEXT
        )
    """)

    # Create samples table
    cursor.execute("""
        CREATE TABLE samples (
            sample TEXT PRIMARY KEY,
            subject TEXT NOT NULL,
            sample_type TEXT NOT NULL,
            time_from_treatment_start INTEGER NOT NULL,
            b_cell INTEGER NOT NULL,
            cd8_t_cell INTEGER NOT NULL,
            cd4_t_cell INTEGER NOT NULL,
            nk_cell INTEGER NOT NULL,
            monocyte INTEGER NOT NULL,
            FOREIGN KEY (subject) REFERENCES subjects(subject)
        )
    """)

    subjects_inserted = set()

    # Read the CSV file
    with open("cell-count.csv", "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            subject = row["subject"]

            # Add subject only once
            if subject not in subjects_inserted:
                response = row["response"]

                # Convert missing response values to NULL
                if response.strip().lower() in {"", "nan", "na", "null"}:
                    response = None

                cursor.execute("""
                    INSERT INTO subjects (
                        subject,
                        project,
                        condition,
                        age,
                        sex,
                        treatment,
                        response
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    subject,
                    row["project"],
                    row["condition"],
                    int(row["age"]),
                    row["sex"],
                    row["treatment"],
                    response
                ))

                subjects_inserted.add(subject)

            # Add sample and cell-count information
            cursor.execute("""
                INSERT INTO samples (
                    sample,
                    subject,
                    sample_type,
                    time_from_treatment_start,
                    b_cell,
                    cd8_t_cell,
                    cd4_t_cell,
                    nk_cell,
                    monocyte
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["sample"],
                subject,
                row["sample_type"],
                int(row["time_from_treatment_start"]),
                int(row["b_cell"]),
                int(row["cd8_t_cell"]),
                int(row["cd4_t_cell"]),
                int(row["nk_cell"]),
                int(row["monocyte"])
            ))

    # Save changes
    conn.commit()

    # Close the database connection
    conn.close()


if __name__ == "__main__":
    main()

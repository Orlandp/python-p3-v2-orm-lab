from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:
    all = {}

    def __init__(self, year, summary, employee_id):
        self.id = None
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return f"<Review id={self.id} year={self.year} employee_id={self.employee_id}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            );
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews;")
        CONN.commit()

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("year must be an int")
        if value < 2000:
            raise ValueError("year must be >= 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str):
            raise ValueError("summary must be a string")
        if not value.strip():
            raise ValueError("summary cannot be empty")
        self._summary = value.strip()

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if hasattr(value, "id"):
            value = value.id
        if not isinstance(value, int):
            raise ValueError("employee_id must be an int")
        row = CURSOR.execute("SELECT id FROM employees WHERE id = ?", (value,)).fetchone()
        if not row:
            raise ValueError("employee_id must reference a persisted Employee")
        self._employee_id = value

    def save(self):
        if self.id is None:
            CURSOR.execute(
                "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)",
                (self.year, self.summary, self.employee_id),
            )
            CONN.commit()
            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self
        else:
            self.update()
        return self

    @classmethod
    def create(cls, year, summary, employee_id_or_employee):
        obj = cls(year, summary, employee_id_or_employee)
        return obj.save()

    @classmethod
    def instance_from_db(cls, row):
        rid, year, summary, employee_id = row
        inst = cls.all.get(rid)
        if inst:
            inst.year = year
            inst.summary = summary
            inst.employee_id = employee_id
        else:
            inst = cls(year, summary, employee_id)
            inst.id = rid
            cls.all[rid] = inst
        return inst

    @classmethod
    def find_by_id(cls, rid):
        row = CURSOR.execute(
            "SELECT id, year, summary, employee_id FROM reviews WHERE id = ?",
            (rid,),
        ).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        if self.id is None:
            raise ValueError("Cannot update unsaved Review")
        CURSOR.execute(
            "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?",
            (self.year, self.summary, self.employee_id, self.id),
        )
        CONN.commit()
        type(self).all[self.id] = self
        return self

    def delete(self):
        if self.id is None:
            return
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        CONN.commit()
        type(self).all.pop(self.id, None)
        self.id = None

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute("SELECT id, year, summary, employee_id FROM reviews").fetchall()
        return [cls.instance_from_db(row) for row in rows]






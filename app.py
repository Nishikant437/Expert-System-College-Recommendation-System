from flask import Flask, render_template, request
import mysql.connector
import re

app = Flask(__name__)

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Yash@2004",
    database="capstone"
)

def extract_districts(college_names):
    districts = set()
    for name in college_names:
        match = re.search(r'[-,]\s*([A-Za-z\s]+)$', name[0])
        if match:
            districts.add(match.group(1).strip().lower())
    return sorted(districts)

@app.route('/')
def index():
    cursor = db.cursor()
    cursor.execute("SELECT College_Name FROM college")
    college_names = cursor.fetchall()
    districts = extract_districts(college_names)
    return render_template('index.html', districts=districts)

@app.route('/search', methods=['POST'])
def search():
    try:
        percentage = float(request.form['percentage'])
        branch = request.form['branch']
        category = request.form['category']
        district = request.form['district'].strip().lower()

        # SQL query to select colleges within ±3% range and filter by district, limit to 15 results
        cursor = db.cursor()
        query = f"""
            SELECT c.College_Name, co.Course, co.{category} 
            FROM courses co 
            JOIN college c ON co.College_ID = c.College_ID 
            WHERE co.Course = %s 
            AND co.{category} BETWEEN %s AND %s
            AND LOWER(c.College_Name) LIKE %s  
            ORDER BY co.{category} DESC  
            LIMIT 15  
        """
        lower_bound = percentage - 3
        upper_bound = percentage + 3
        cursor.execute(query, (branch, lower_bound, upper_bound, f'%{district}%'))

        results = cursor.fetchall()
        print(f"Total results fetched: {len(results)}")
        for result in results:
            print(result)

        return render_template('results.html', results=results)

    except KeyError as e:
        return f"Missing form field: {e}", 400
    except Exception as e:
        return f"An error occurred: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)

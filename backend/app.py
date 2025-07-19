from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

# MySQL connection setup
def get_db_connection():
    return mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "root123"),
    port=int(os.getenv("DB_PORT", 3307)),
    database=os.getenv("DB_NAME", "task_agent")
)

# Load employee data
def load_employees():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert skills to list
    for e in employees:
        e['skills'] = [s.strip().lower() for s in e['skills'].split(',')]
    return employees

def assign_and_increment(title, skills, priority, emp_id, assigned_by_ai):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert task with assignment
    cursor.execute("""
        INSERT INTO tasks (title, required_skills, priority, assigned_to, assigned_by_ai)
        VALUES (%s, %s, %s, %s, %s)
    """, (title, skills, priority, emp_id, assigned_by_ai))

    # Increment employee workload if an employee was assigned
    if emp_id is not None:
        cursor.execute("""
            UPDATE employees SET workload = workload + 1 WHERE id = %s
        """, (emp_id,))

    conn.commit()
    cursor.close()
    conn.close()

@app.route('/assign-task', methods=['POST'])
def assign_task():
    import re

    data = request.get_json()
    title = data.get('title', '')
    skills = data.get('skills', '')
    priority = data.get('priority', '')
    task_description = f"{title} (Skills: {skills}, Priority: {priority})"

    employees = load_employees()
    
    required_skills = [s.strip().lower() for s in skills.split(",")]
    filtered_employees = []

    required_skills = [s.strip().lower() for s in skills.split(",")]
    filtered_employees = []

    for e in employees:
        matches = sum(1 for skill in e['skills'] if skill in required_skills)
        if matches > 0 and e['workload'] <= 10:
             e['match_count'] = matches  # Optional for future use
             filtered_employees.append(e)
             
             
# Use only relevant employees in the prompt
# Step: Sort alphabetically by name
    employees = sorted(filtered_employees, key=lambda e: e['name'].lower())

    print("Filtered employees:")
    for emp in filtered_employees:
        print(f"ID: {emp['id']}, Name: {emp['name']}, Skills: {emp['skills']}, Workload: {emp['workload']}")


    prompt = f"""
                    You are a task assignment assistant. A task needs to be assigned to the most suitable employee.

                    ## Task:
                    Title: {title}
                    Required Skills: {skills}
                    Priority: {priority}

                    ## Available Employees:
                    """
    for e in employees:
        prompt += f"- {e['name']} [ID: {e['id']}] (skills: {', '.join(e['skills'])}, workload: {e['workload']})\n"
   
    prompt += """
                    ## Your Rules for Selection:
                    1. Only consider employees who match **all required skills** (case-insensitive exact match).
                    2. - If multiple employees match all required skills, compare their workload:
                            - If one has a strictly lower workload, choose them.
                            - If multiple have equal workload, break the tie alphabetically based on their names (already sorted above).
                             - Never say one workload is lower than another if they are equal — instead, clearly state they are equal.
                    3. Always explain your decision based on the above rules — don't invent or assume anything not listed.

                    ## Output format:
                    AI Recommendation:

                    The best candidate for this task is <Name> [ID: <id>].

                    1. Skill Match: Explain who matched and why.
                    2. Workload: Compare workloads if needed.
                    3. Tie-breaker: Only apply if multiple candidates have the same skills AND same workload. Otherwise, skip this section.

                    **Use precise and logical reasoning. Do not repeat the task input. Do not make up reasons.**
                    """



    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral", "prompt": prompt},
            stream=True
        )
        result_text = ""
        for line in response.iter_lines():
            if line:
                try:
                    parsed = json.loads(line)
                    chunk = parsed.get("response", "")
                    result_text += chunk
                except json.JSONDecodeError:
                    print("❌ Failed to parse line:", line)

        result_text = result_text.replace("AI Recommendation:", "").strip()

        match = re.search(r"The best candidate for this task is (.+?) \[ID: (\d+)\]", result_text)
        if match:
            selected_id = int(match.group(2))
            assign_and_increment(title, skills, priority, selected_id, True)
        else:
            assign_and_increment(title, skills, priority, None, True)

        return jsonify({"recommendation": result_text})

    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500



@app.route('/assign-rule-based', methods=['POST'])
def assign_task_rule_based():
    data = request.get_json()
    title = data.get('title', '')
    skills = data.get('skills', '')
    priority = data.get('priority', '')
    required_skills = [s.strip().lower() for s in skills.split(",")]

    employees = load_employees()

    best_employee = None
    best_score = float('-inf')
    match_count = 0

    for e in employees:
        matches = sum(1 for skill in e['skills'] if skill in required_skills)
        score = matches - e['workload']
        print(f"Employee: {e['name']} | Skills: {e['skills']} | Matches: {matches} | Score: {score}")
        
        if matches > 0 and score > best_score and e['workload'] <= 10:
            print(f"-> {e['name']} is currently the best match with score {score}")
            best_score = score
            best_employee = e
            match_count = matches

    print(f"Final best employee: {best_employee['name'] if best_employee else 'None'} | Match count: {match_count}")

    if best_employee and match_count > 0:
        assign_and_increment(title, skills, priority, best_employee['id'], False)
        return jsonify({
            "recommendation": f"{best_employee['name']} is selected based on rule-based logic. "
                              f"Skills matched: {match_count}, New workload: {best_employee['workload'] + 1}."
        })
    else:
        return jsonify({
            "recommendation": "No suitable employee found with matching skills and acceptable workload."
        })

@app.route('/')
def home():
    return "✅ Flask backend is running on Docker!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

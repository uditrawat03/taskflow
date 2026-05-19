
import datetime

# Bug 1
def greet_user(name):
    message = f"Hello {name}! Welcome to TaskFlow AI."
    print(message)

greet_user("Udit")


# Bug 2
def calculate_completion(done_count, total_count):
    if total_count == 0:
        return 0
    return (done_count / total_count) * 100

tasks_done  = 3
tasks_total = 0
rate = calculate_completion(tasks_done, tasks_total)
print(f"Completion rate: {rate}%")


# Bug 3
task_titles = ["Review PR", "Buy groceries", "Write tests"]
print(f"First task: {task_titles[0]}")
print(f"Last task: {task_titles[2]}")


# Bug 4
user_age = int(input("Enter your age: "))
years_to_retirement = 60 - user_age
print(f"Years until retirement: {years_to_retirement}")


# Bug 5
def get_high_priority(task_list):
    high = []
    for task in task_list:
        if task["priority"] == "high":
            high.append(task)
    return high

sample_tasks = [
    {"title": "Deploy app",   "priority": "high"},
    {"title": "Buy groceries","priority": "low"},
]
print(get_high_priority(sample_tasks))


# Bug 6
def show_task_count(tasks):
    count = len(tasks)
    if count == 0:
        print("No tasks")
    else:
        print(f"{count} tasks")

show_task_count(sample_tasks)


# Bug 7
config = {
    "theme": "dark",
    "notifications": True,
    "language": "en"
}
print(f"Language setting: {config['language']}")


# Bug 8
def format_date(dt):
    return dt.strftime("%d %B %Y")

today = datetime.date.today()
result = format_date(today)   # passing date object
print(result)
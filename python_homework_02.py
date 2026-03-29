# =========================
# 任务 0：导入模块
# =========================
print("---------- 任务 0 开始 ----------")

import os
import random
import time

print("模块导入完成")

print("---------- 任务 0 完成 ----------")


# =========================
# 任务 1：定义 Student 类
# =========================
print("---------- 任务 1 开始 ----------")

class Student:
    def __init__(self, student_id, name, gender, class_name, college):
        self.student_id = student_id
        self.name = name
        self.gender = gender
        self.class_name = class_name
        self.college = college

    def __str__(self):
        return f"学号:{self.student_id} 姓名:{self.name} 性别:{self.gender} 班级:{self.class_name} 学院:{self.college}"

print("Student 类定义完成")

print("---------- 任务 1 完成 ----------")


# =========================
# 任务 2：定义 ExamSystem 类
# =========================
print("---------- 任务 2 开始 ----------")

class ExamSystem:
    def __init__(self, file_path):
        self.file_path = file_path
        self.students = []
        self.load_students()

    def load_students(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

                for i, line in enumerate(lines):
                    if i == 0:
                        continue

                    parts = line.strip().split()

                    if len(parts) != 6:
                        continue

                    _, name, gender, class_name, student_id, college = parts

                    stu = Student(student_id, name, gender, class_name, college)
                    self.students.append(stu)

            print(f"成功加载 {len(self.students)} 名学生")

            # 防空数据
            if len(self.students) == 0:
                print("警告：未读取到任何学生数据，请检查文件格式！")

        except FileNotFoundError:
            print("错误：文件未找到！")

    def find_student(self, student_id):
        for stu in self.students:
            if stu.student_id == student_id:
                return stu
        return None

    def random_select(self, num):
        try:
            num = int(num)

            if num <= 0:
                print("错误：人数必须大于0！")
                return

            if num > len(self.students):
                print("错误：人数超过总人数！")
                return

            # 核心逻辑
            selected = random.sample(self.students, num)
            # 从学生列表中随机抽取num个不重复的学生

            print("随机点名结果：")
            for stu in selected:
                print(stu)
                # 调用__str__方法输出学生信息

        except ValueError:
            print("错误：请输入数字！")

    def generate_exam_arrangement(self):
        shuffled = self.students[:]
        random.shuffle(shuffled)

        current_time = time.strftime("%Y-%m-%d %H:%M:%S")

        try:
            with open("考场安排表.txt", "w", encoding="utf-8") as f:
                f.write(f"生成时间：{current_time}\n")

                for i, stu in enumerate(shuffled, start=1):
                    f.write(f"{i} {stu.name} {stu.student_id}\n")

            print("考场安排表生成完成")

        except Exception as e:
            print("写入考场安排表失败：", e)

        return shuffled

    def generate_admission_tickets(self, shuffled):
        folder = "准考证"

        try:
            if not os.path.exists(folder):
                os.mkdir(folder)

            for i, stu in enumerate(shuffled, start=1):
                filename = os.path.join(folder, f"{str(i).zfill(2)}.txt")

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"座位号：{i}\n")
                    f.write(f"姓名：{stu.name}\n")
                    f.write(f"学号：{stu.student_id}\n")

            print("准考证生成完成")

        except Exception as e:
            print("生成准考证失败：", e)

    @staticmethod
    def validate_student_id(sid):
        return sid.isdigit()

print("ExamSystem 类定义完成")

print("---------- 任务 2 完成 ----------")


# =========================
# 任务 3：系统初始化
# =========================
print("---------- 任务 3 开始 ----------")

system = ExamSystem("人工智能编程语言学生名单.txt")

print("系统初始化完成")

print("---------- 任务 3 完成 ----------")


# =========================
# 任务 4-7：改成菜单
# =========================
print("---------- 系统运行开始 ----------")

while True:
    print("\n===== 功能菜单 =====")
    print("1. 查找学生")
    print("2. 随机点名")
    print("3. 生成考场安排+准考证")
    print("4. 退出")

    choice = input("请选择：")

    if choice == "1":
        sid = input("请输入学号：")

        if ExamSystem.validate_student_id(sid):
            stu = system.find_student(sid)
            print(stu if stu else "未找到该学生")
        else:
            print("学号格式错误")

    elif choice == "2":
        num = input("请输入点名人数：")
        system.random_select(num)

    elif choice == "3":
        shuffled = system.generate_exam_arrangement()
        system.generate_admission_tickets(shuffled)

    elif choice == "4":
        print("系统退出")
        break

    else:
        print("输入无效，请重新输入")
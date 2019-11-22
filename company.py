from random import randint


class Manager:

    def __init__(self):
        self.departments = {}
        self.projects = []

    def add_departments(self, departments):
        self.departments.update(**departments)

    def add_projects(self, projects):
        self.projects.extend(projects)

    def hire_employees(self):
        num = 0
        for project in self.projects:
            hired_num = self.departments[project.p_type].add_employees(project.complicity)
            num += hired_num
        return num


class Department:

    def __init__(self, manager, employees=None):
        self.employees = {
            'free': employees or [],
            'busy': []
        }
        self.manager = manager

    def add_employees(self, complicity):
        raise NotImplementedError

    def appoint_employees(self, project):
        raise NotImplementedError

    def print_busy_info(self):
        print(f'Свободные: {self.employees["free"]}')
        print(f'Занятые: {self.employees["busy"]}')

    @staticmethod
    def print_appoint_info(employee, project):
        print(f'Сотрудник {employee}/{employee.department.name} назначен на проект {project}')


class MobDepartment(Department):

    name = 'mob'

    def add_employees(self, complicity):
        employees = [Employee(self) for _ in range(complicity)]
        self.employees['free'].extend(employees)
        print(f'В департамент MOB наняты сотрудники: {employees}')
        return len(employees)

    def appoint_employees(self, project):
        if project.complicity > len(self.employees['free']):
            return False

        for i in range(project.complicity):
            employee = self.employees['free'].pop(0)
            employee.add_project(project)
            self.employees['busy'].append(employee)
            self.print_appoint_info(employee, project)
        return True


class WebDepartment(Department):

    name = 'web'

    def add_employees(self, complicity):
        employees = [Employee(self)]
        self.employees['free'].extend(employees)
        print(f'В департамент MOB наняты сотрудники: {employees}')
        return len(employees)

    def appoint_employees(self, project):
        if len(self.employees['free']) < 1:
            return False

        employee = self.employees['free'].pop(0)
        employee.add_project(project)
        self.employees['busy'].append(employee)
        self.print_appoint_info(employee, project)
        return True


class QaDepartment(Department):

    name = 'qa'

    def add_employees(self, complicity):
        employees = [QaEmployee(self)]
        self.employees['free'].extend(employees)
        print(f'В департамент QA наняты сотрудники: {employees}')
        return len(employees)

    def appoint_employees(self, project):
        if len(self.employees['free']) < 1:
            return False

        employee = self.employees['free'].pop(0)
        employee.add_project(project)
        self.employees['busy'].append(employee)
        self.print_appoint_info(employee, project)
        return True


class Employee:

    def __init__(self, department):
        self.department = department
        self.projects = []
        self.days_counter = 0

    def __lt__(self, other):
        return len(self.projects) < len(self.projects)

    def add_project(self, project):
        self.days_counter = 0
        self.projects.append(project)

    def do_daily_work(self):
        ready = False
        if self.is_busy:
            ready = self._check_readiness()
        if not ready:
            self.days_counter += 1

    def _check_readiness(self):
        if len(self.projects) > 0:
            current_project = self.projects[-1]
            if current_project.complicity == self.days_counter:
                current_project.status = 1
                self.days_counter = 0
                self.department.employees['busy'].remove(self)
                self.department.employees['free'].append(self)
                self.send_to_testing(current_project)
                return True
        return False

    def send_to_testing(self, project):
        project.p_type = 'qa'
        manager = self.department.manager
        manager.add_projects([project])

    @property
    def is_busy(self):
        if len(self.projects) > 0:
            current_project = self.projects[-1]
            if current_project.status == 0:
                return True
        return False

    def check_dismissal(self):
        if self.days_counter > 3:
            return True
        return False

    def dismiss(self):
        self.department.employees['free'].remove(self)
        print(f'Уволен сотрудник {self}. xxxxxxxxxxxxxxxxxx')


class QaEmployee(Employee):

    def do_daily_work(self):
        ready = False
        if self.is_busy:
            ready = self._check_readiness()
        if not ready:
            self.days_counter += 1
        return ready

    @property
    def is_busy(self):
        if len(self.projects) > 0:
            current_project = self.projects[-1]
            if current_project.status == 1:
                return True
        return False

    def _check_readiness(self):
        if len(self.projects) > 0:
            current_project = self.projects[-1]
            if self.days_counter >= 1:
                current_project.status = 2
                self.days_counter = 0
                self.department.employees['busy'].remove(self)
                self.department.employees['free'].append(self)
                return True
        return False


class Project:
    STATUS = {
        0: 'In progress',
        1: 'Completed',
        2: 'Tested',
    }

    def __init__(self, p_type, complicity):
        self.p_type = p_type
        self.complicity = complicity
        self.status = 0


def create_company():
    manager = Manager()
    departments = {
        'web': WebDepartment(manager),
        'mob': MobDepartment(manager),
        'qa': QaDepartment(manager)
    }
    manager.add_departments(departments)
    return manager


def generate_projects():
    num = randint(0, 4)
    p_type = ['mob', 'web'][randint(0, 1)]
    projects = [Project(p_type, randint(1, 3)) for _ in range(num)]
    for project in projects:
        print(f'Добавлен проект {project} сложности {project.complicity} для департамента {project.p_type}')
    return projects


def main_process(days_num):
    manager = create_company()
    departments = manager.departments

    # main loop
    completed_projects_num = 0
    hired_number = 0
    dismissed_number = 0
    for day in range(days_num):
        day += 1
        print(f'День № {day}:')

        # hire employees for rest of projects
        day_hired_number = manager.hire_employees()
        hired_number += day_hired_number

        # new daily projects for manager
        manager.add_projects(generate_projects())

        # appoint projects to employees
        projects_to_delegate = []
        for project in manager.projects:
            appointed = departments[project.p_type].appoint_employees(project)
            if appointed:
                projects_to_delegate.append(project)
        for p in projects_to_delegate:
            manager.projects.remove(p)

        # do work
        dismissal_candidates = []
        for name, department in departments.items():
            for employee in department.employees['busy']:
                completed = employee.do_daily_work()
                if completed:
                    completed_projects_num += 1

            for employee in department.employees['free']:
                employee.do_daily_work()
                dismiss = employee.check_dismissal()
                if dismiss:
                    dismissal_candidates.append(employee)
            print('\n','---------------------', name, '---------------------')
            department.print_busy_info()
        print('\n')

        if dismissal_candidates:
            worst_employee = sorted(dismissal_candidates)[0]
            worst_employee.dismiss()
            dismissed_number += 1

        print(f'Конец дня № {day}----------------------------\n'
              f'---------------------------------------------\n')
    print(f'projects completed = {completed_projects_num}\n'
          f'hired = {hired_number}\n'
          f'dismissed = {dismissed_number}')


main_process(10)

from random import randint


class Manager:

    def __init__(self):
        self.departments = {}
        self.projects = []
        self.dismissed_number = 0
        self.hired_number = 0
        self.completed_projects_number = 0

    def add_departments(self, departments):
        self.departments.update(**departments)

    def add_projects(self, projects):
        self.projects.extend(projects)

    def appoint(self):
        projects_to_delegate = []
        for project in self.projects:
            appointed = self.departments[project.p_type].appoint_employees(project)
            if appointed:
                projects_to_delegate.append(project)
        for p in projects_to_delegate:
            self.projects.remove(p)

    def hire_employees(self):
        num = 0
        for project in self.projects:
            hired_num = self.departments[project.p_type].add_employees(project.complicity)
            num += hired_num
        self.hired_number += num

    def start_departments_daily_work(self):
        company_dismissal_candidates = []
        for dep_name, department in self.departments.items():
            department_dismissal_candidates = department.start_employees_daily_work(dep_name)
            company_dismissal_candidates.extend(department_dismissal_candidates)

        if company_dismissal_candidates:
            worst_employee = sorted(company_dismissal_candidates)[0]
            worst_employee.dismiss()
            self.dismissed_number += 1

    def record_completed_project(self):
        self.completed_projects_number += 1


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

    def start_employees_daily_work(self, dep_name):
        """
        Starts the work of employees (busy then free)
        :param dep_name: name of department
        :return: dismissal_candidates -> list
        """
        dismissal_candidates = []
        for employee in self.employees['busy']:
            ready = employee.do_daily_work()
            if ready:
                self.record_completed_project()

        for employee in self.employees['free']:
            employee.do_daily_work()
            dismiss = employee.check_dismissal()
            if dismiss:
                dismissal_candidates.append(employee)
        print('\n', '---------------------', dep_name, '---------------------')
        self.print_busy_info()
        print('\n')
        return dismissal_candidates

    def record_completed_project(self):
        self.manager.record_completed_project()


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

    READY_STATUS = 1

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
        self.days_counter += 1
        if self.is_busy:
            self._check_readiness()

    def _check_readiness(self):
        if len(self.projects) > 0:
            current_project = self.projects[-1]
            if current_project.complicity == self.days_counter:
                current_project.status = self.READY_STATUS
                self.days_counter = -1  # because days_counter works for busy than free employees
                self.department.employees['busy'].remove(self)
                self.department.employees['free'].append(self)
                if self.READY_STATUS == 1:
                    self.send_to_testing(current_project)
                if self.READY_STATUS == 2:
                    return True

    def send_to_testing(self, project):
        project.p_type = 'qa'
        manager = self.department.manager
        manager.add_projects([project])

    @property
    def is_busy(self):
        if self in self.department.employees['busy']:
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
    READY_STATUS = 2

    def do_daily_work(self):
        """
        Do QA employee daily work and returns True if project completed
        :return:
        """
        self.days_counter += 1
        if self.is_busy:
            ready = self._check_readiness()
            return ready


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


def create_company_manager():
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
    manager = create_company_manager()

    # main loop
    for day in range(days_num):
        day += 1
        print(f'День № {day}:')

        # hire employees for rest of projects
        manager.hire_employees()

        # new daily projects for manager
        manager.add_projects(generate_projects())

        # appoint employees to projects
        manager.appoint()

        # do work
        manager.start_departments_daily_work()

        print(f'Конец дня № {day}----------------------------\n'
              f'---------------------------------------------\n')
    print(f'projects completed = {manager.completed_projects_number}\n'
          f'hired = {manager.hired_number}\n'
          f'dismissed = {manager.dismissed_number}')


main_process(10)

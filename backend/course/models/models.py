from django.db import models
from django.contrib.postgres.fields import JSONField


# Create your models here.
class Department(models.Model):
    # sigaa_id = models.PositiveSmallIntegerField(null=True)
    name = models.CharField(max_length=100)
    initials = models.CharField(max_length=4)

    def __str__(self):
        return self.name

    def courses_list(self):
        return [course.to_json() for course in self.courses.all()]

    def subjects_list(self):
        return [subject.to_json() for subject in self.subject.all().order_by("name")]


# Classe que armazena as disciplinas
class Subject(models.Model):
    id = models.PositiveSmallIntegerField(null=True)
    code = models.CharField(max_length=20, primary_key=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="subject", null=True
    )
    name = models.CharField(max_length=80)
    credit = models.SmallIntegerField()

    # Campos pré-processados
    equivalences = JSONField(blank=True, null=True)
    prerequisites = JSONField(blank=True, null=True)
    corequisites = JSONField(blank=True, null=True)
    offer = JSONField(blank=True, null=True)

    def __str__(self):
        return self.name

    def department_name(self):
        if self.department:
            return self.department.name
        else:
            return "Departamento ou Unidade não encotrada"

    def to_json(self):
        return {"code": self.code, "subject_name": self.name, "credit": self.credit}

    def get_equivalences(self):
        """Retorna as equivalências em JSON"""
        equivalences = []
        for equivalence in self.subject_eq.all():
            equivalences.append(equivalence.to_json())
        return equivalences

    def get_offer(self, semester=""):
        if semester == "":
            return [offer.to_json() for offer in self.offers.all()]
        else:
            return [offer.to_json() for offer in self.offers.filter(semester=semester)]

    def get_corequisite(self):
        return [subject.to_json() for subject in self.corequisite.all()]

    def get_prerequisites(self):
        """Retorna os pré-requisitos em JSON"""
        prerequisites = []
        for prerequisite_set in self.prerequisite_set.all():
            prerequisites_set_list = []
            for prerequisite in prerequisite_set.prerequisite.all():
                prerequisites_set_list.append(prerequisite.subject.to_json())
            prerequisites.append(prerequisites_set_list)
        return prerequisites

    # Semester no formato exemplo: 2022.2
    def preprocess_info(self, semester=""):
        self.prerequisites = self.get_prerequisites()
        self.equivalences = self.get_equivalences()
        self.corequisites = self.get_corequisite()
        self.offer = self.get_offer(semester)
        self.save()


# Classe que armazena o curso
class Course(models.Model):
    SHIFT = (
        ("N", "Noturno"),
        ("D", "Diurno"),
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="courses"
    )
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    coordinator_name = models.CharField(max_length=100, null=True)
    academic_degree = models.CharField(max_length=100)
    is_ead = models.BooleanField(default=False)
    shift = models.CharField(max_length=2, choices=SHIFT)

    def __str__(self):
        return self.name

    def get_curriculums(self):  # TODO
        return

    def details(self):
        """Retorna as informações detalhadas do curso, no formato padronizado pelo front"""
        return {
            "academic_degree": self.academic_degree,
            "shift": self.shift,
            "coordinator_name": self.coordinator_name,
        }

    def to_json(self):
        return {
            "code": self.code,
            "name": self.name,
            "shift": self.get_shift_display(),
            "academic_degree": self.academic_degree,
        }


class CourseCurriculum(models.Model):
    id = models.BigIntegerField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course")
    code = models.CharField(max_length=6, null=True)
    start_semester = models.CharField(max_length=6, null=True)

    total_workload = models.PositiveIntegerField(null=True)
    optional_workload = models.PositiveIntegerField(null=True)
    mandatory_workload = models.PositiveIntegerField(null=True)

    max_total_free_module = models.PositiveIntegerField(null=True)
    max_period_workload = models.PositiveIntegerField(null=True)
    min_period_workload = models.PositiveIntegerField(null=True)

    # Campos calculados
    flow = JSONField(null=True, blank=True)
    num_semester = models.SmallIntegerField(null=True, blank=True)

    def append_subject(self, semester, subject, status):
        curriculum_subject = CurriculumSubject(
            curriculum=self, subject=subject, semester=semester, status=status
        )
        curriculum_subject.save()

    def __str__(self):
        return self.name

    def get_flow(self):  # TODO
        return

    def get_num_semester(self):
        """Retorna o número de semestres do curso baseado no fluxo"""
        return len(self.flow)

    def details(self):
        """Retorna as informações detalhadas do curso, no formato padronizado pelo front"""
        return {
            "workload": {
                "total": self.total_workload,
                "optional": self.opt_workload,
                "mandatory": self.mandatory_workload,
                "min": self.min_period_workload,
                "max": self.max_period_workload,
                "max_ML": self.max_total_free_module,
            },
            "num_semester": self.num_semester,
        }

    def preprocess_info(self):
        """Realiza o pré-processamento das informações do curso"""
        self.flow = self.get_flow()
        self.curriculum = {
            "optional": self.get_curriculum(),
            # Coleta as disciplinas obrigatórias do fluxo do curso
            "mandatory": [
                course_subject.to_json()
                for course_subject in self.course_subject.filter(status="OBR").order_by(
                    "semester"
                )
            ],
        }
        self.num_semester = self.get_num_semester()
        self.save()

    def to_json(self):
        return {
            "code": self.code,
            "num_semester": self.num_semester,
        }


# Classe que armazena as disciplinas do curso com o semestre
class CurriculumSubject(models.Model):
    STATUS = (
        ("OBR", "OBRIGATÓRIA"),
        ("OPT", "OPTATIVA"),
        ("ML", "MÓDULO LIVRE"),
    )
    curriculum = models.ForeignKey(
        CourseCurriculum, on_delete=models.CASCADE, related_name="curriculum_subject"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="curriculum_subject"
    )
    semester = models.PositiveSmallIntegerField(null=True)
    status = models.CharField(max_length=3, choices=STATUS)

    def subject_name(self):
        return self.subject.name

    def to_json(self):
        return {
            "semester": self.semester,
            "status": self.status,
            "subject": self.subject,
            "curriculum": self.curriculum,
        }


class PreRequisiteSet(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="prerequisite_set"
    )


# Classe que armazena um pré-requisito em um conjunto de requisito
class PreRequisite(models.Model):
    prerequisite_set = models.ForeignKey(
        PreRequisiteSet, on_delete=models.CASCADE, related_name="prerequisite"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="prerequisite"
    )


class CoRequisite(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="corequisite"
    )
    corequisite = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="subject_co"
    )

    def to_json(self):
        return self.corequisite.to_json()


class Equivalence(models.Model):
    coverage = models.CharField(max_length=10)
    destination = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="destination_eq"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="subject_eq"
    )
    direction = models.CharField(max_length=14)

    def to_json(self):
        return {
            "coverage": self.coverage,
            "direction": self.direction,
            "destination": self.destination.to_json(),
            "subject": self.subject.to_json(),
            "options": [op.to_json() for op in self.options.all()],
        }


# Classe que armazena um curso e a qual equivalência ele se refere
class Option(models.Model):
    curriculum = models.ForeignKey(
        CourseCurriculum, on_delete=models.CASCADE, related_name="subject_option"
    )
    equivalence = models.ForeignKey(
        Equivalence, on_delete=models.CASCADE, related_name="options"
    )

    def to_json(self):
        return {"code": self.course.id, "name": self.course.name}


class Offer(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="offers"
    )
    name = models.CharField(max_length=100)
    semester = models.CharField(max_length=7)
    schedule = models.CharField(max_length=100)
    students_qtd = models.CharField(max_length=3)
    occupied = models.CharField(max_length=3, default="0")
    place = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)

    def to_json(self):
        return {
            "name": self.name,
            "semester": self.semester,
            "teachers": [ot.teacher.name for ot in self.offer_teachers.all()],
            "total_vacancies": self.students_qtd,
            "occupied_vacancies": self.occupied,
            "updated_at": self.updated_at.strftime("%m/%d/%Y - %H:%M:%S"),
            "schedule": self.schedule.split(" "),
            "place": self.place,
        }


class Teacher(models.Model):
    name = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.name


class OfferTeacher(models.Model):
    offer = models.ForeignKey(
        Offer, on_delete=models.CASCADE, related_name="offer_teachers"
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="offer_teachers"
    )

    # Import feito depois para não dar conflito com referência cruzada (TODO Alterar esse funcionamento)


# from course.scripts.graph_flow_course import do_graph

from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import TeacherSerializer, CategorySerializer, CourseSerializer, ChapterSerializer, StudentSerializer, StudentCourseEnrollSerializer, CourseRatingSerializer, TeacherDashboardSerializer, StudentFavoriteCourseSerializer, StudentAssignmentSerializer, StudentDashboardSerializer, NotificationSerializer, QuizSerializer, QuizQuestionSerializer, CourseQuizSerializer, AttemptQuizSerializer, StudyMaterialSerializer, FAQSSerializer, ContactSerializer
from . import models
from rest_framework.response import Response
from rest_framework import permissions#restricts who can access the api
from rest_framework import generics#combines all the actions into one ie: post,delete etc
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,HttpResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.core.mail import send_mail




# Create your views here.

#pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 8
#class based views
#provide list of teachers
class TeacherList(generics.ListCreateAPIView):
    queryset = models.Teacher.objects.all()
    serializer_class = TeacherSerializer

    def get_queryset(self):
        if 'popular' in self.request.GET:
            sql='SELECT *,COUNT(c.id) as total_course FROM main_teacher as t INNER JOIN main_course as c ON c.teacher_id=t.id GROUP BY t.id ORDER BY total_course desc'
            return models.Teacher.objects.raw(sql)

class TeacherDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Teacher.objects.all()
    serializer_class = TeacherSerializer
    
@csrf_exempt
def teacher_login(request):
    email=request.POST['email']
    password=request.POST['password']
    try:
        teacherData = models.Teacher.objects.get(email=email, password=password)
    except models.Teacher.DoesNotExist:
        teacherData = None
    if teacherData:
        return JsonResponse({'bool': True,'teacher_id':teacherData.id})
    else:
        return JsonResponse({'bool': False})

class CategoryList(generics.ListCreateAPIView):
    queryset = models.CourseCategory.objects.all()
    serializer_class = CategorySerializer



#handles post and get requests
class CourseList(generics.ListCreateAPIView):
    queryset = models.Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        if 'result' in self.request.GET:
            limit = int(self.request.GET['result'])
            qs=models.Course.objects.all().order_by('-id')[:limit]

        if 'category' in self.request.GET:
            category = self.request.GET['category']
            category = models.CourseCategory.objects.filter(id=category).first()
            qs = models.Course.objects.filter(category =category)
        
        if 'skill_name' in self.request.GET and 'teacher' in self.request.GET:
            skill_name = self.request.GET['skill_name']
            teacher  = self.request.GET['teacher']
            teacher = models.Teacher.objects.filter(id=teacher).first()
            qs = models.Course.objects.filter(techs__icontains=skill_name,teacher=teacher)

        if 'searchString' in self.kwargs:
            search = self.kwargs['searchString']
            if search:
                qs = models.Course.objects.filter(Q(techs__icontains=search)|Q(title__icontains=search))
            
        elif 'studentId' in self.kwargs:
            student_id = self.kwargs['studentId']
            student =models.Student.objects.get(pk=student_id)
            queries = [Q(techs__iendswith=value) for value in student.interested_categories]
            qs=models.Course.objects.filter(techs__icontains=student.interested_categories)
            query = queries.pop()
            for item in queries:
                query |= item
            qs = models.Course.objects.filter(query)
            return qs

        return qs
            

#specific teacher course
class TeacherCourseList(generics.ListCreateAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher=models.Teacher.objects.get(pk=teacher_id)
        return models.Course.objects.filter(teacher=teacher)

#specific teacher course
class TeacherCourseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Course.objects.all()
    serializer_class = CourseSerializer


#handles post and get requests
class ChapterList(generics.ListCreateAPIView):
    queryset = models.Chapter.objects.all()
    serializer_class = ChapterSerializer

class CourseDetailView(generics.RetrieveAPIView):
    queryset = models.Course.objects.all()
    serializer_class = CourseSerializer

    
#retuning only chapter list 
class CourseChapterList(generics.ListAPIView):
    serializer_class = ChapterSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course=models.Course.objects.get(pk=course_id)
        return models.Chapter.objects.filter(course=course)

#retuning only chapter list 
class ChapterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Chapter.objects.all()
    serializer_class = ChapterSerializer

    # def get_serializer_context(self):
    #     context = super().get_serializer_context()
    #     context['chapter_duration']=self.chapter_duration
    #     print('context.............')
    #     print(context)
    #     return context

################STUDENT API####################

class StudentList(generics.ListCreateAPIView):
    queryset = models.Student.objects.all()
    serializer_class = StudentSerializer
"""
class StudentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Student.objects.all()
    serializer_class = StudentSerializer
"""


@csrf_exempt
def student_login(request):
    email=request.POST['email']
    password=request.POST['password']
    try:
        studentData = models.Student.objects.get(email=email, password=password)
    except models.Student.DoesNotExist:
        studentData = None
    if studentData:
        return JsonResponse({'bool': True,'student_id':studentData.id})
    else:
        return JsonResponse({'bool': False})

class StudentEnrollCourseList(generics.ListCreateAPIView):
    queryset = models.StudentCourseEnrollment.objects.all()
    serializer_class = StudentCourseEnrollSerializer


def fetch_enroll_status(request,student_id,course_id):
    student=models.Student.objects.filter(id=student_id).first()
    course=models.Course.objects.filter(id=course_id).first()
    enrollStatus=models.StudentCourseEnrollment.objects.filter(course=course, student=student).count()
    if enrollStatus:
        return JsonResponse({'bool': True})
    else:
        return JsonResponse({'bool': False})

class EnrolledStudentList(generics.ListAPIView):
    queryset = models.StudentCourseEnrollment.objects.all()
    serializer_class = StudentCourseEnrollSerializer

    def get_queryset(self):
        if 'course_id' in self.kwargs:
            course_id = self.kwargs['course_id']
            course=models.Course.objects.get(pk=course_id)
            return models.StudentCourseEnrollment.objects.filter(course=course)
        elif 'teacher_id' in self.kwargs:
            teacher_id = self.kwargs['teacher_id']
            teacher =models.Teacher.objects.get(pk=teacher_id)
            return models.StudentCourseEnrollment.objects.filter(course__teacher=teacher).distinct()
        elif 'student_id' in self.kwargs:
            student_id = self.kwargs['student_id']
            student =models.Student.objects.get(pk=student_id)
            return models.StudentCourseEnrollment.objects.filter(student=student).distinct()
        


class CourseRatingList(generics.ListCreateAPIView):
    queryset = models.CourseRating.objects.all()
    serializer_class =  CourseRatingSerializer

    def get_queryset(self):
        if 'popular' in self.request.GET:
            sql='SELECT *,AVG(cr.rating) as avg_rating FROM main_courserating as cr INNER JOIN main_course as c on cr.course_id=c.id GROUP BY c.id ORDER BY avg_rating desc LIMIT 4'
            return models.CourseRating.objects.raw(sql)
        if 'all' in self.request.GET:
            sql='SELECT *,AVG(cr.rating) as avg_rating FROM main_courserating as cr INNER JOIN main_course as c on cr.course_id=c.id GROUP BY c.id ORDER BY avg_rating desc'
            return models.CourseRating.objects.raw(sql)
   
def fetch_rating_status(request,student_id,course_id):
        student=models.Student.objects.filter(id=student_id).first()
        course=models.Course.objects.filter(id=course_id).first()
        ratingStatus=models.CourseRating.objects.filter(course=course, student=student).count()
        if ratingStatus:
            return JsonResponse({'bool': True})
        else:
            return JsonResponse({'bool': False})

class TeacherDashboard(generics.RetrieveAPIView):
    queryset = models.Teacher.objects.all()
    serializer_class = TeacherDashboardSerializer

class StudentFavoriteCourseList(generics.ListCreateAPIView):
    queryset = models.StudentFavoriteCourse.objects.all()
    serializer_class =  StudentFavoriteCourseSerializer

    def get_queryset(self):
        if 'student_id' in self.kwargs:
            student_id = self.kwargs['student_id']
            student =models.Student.objects.get(pk=student_id)
            return models.StudentFavoriteCourse.objects.filter(student=student).distinct()



def fetch_favorite_status(request, student_id, course_id):
    student = models.Student.objects.filter(id=student_id).first()
    course = models.Course.objects.filter(id=course_id).first()
    favoriteStatus = models.StudentFavoriteCourse.objects.filter(course=course, student=student).first()
    if favoriteStatus and favoriteStatus.status == True:
        return JsonResponse({'bool': True})
    else:
        return JsonResponse({'bool': False})

def remove_favorite_course(request, course_id, student_id):
    student = models.Student.objects.filter(id=student_id).first()
    course = models.Course.objects.filter(id=course_id).first()
    favoriteStatus = models.StudentFavoriteCourse.objects.filter(course=course, student=student).delete()
    if favoriteStatus:
        return JsonResponse({'bool': True})
    else:
        return JsonResponse({'bool': False})

class AssignmentList(generics.ListCreateAPIView):
    queryset = models.StudentAssignment.objects.all()
    serializer_class = StudentAssignmentSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        teacher_id = self.kwargs['teacher_id']
        student=models.Student.objects.get(pk=student_id)
        teacher=models.Teacher.objects.get(pk=teacher_id)
        return models.StudentAssignment.objects.filter(student=student, teacher=teacher)

class MyAssignmentList(generics.ListCreateAPIView):
    queryset = models.StudentAssignment.objects.all()
    serializer_class = StudentAssignmentSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        student=models.Student.objects.get(pk=student_id)
        #update notifications
        models.Notification.objects.filter(student=student, notif_for='student',notif_subject='assignment').update(notif_read_status=True)
        return models.StudentAssignment.objects.filter(student=student)

class UpdateAssignment(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.StudentAssignment.objects.all()
    serializer_class = StudentAssignmentSerializer

class StudentDashboard(generics.RetrieveAPIView):
    queryset = models.Student.objects.all()
    serializer_class = StudentDashboardSerializer

class StudentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Student.objects.all()
    serializer_class = StudentSerializer


@csrf_exempt
def teacher_change_password(request, teacher_id):
    password=request.POST['password']
    try:
        teacherData = models.Teacher.objects.get(id=teacher_id)
    except models.Teacher.DoesNotExist:
        teacherData = None
    if teacherData:
        models.Teacher.objects.filter(id=teacher_id).update(password=password)
        return JsonResponse({'bool': True})
    else:
        return JsonResponse({'bool': False})


@csrf_exempt
def student_change_password(request, student_id):
    password=request.POST['password']
    try:
        studentData = models.Student.objects.get(id=student_id)
    except models.Student.DoesNotExist:
        studentData = None
    if studentData:
        models.Student.objects.filter(id=student_id).update(password=password)
        return JsonResponse({'bool': True})
    else:
        return JsonResponse({'bool': False})

class NotificationList(generics.ListCreateAPIView):
    queryset = models.Notification.objects.all()
    serializer_class =  NotificationSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        student=models.Student.objects.get(pk=student_id)
        return models.Notification.objects.filter(student=student, notif_for='student',notif_subject='assignment',notif_read_status=False)

class QuizList(generics.ListCreateAPIView):
    queryset = models.Quiz.objects.all()
    serializer_class = QuizSerializer
#specific teacher quiz
class TeacherQuizList(generics.ListCreateAPIView):
    serializer_class = QuizSerializer

    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher=models.Teacher.objects.get(pk=teacher_id)
        return models.Quiz.objects.filter(teacher=teacher)

#specific teacher quiz
class TeacherQuizDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Quiz.objects.all()
    serializer_class = QuizSerializer

#retuning only quiz list 
class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Quiz.objects.all()
    serializer_class = QuizSerializer

class QuizQuestionList(generics.ListCreateAPIView):
    serializer_class = QuizQuestionSerializer

    def get_queryset(self):
        quiz_id = self.kwargs['quiz_id']
        quiz=models.Quiz.objects.get(pk=quiz_id)
        if 'limit' in self.kwargs:
           return models.QuizQuestions.objects.filter(quiz=quiz).order_by('id')[:1]
           ###for next question
        elif 'question_id' in self.kwargs:
            current_question = self.kwargs['question_id']
            return models.QuizQuestions.objects.filter(quiz=quiz,id__gt=current_question).order_by('id')[:1]
        else:
            return models.QuizQuestions.objects.filter(quiz=quiz)

class CourseQuizList(generics.ListCreateAPIView):
    queryset = models.CourseQuiz.objects.all()
    serializer_class = CourseQuizSerializer

    def get_queryset(self):
        if 'course_id' in self.kwargs:
            course_id = self.kwargs['course_id']
            course=models.Course.objects.get(pk=course_id)
            return models.CourseQuiz.objects.filter(course=course)

def fetch_quiz_assign_status(request,quiz_id,course_id):
    quiz=models.Quiz.objects.filter(id=quiz_id).first()
    course=models.Course.objects.filter(id=course_id).first()
    assignStatus=models.CourseQuiz.objects.filter(course=course,quiz=quiz).count()
    if assignStatus:
        return JsonResponse({'bool': True})
    else:
        return JsonResponse({'bool': False})


class AttemptQuizList(generics.ListCreateAPIView):
    queryset = models.AttemptQuiz.objects.all()
    serializer_class = AttemptQuizSerializer

    def get_queryset(self):
        if 'quiz_id' in self.kwargs:
            quiz_id = self.kwargs['quiz_id']
            quiz = models.Quiz.objects.get(pk=quiz_id)
            return models.AttemptQuiz.objects.filter(quiz=quiz)
            #raw(f'SELECT * FROM main_attemptquiz WHERE quiz_id={int(quiz_id)}GROUP by student_id')
        else:
            return models.AttemptQuiz.objects.none()


def fetch_quiz_attempt_status(request,quiz_id,student_id):
    quiz=models.Quiz.objects.filter(id=quiz_id).first()
    student=models.Student.objects.filter(id=student_id).first()
    attemptStatus=models.AttemptQuiz.objects.filter(student=student,question__quiz=quiz).count()
    if attemptStatus > 0:
        return JsonResponse({'bool': True})
    else:
        return JsonResponse({'bool': False})

#def fetch_quiz_result(request,quiz_id,student_id):
    #total_questions = models.QuizQuestions.objects.filter(quiz=quiz).count()
    #total_attempted_questions = models.AttemptQuiz.objects.filter(student=student,quiz=quiz).values('student').count()
    #attempted_questions = models.AttemptQuiz.objects.filter(student=student,quiz=quiz)

    #total_correct_answers = 0
    #for attempt in attempted_questions:
        #if attempt.correct_ans == attempt.question.correct_ans:
            #total_correct_answers+=1

    #return JsonResponse({'total_questions':total_questions,'total_attempted_questions':total_attempted_questions,'total_correct_answers':total_correct_answers})

    
#retuning only study material list 
class StudyMaterialList(generics.ListCreateAPIView):
    serializer_class = StudyMaterialSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = models.Course.objects.get(pk=course_id)
        return models.StudyMaterial.objects.filter(course=course)

    def perform_create(self, serializer):
        # Retrieve the course_id from URL parameters
        course_id = self.kwargs['course_id']
        # Retrieve the course instance based on the course_id
        course = models.Course.objects.get(pk=course_id)
        # Set the course_id for the StudyMaterial instance
        serializer.save(course_id=course_id)


class StudyMaterialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.StudyMaterial.objects.all()
    serializer_class =  StudyMaterialSerializer

def update_view(request,course_id):
    queryset=models.Course.objects.filter(pk=course_id).first()
    queryset.course_views+=1
    queryset.save()
    return JsonResponse({'views':queryset.course_views})

class FAQList(generics.ListAPIView):
    queryset = models. FAQS.objects.all()
    serializer_class =   FAQSSerializer


#contact us form
class ContactList(generics.ListCreateAPIView):
    queryset = models.ContactUs.objects.all()
    serializer_class =   ContactSerializer

#teacher forgot password
#@csrf_exempt
#def teacher_forgot_password(request):
 #   email = request.POST.get('email', '')
 #   verify = models.Teacher.objects.filter(email=email).first()
  #  if verify:
   #     link = f'http://localhost:5173/instructor-forgot-password/{verify.id}/'
    #    send_mail(
     #       "Reset Password",
        #    "",  # Empty message since you're using html_message
          #  "simonmulu7@gmail.com",
           # [email],
           # fail_silently=False,
           # html_message=f'<a href="{link}">Click here to reset your password</a>'
        #)
       # return JsonResponse({'bool': True, 'msg': 'Please check your email!'})
    #else:
        #return JsonResponse({'bool': False, 'msg': 'Email not found!'})


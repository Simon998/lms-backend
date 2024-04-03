from django.db import models
from django.core import serializers
from django.core.mail import send_mail


# Create your models here.
#Teacher Model
class Teacher(models.Model):
    full_name=models.CharField(max_length=250)
    detail=models.TextField(null=True)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=250, blank=True,null=True)
    qualification=models.CharField(max_length=250)
    mobile_no=models.CharField(max_length=20)
    skills=models.TextField()
    profile_img = models.ImageField(upload_to='teacher_profile_imgs/', null=True)

    #Modifies the plural in admin dashboard ad sorts alphabetically
    class Meta:
        verbose_name_plural="1. Teachers"
    
    def skill_list(self):
        skill_list = self.skills.split(',')
        return skill_list

    def __str__(self):
        return self.full_name

    #Total courses, chapters and students taught by teacher
    def total_teacher_courses(self):
        total_courses=Course.objects.filter(teacher=self).count()
        return total_courses
    
    def total_teacher_chapters(self):
        total_chapters=Chapter.objects.filter(course__teacher=self).count()
        return total_chapters

    def total_teacher_students(self):
        total_students=StudentCourseEnrollment.objects.filter(course__teacher=self).count()
        return total_students
#Course Category Model
class CourseCategory(models.Model):
    title=models.CharField(max_length=250)
    description=models.TextField()

    #total courses in category
    def total_courses(self):
        total_courses=Course.objects.filter(category=self).count()
        return total_courses

    #Modifies the plural in admin dashboard ad sorts alphabetically
    class Meta:
        verbose_name_plural="2. Course Categories"
    #show the title of the category in admin dashboard
    def __str__(self):
        return self.title

  
#course model
class Course(models.Model):
    category = models.ForeignKey(CourseCategory, on_delete=models.CASCADE, related_name='category_courses')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_courses')
    title = models.CharField(max_length=250)
    description = models.TextField()
    techs = models.TextField(null=True)
    featured_image = models.ImageField(upload_to='coures_imgs/', null=True)
    course_views = models.BigIntegerField(default=0)

    class Meta:
        verbose_name_plural = "3. Courses"

    def related_videos(self):
        related_videos = Course.objects.filter(techs__icontains=self.techs)
        return serializers.serialize('json', related_videos)
    
    def tech_list(self):
        return self.techs.split(',')
        return tech_list

    def total_enrolled_students(self):
        total_enrolled_students=StudentCourseEnrollment.objects.filter(course=self).count()
        return total_enrolled_students

    def course_rating(self):
        course_rating = CourseRating.objects.filter(course=self).aggregate(avg_rating=models.Avg('rating'))
        return course_rating['avg_rating']


    def __str__(self):
        return self.title


#Student Model
class Student(models.Model):
    full_name=models.CharField(max_length=250)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=250, null=True, blank=True)
    username=models.CharField(max_length=250)
    interested_categories=models.TextField()
    profile_img = models.ImageField(upload_to='student_profile_imgs/', null=True)

    def __str__(self):
        return self.full_name

    #Total courses, assignments and fav courses for student
    def enrolled_courses(self):
        enrolled_courses=StudentCourseEnrollment.objects.filter(student=self).count()
        return enrolled_courses
    
    def favorite_courses(self):
        favorite_courses=StudentFavoriteCourse.objects.filter(student=self).count()
        return favorite_courses

    #completed assignments
    def complete_assignments(self):
        complete_assignments=StudentAssignment.objects.filter(student=self,student_status=True).count()
        if complete_assignments> 0:
            return complete_assignments
        else:
            return "No completed assignments"

    #pending assignments
    def pending_assignments(self):
        pending_assignments=StudentAssignment.objects.filter(student=self,student_status=False).count()
        if pending_assignments> 0:
            return pending_assignments
        else:
            return "No pending assignments"
    
    #Modifies the plural in admin dashboard ad sorts alphabetically
    class Meta:
        verbose_name_plural="4. Students"

#Chapter Model
class Chapter(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_chapters')#relationship of Chapter to Course
    title=models.CharField(max_length=250)
    description=models.TextField()
    remarks=models.TextField(null=True)
    video = models.FileField(upload_to='chapter_videos/', null=True)

    def __str__(self):
        return f"Course: {self.course}, Title: {self.title}"

    #Modifies the plural in admin dashboard ad sorts alphabetically
    class Meta:
        verbose_name_plural="5. Chapters"

#student course enrollment model
class StudentCourseEnrollment(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE,related_name='enrolled_courses')
    student=models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrolled_students')
    enrolled_time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Course: {self.course}, Student: {self.student}"
        
    class Meta:
        verbose_name_plural="6. Enrolled Courses"

#Course rating and reviews

class CourseRating(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    student=models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    rating=models.PositiveBigIntegerField(default=0)
    reviews=models.TextField(null=True)
    review_time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Course: {self.course}, Student: {self.student}, Rating: {self.rating}, Review: {self.reviews}"
    
    class Meta:
        verbose_name_plural="7. Course Ratings and Reviews"

##student favorite courses
class StudentFavoriteCourse(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE)
    student=models.ForeignKey(Student, on_delete=models.CASCADE)
    status=models.BooleanField(default=False)

    class Meta:
        verbose_name_plural="8. Student Favorite Courses"

    def __str__(self):
        return f"Course: {self.course}, Student: {self.student}"

##student assignment
class StudentAssignment(models.Model):
    teacher=models.ForeignKey(Teacher, on_delete=models.CASCADE,null=True)
    student=models.ForeignKey(Student, on_delete=models.CASCADE,null=True)
    title=models.CharField(max_length=250)
    detail=models.TextField(null=True)
    student_status=models.BooleanField(default=False,null=True)
    student_submission=models.FileField(upload_to='student_submissions/', null=True)
    add_time=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural="9. Student Assignment"

    def __str__(self):
        return f"Assignment: {self.title}, Student: {self.student}, Comment: {self.detail} , Status: {self.student_status}"

#notification model
class Notification(models.Model):
    teacher=models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    student=models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    notif_subject=models.CharField(max_length=500, verbose_name="Notification Subject", null=True)
    notif_for=models.CharField(max_length=500, verbose_name="Notification For")
    notif_created_time=models.DateTimeField(auto_now_add=True)
    notif_read_status=models.BooleanField(default=False, verbose_name="Notification Status")

    class Meta:
        verbose_name_plural="91. Notifications"

####Quiz Modal
class Quiz(models.Model):
    teacher=models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=250)
    description = models.TextField(null=True)
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "92. Quiz"

    def assign_status(self):
        assign_status = CourseQuiz.objects.filter(quiz=self).count()
        return assign_status

    
    def __str__(self):
        return f"Title: {self.title}, Description: {self.description}, Teacher: {self.teacher}"
####Quiz Questions Modal
class QuizQuestions(models.Model):
    quiz=models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True)
    questions=models.CharField(max_length=10000)
    ans1=models.CharField(max_length=250)
    ans2=models.CharField(max_length=250)
    ans3=models.CharField(max_length=250)
    ans4=models.CharField(max_length=250)
    correct_ans=models.CharField(max_length=250)
    add_time=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural="93. Quiz Questions"

    def __str__(self):
        return f"Question: {self.questions}, Correct Answer: {self.correct_ans}"

###Add Quiz to course
class CourseQuiz(models.Model):
    teacher=models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    course=models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    quiz=models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True)
    add_time=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural="94. Course Quiz"

    def __str__(self):
        return f"Course: {self.course}, Quiz: {self.quiz}"

###Answer model
class AttemptQuiz(models.Model):
    student=models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    quiz=models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True)
    question=models.ForeignKey(QuizQuestions, on_delete=models.CASCADE, null=True)
    correct_ans=models.CharField(max_length=250, null=True)
    add_time=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural="95. Attempted Questions/quiz"

    def __str__(self):
        return f"Student: {self.student}, {self.question}"

#Study Material Model
class StudyMaterial(models.Model):
    course=models.ForeignKey(Course, on_delete=models.CASCADE)#relationship of Chapter to Course
    title=models.CharField(max_length=250)
    description=models.TextField()
    remarks=models.TextField(null=True)
    upload = models.FileField(upload_to='study_materials/', null=True)

    #Modifies the plural in admin dashboard ad sorts alphabetically
    class Meta:
        verbose_name_plural="96. Course Study Materials"

    def __str__(self):
        return f"{self.title}, {self.description}, {self.remarks}"

#FAQS Model
class FAQS(models.Model):
    question=models.CharField(max_length=250)
    answer=models.TextField()

    #Modifies the plural in admin dashboard ad sorts alphabetically
    class Meta:
        verbose_name_plural="97.  FAQs"

    def __str__(self):
        return f"Question:{self.question}, Answer:{self.answer}"

#Contact Us Model
class ContactUs(models.Model):
    full_name=models.CharField(max_length=250)
    email=models.CharField(max_length=100)
    message=models.TextField()
    add_time=models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        send_mail(
            "ContactUs message",
            "Name: "+self.full_name+"\nEmail: "+self.email+"\nMessage: "+self.message,
            "your email",
            [self.email],
            fail_silently=False,
            )
        return super(ContactUs, self).save(*args, **kwargs)

    #Modifies the plural in admin dashboard ad sorts alphabetically
    class Meta:
        verbose_name_plural="98. Contact Us"

    def __str__(self):
        return f"Name: {self.full_name}, Email: {self.email}, Message: {self.message}"






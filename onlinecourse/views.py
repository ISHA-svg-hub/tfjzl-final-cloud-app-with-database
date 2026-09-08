from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Lesson, Question, Choice, Submission

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    
    if request.method == 'POST':
        # Create a new submission for the course
        submission = Submission.objects.create(enrollment_id=course_id)
        
        # Collect selected choices from POST data
        selected_choice_ids = request.POST.getlist('choice')
        for choice_id in selected_choice_ids:
            choice = Choice.objects.get(pk=int(choice_id))
            submission.choices.add(choice)
            
        submission.save()
        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    selected_choices = submission.choices.all()
    total_score = 0
    max_score = 0
    
    # Calculate score logic
    for question in course.question_set.all():
        max_score += question.grade
        question_choices = set(question.choice_set.all())
        correct_choices = set(question.choice_set.filter(is_correct=True))
        selected_in_question = set(selected_choices.filter(question=question))
        
        if selected_in_question == correct_choices:
            total_score += question.grade

    context['course'] = course
    context['submission'] = submission
    context['total_score'] = total_score
    context['max_score'] = max_score
    context['passed'] = total_score >= (max_score * 0.7)
    
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)

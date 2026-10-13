from django import forms
from tasks.models import TaskModel


class TaskForm(forms.ModelForm):
    class Meta:
        model = TaskModel
        fields = ['title', 'description', 'status', 'due_date']
        widgets = {
            'due_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'title': forms.TextInput(
                attrs={'placeholder': 'Enter task title', 'class': 'form-control'}
            ),
            'description': forms.Textarea(
                attrs={
                    'placeholder': 'Enter task description',
                    'rows': 4,
                    'class': 'form-control',
                }
            ),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError('Title cannot be empty.')
        return title

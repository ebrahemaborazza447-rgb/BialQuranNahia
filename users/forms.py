from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from .models import Lesson
from .models import Subscription

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('name', 'email', 'password1', 'password2')
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            "title",
            "date",
            "time",
            "teacher",
            "student",
            "meeting_link",
            "record_link",
            "content"
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
            "content": forms.Textarea(attrs={"rows": 3}),
        }
        
class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['payment_image']  # بس صورة الدفع

    def clean_payment_image(self):
        payment_image = self.cleaned_data.get('payment_image')
        if not payment_image:
            raise forms.ValidationError("يجب رفع صورة إيصال الدفع.")
        return payment_image

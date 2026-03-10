from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Group, GroupSubject, Comment


class GroupForm(forms.ModelForm):
    """
    Form that handles group data.
    """
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': _('Enter a name for your group'),
            'class': 'form-control'
        }),
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': _('Describe what your group is about...'),
            'class': 'form-control'
        }),
    )

    category = forms.ChoiceField(
        choices=[
            ('', _('Select a category')),
            ('technology', _('Technology')),
            ('arts_culture', _('Arts & Culture')),
            ('sports', _('Sports')),
            ('science', _('Science')),
            ('business', _('Business')),
            ('lifestyle', _('Lifestyle')),
            ('other', _('Other')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text=_('Categorizing your group helps people find it more easily.')
    )

    cover = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text=_("Recommended dimensions: 900 × 300 pixels. Maximum size: 2MB."),
        required=False
    )

    is_private = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text=_('Private groups are only visible to members.')
    )

    class Meta:
        model = Group
        fields = ('title', 'description', 'category', 'cover', 'is_private')

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 4:
            raise forms.ValidationError(_('Group title must be at least 4 characters long.'))
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 20:
            raise forms.ValidationError(_('Please provide a more detailed description (at least 20 characters).'))
        return description

    def clean_cover(self):
        cover = self.cleaned_data.get('cover')
        if cover and cover.size > 2 * 1024 * 1024:
            raise forms.ValidationError(_('Image file too large. Please keep it under 2MB.'))
        return cover


class GroupSubjectForm(forms.ModelForm):
    """
    Form that handles group subject/post creation.
    """
    title = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': _('Enter a title for your post'),
            'class': 'form-control'
        })
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 8,
            'placeholder': _('Write your post content here...'),
            'class': 'form-control'
        })
    )

    class Meta:
        model = GroupSubject
        fields = ('title', 'description')


class CommentForm(forms.ModelForm):
    """
    Form that handles commenting on group subjects.
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': _('Write your comment...'),
            'class': 'form-control'
        })
    )

    class Meta:
        model = Comment
        fields = ('content',)


class GroupSettingsForm(forms.ModelForm):
    """
    Form for group administrators to modify group settings.
    """
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'class': 'form-control'
        })
    )

    category = forms.ChoiceField(
        choices=[
            ('', _('Select a category')),
            ('technology', _('Technology')),
            ('arts_culture', _('Arts & Culture')),
            ('sports', _('Sports')),
            ('science', _('Science')),
            ('business', _('Business')),
            ('lifestyle', _('Lifestyle')),
            ('other', _('Other')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    is_private = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Group
        fields = ('title', 'description', 'category', 'is_private')
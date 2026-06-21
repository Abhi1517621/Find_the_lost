# portal/models.py
from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=15)
    hostel = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    year_of_study = models.IntegerField()
    
class Item(models.Model):
    ITEM_TYPES = (('Lost', 'Lost'), ('Found', 'Found'))
    STATUS_CHOICES = (('Open', 'Open'), ('Resolved', 'Resolved'))
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Open')
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_type}: {self.title}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='chats')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
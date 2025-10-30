from django.db import models
from django.urls import reverse
import os

class Tattoo(models.Model):
    telegram_id = models.BigIntegerField()
    username = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    filename = models.CharField(max_length=255)
    file_id = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField()
    likes = models.IntegerField(default=0)  # Campo mancante
    
    class Meta:
        db_table = 'tattoos'  # Usa la tabella esistente del bot
        
    def __str__(self):
        return f"{self.description[:50]}... by {self.username}"
    
    def get_absolute_url(self):
        return f"/detail.html?id={self.pk}"  # URL corretto per HTML statico
    
    @property
    def image_url(self):
        return f"/images/{self.filename}"
    
    @property
    def telegram_url(self):
        if self.username:
            return f"https://t.me/{self.username}"
        return "#"
    
    @property
    def seo_title(self):
        title = f"{self.description} - Roma Studio Tattoo"
        return title[:60] if len(title) > 60 else title
    
    @property
    def seo_description(self):
        desc = f"Tatuaggio: {self.description}. Realizzato presso Roma Studio Tattoo Roma. Contatta {self.username} su Telegram."
        return desc[:160] if len(desc) > 160 else desc
    
    @property
    def keywords(self):
        return f"tatuaggio, {self.description.lower()}, roma, studio tattoo, {self.username}"
    
    @property 
    def file_exists(self):
        file_path = f"/var/www/romastudiotattoo/images/{self.filename}"
        return os.path.exists(file_path)

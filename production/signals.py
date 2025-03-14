from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import Part, Production, Aircraft, AircraftPart, Team

@receiver(post_save, sender=Part)
def check_low_stock(sender, instance, **kwargs):
    """Parça stoku düşük olduğunda ilgili takıma bildirim gönder"""
    if instance.is_low_stock:
        # Parçayı üreten takımı bul
        team = Team.objects.filter(team_type=instance.team_type).first()
        if team:
            subject = f'Düşük Stok Uyarısı: {instance.name}'
            message = f'''
            Sayın {team.name} üyeleri,

            {instance.name} parçasının stok seviyesi kritik seviyenin altına düştü.
            Mevcut stok: {instance.stock}

            Lütfen en kısa sürede üretim planlaması yapınız.

            Saygılarımızla,
            Üretim Sistemi
            '''
            recipient_list = [
                member.email for member in team.members.all()
                if member.email
            ]
            if recipient_list:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_list,
                    fail_silently=True
                )

@receiver(post_save, sender=Production)
def update_part_stock(sender, instance, created, **kwargs):
    """Üretim kaydedildiğinde parça stoğunu güncelle"""
    if created:
        instance.part.stock += instance.quantity
        instance.part.save()

@receiver(post_save, sender=Aircraft)
def notify_completion(sender, instance, **kwargs):
    """Uçak üretimi tamamlandığında bildirim gönder"""
    if instance.completed_at and instance.completed_at != instance._loaded_values.get('completed_at'):
        subject = f'Uçak Üretimi Tamamlandı: {instance.get_aircraft_type_display()}'
        message = f'''
        {instance.get_aircraft_type_display()} üretimi başarıyla tamamlandı.

        Üretim başlangıç: {instance.created_at.strftime('%d.%m.%Y %H:%M')}
        Üretim bitiş: {instance.completed_at.strftime('%d.%m.%Y %H:%M')}

        Saygılarımızla,
        Üretim Sistemi
        '''
        # Tüm admin kullanıcılara bildirim gönder
        recipient_list = [
            user.email for user in User.objects.filter(is_staff=True)
            if user.email
        ]
        if recipient_list:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=True
            )

@receiver(post_save, sender=AircraftPart)
def check_aircraft_completion(sender, instance, created, **kwargs):
    """Uçağa parça eklendiğinde tamamlanma durumunu kontrol et"""
    if created and instance.aircraft.is_complete:
        # Montaj takımına bildirim gönder
        assembly_team = Team.objects.filter(team_type='ASSEMBLY').first()
        if assembly_team:
            subject = f'Uçak Montaja Hazır: {instance.aircraft.get_aircraft_type_display()}'
            message = f'''
            Sayın {assembly_team.name} üyeleri,

            {instance.aircraft.get_aircraft_type_display()} için gerekli tüm parçalar hazır.
            Montaj işlemine başlayabilirsiniz.

            Saygılarımızla,
            Üretim Sistemi
            '''
            recipient_list = [
                member.email for member in assembly_team.members.all()
                if member.email
            ]
            if recipient_list:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_list,
                    fail_silently=True
                )

@receiver(m2m_changed, sender=Team.members.through)
def update_user_team(sender, instance, action, pk_set, **kwargs):
    """Kullanıcı takıma eklendiğinde veya çıkarıldığında bildirim gönder"""
    if action in ["post_add", "post_remove"]:
        users = User.objects.filter(pk__in=pk_set)
        for user in users:
            if user.email:
                if action == "post_add":
                    subject = f'Takıma Hoş Geldiniz: {instance.name}'
                    message = f'''
                    Sayın {user.get_full_name() or user.username},

                    {instance.name} ekibine dahil edildiniz.
                    Üretim sistemine giriş yaparak görevlerinizi görüntüleyebilirsiniz.

                    Saygılarımızla,
                    Üretim Sistemi
                    '''
                else:
                    subject = f'Takımdan Ayrıldınız: {instance.name}'
                    message = f'''
                    Sayın {user.get_full_name() or user.username},

                    {instance.name} ekibinden çıkarıldınız.

                    Saygılarımızla,
                    Üretim Sistemi
                    '''
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True
                ) 
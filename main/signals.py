import os

from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from jb_test.settings import MAIN_URL, MEDIA_ROOT
from utils.base58 import Encoder
from utils.images import Avatar, Plates
from utils.other import expires, no_signals_recursion, delete, move
from .models import CustomUser, Profile, Code


@receiver(post_save, sender=CustomUser)
def back_worker(sender, instance=None, created=False, **kwargs):
    """
    Create empty profile and invitation code with qr code for new user
    """
    if created:
        # Create empty User Profile
        profile = Profile.objects.create(owner=instance)

        # Generate invitation code for new User
        encode = Encoder(f'{MAIN_URL}/register', instance.id, 1)
        code = Code.objects.create(
            owner=instance,
            number=encode.invitation_code.split('_')[0],
            sort=1,
            code=encode.invitation_code,
            url=encode.encoded_url,
            qr=encode.qr()[1],
        )

        # Update number of people using social network
        counter = cache.get('number_of_users')
        if counter is not None:
            counter += 1
        else:
            counter = CustomUser.objects.count()
        cache.set('number_of_users', counter, expires(hours=1))

        # Update quantity of invites in invitation code that was used by user
        invited_with = instance.invitation_code
        if invited_with is not None:
            invited_with.joined += 1
            invited_with.save()


@receiver(post_save, sender=Profile)
@no_signals_recursion
def profile_images_correction(sender, instance=None, created=False, **kwargs):
    if not created:
        rel_avatar_dir = os.path.join('profiles', instance.owner.email, 'avatar')
        rel_plates_dir = os.path.join('profiles', instance.owner.email, 'plates')
        abs_avatar_dir = os.path.join(MEDIA_ROOT, rel_avatar_dir)
        abs_plates_dir = os.path.join(MEDIA_ROOT, rel_plates_dir)

        current_plates = (instance.plate_img_1,
                          instance.plate_img_2,
                          instance.plate_img_3,
                          instance.plate_img_4)

        for number, image in enumerate(current_plates):
            if 'tmp' in image.name.split('/'):
                delete(abs_plates_dir, f'original_{number + 1}')
                move(image.path, abs_plates_dir, f'original_{number + 1}')
        try:
            current_avatar = instance.avatar.path
            if 'tmp' in current_avatar.split('/'):
                delete(abs_avatar_dir, 'original')
                move(current_avatar, abs_avatar_dir, 'original')
        except ValueError:
            Avatar.adorable_avatar(abs_avatar_dir, rel_avatar_dir, instance.owner.email)

        plates_corrector = Plates(instance.template, abs_plates_dir)
        new_plates = list(os.path.join(rel_plates_dir, name) for name in plates_corrector.transform())

        instance.plate_img_1 = new_plates[0]
        instance.plate_img_2 = new_plates[1]
        instance.plate_img_3 = new_plates[2]
        instance.plate_img_4 = new_plates[3]

        avatar_corrector = Avatar(abs_avatar_dir)
        new_avatar = os.path.join(rel_avatar_dir, avatar_corrector.transform())
        instance.avatar = new_avatar

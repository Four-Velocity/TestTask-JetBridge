import os
from datetime import timedelta
from random import randint, choice
from time import sleep

import requests
from faker import Faker
from pytz import timezone

from generator.settings import get_settings
from jb_test.settings import MEDIA_ROOT
from main.models import CustomUser, Code, TMP_DIRS
from utils.base58 import Encoder
from utils.other import create_folder

requests.packages.urllib3.disable_warnings()


class Generator:
    used_emails = set()
    existing_codes = []
    fake = Faker()
    avatar_reserve = []
    images_reserve = []

    def generate_image(self, reserve, api_url, api_type, api_verify, api_path_to_content):
        if api_type == 'json':
            if not reserve:
                reserve = requests.request('GET', api_url, verify=api_verify).json()
            number = randint(0, len(reserve) - 1)
            url = reserve.pop(number)
            for path in api_path_to_content:
                url = url[path]
            content = requests.request('GET', url, verify=api_verify).content
        elif api_type == 'content':
            content = requests.request('GET', api_url, verify=api_verify).content
        else:
            content = None
        return content

    def unique_email(self):
        email = self.fake.ascii_email()
        if email not in self.used_emails:
            self.used_emails.add(email)
            return email
        else:
            return self.unique_email()

    def generate_period_dates(self, start_period, period):
        star_date = start_period + timedelta(weeks=4 * period)
        end_date = star_date + timedelta(weeks=4)
        return self.fake.date_time_between(start_date=star_date, end_date=end_date, tzinfo=timezone('Europe/Kiev'))

    def generate(self):

        def generate_image(img_type):
            sleep(api.sleep_time)
            if img_type == 'avatar':
                return self.generate_image(self.avatar_reserve,
                                           api.avatar,
                                           api.avatar_type,
                                           api.avatar_verify,
                                           api.avatar_path_to_content)
            elif img_type == 'plate':
                return self.generate_image(self.images_reserve,
                                           api.image,
                                           api.image_type,
                                           api.image_verify,
                                           api.image_path_to_content)
            else:
                return

        config = get_settings()
        basic, chances, api = config.Basic, config.Chances, config.API
        max_users = basic.first_period
        users_count = 0
        for period in range(basic.periods):
            print('BIG LOOP')
            max_users += int(basic.first_period * basic.growth / 100 * period)
            users_in_period = randint(max_users - users_count, max_users)
            users_count += users_in_period
            period_dates = sorted([self.generate_period_dates(basic.start_date, period)
                                   for _ in range(users_in_period)])
            for date in period_dates:
                print('USER')
                email = self.unique_email()
                user = CustomUser(email=email)
                if basic.default_password:
                    user.set_password(basic.default_password)
                else:
                    user.set_password(self.fake.ean8)

                if randint(1, 100) <= chances.invite:
                    try:
                        user.invitation_code = choice(self.existing_codes)
                    except IndexError:
                        user.invitation_code = None

                user.save()

                self.existing_codes.append(user.invite_code)

                if randint(1, 100) <= chances.non_personal_invite:
                    sort = randint(2, 3)
                    encode = Encoder(r'http://127.0.0.1:8000/register', len(self.existing_codes) + 1, sort)
                    additional = Code.objects.create(owner=None,
                                                     number=encode.invitation_code.split('_')[0],
                                                     sort=sort,
                                                     code=encode.invitation_code,
                                                     url=encode.encoded_url,
                                                     qr=encode.qr()[1])
                    self.existing_codes.append(additional)

                profile = user.profile
                gender = randint(1, 2)

                if gender == 1:
                    first_name = self.fake.first_name_male()
                    last_name = self.fake.last_name_male()
                else:
                    first_name = self.fake.first_name_female()
                    last_name = self.fake.last_name_female()


                if randint(1, 100) <= chances.non_standart_avatar:
                    content = generate_image('avatar')

                    if content is not None:
                        relative_avatar = os.path.join(TMP_DIRS['avatar'], 'avatar.jpeg')
                        create_folder(os.path.join(MEDIA_ROOT, TMP_DIRS['avatar']))
                        with open(os.path.join(MEDIA_ROOT, relative_avatar), 'wb') as img:
                            img.write(content)
                    else:
                        relative_avatar = None
                else:
                    relative_avatar = None

                date_joined = date


                plates = []
                for index in range(4):
                    plate = generate_image('plate')

                    if plate is not None:
                        relative_image = os.path.join(TMP_DIRS['plates'], f'original_{index + 1}.png')
                        create_folder(os.path.join(MEDIA_ROOT, TMP_DIRS['plates']))
                        with open(os.path.join(MEDIA_ROOT, relative_image), 'wb') as img:
                            img.write(plate)
                        plates.append(relative_image)
                    else:
                        plates.append(None)

                template = randint(1, 4)

                finished = True

                updates = dict(first_name=first_name,
                               last_name=last_name,
                               gender=gender,
                               avatar=relative_avatar,
                               date_joined=date_joined,
                               plate_img_1=plates[0],
                               plate_img_2=plates[1],
                               plate_img_3=plates[2],
                               plate_img_4=plates[3],
                               template=template,
                               finished=finished)

                for key, value in updates.items():
                    setattr(profile, key, value)

                profile.save()

# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    models.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ipetruni <ipetruni@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/19 12:09:43 by ipetruni          #+#    #+#              #
#    Updated: 2024/11/19 12:09:45 by ipetruni         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.db import models
from django.contrib.auth.models import User

def upload_to(instance, filename):
    return f'avatars/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100, unique=True)
    avatar_url = models.ImageField(upload_to=upload_to, blank=True, null=True)

    def __str__(self):
        return self.display_name

    def get_avatar_url(self):
        return self.avatar_url.url if self.avatar_url else '/static/default.png'

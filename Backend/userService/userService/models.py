# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    models.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ipetruni <ipetruni@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/19 12:09:43 by ipetruni          #+#    #+#              #
#    Updated: 2024/11/21 12:38:39 by ipetruni         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255, unique=True)
    avatar = models.ImageField(upload_to='avatars/', default='images/default.png')

    def __str__(self):
        return self.display_name

    def get_avatar(self):
        return self.avatar.url if self.avatar else None

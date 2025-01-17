# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    models.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ipetruni <ipetruni@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2024/11/19 12:09:43 by ipetruni          #+#    #+#              #
#    Updated: 2025/01/17 15:35:15 by ipetruni         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_online = models.BooleanField(default=False)

    def get_friends(self):
        friendships = Friendship.objects.filter(
            (Q(from_profile=self) | Q(to_profile=self)) & Q(status='accepted')
        )
        friends = []
        for friendship in friendships:
            if friendship.from_profile == self:
                friends.append(friendship.to_profile)
            else:
                friends.append(friendship.from_profile)
        return friends

class Friendship(models.Model):
    from_profile = models.ForeignKey(Profile, related_name='from_friend_set', on_delete=models.CASCADE)
    to_profile = models.ForeignKey(Profile, related_name='to_friend_set', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted')], default='pending')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_profile', 'to_profile')

class ChatModel(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    thread_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.message[:50]}"
    
class ChatNotification(models.Model):
    chat = models.ForeignKey(to=ChatModel, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
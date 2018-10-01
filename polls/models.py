from django.db import models

from domains.models import Domain


class Poll(models.Model):
    content = models.CharField(max_length=256)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='poll_options')
    value = models.CharField(max_length=256)

    def __str__(self):
        return self.value

from django.db import models

class Voter(models.Model):
    name = models.CharField(max_length=254, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    password = models.CharField(max_length=100)
    identity_number = models.CharField(max_length=50, blank=True)
    is_registered = models.BooleanField(default=False, null=True)
    has_voted = models.BooleanField(default=False, null=True)
    reference = models.CharField(max_length=254, blank=True)
    a_reference = models.CharField(max_length=2500, blank=True, default="")
    b_reference = models.CharField(max_length=2500, blank=True, default="")
    private_key = models.CharField(max_length=2500, blank=True)
    public_key = models.CharField(max_length=2500, blank=True)
    vote = models.CharField(max_length=2500, blank=True)

class Candidate(models.Model):
    name = models.CharField(max_length=254, blank=True)
    image = models.CharField(max_length=2500, blank=True)
    xnt = models.CharField(max_length=2500, blank=True)
    ynt = models.CharField(max_length=2500, blank=True)
    yes_count = models.CharField(max_length=2500, blank=True)
    no_count = models.CharField(max_length=2500, blank=True)

class TallyingAuthority(models.Model):
    name = models.CharField(max_length=254, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    password = models.CharField(max_length=100)
    identity_number = models.CharField(max_length=50, blank=True)
    is_registered = models.BooleanField(default=False, null=True)
    result_submitted = models.BooleanField(default=False, null=True)
    private_key = models.CharField(max_length=2500, blank=True)
    public_key = models.CharField(max_length=2500, blank=True)
    x_value = models.CharField(max_length=2500, blank=True)
    y_value = models.CharField(max_length=2500, blank=True)

class Admin(models.Model):
    name = models.CharField(max_length=254, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    password = models.CharField(max_length=100)

class System(models.Model):
    q = models.CharField(max_length=2500, blank=True)
    g = models.CharField(max_length=2500, blank=True)
    voter_registration_open = models.BooleanField(default=False, null=True)
    tallying_authority_registration_open = models.BooleanField(default=False, null=True)
    voting_enabled = models.BooleanField(default=False, null=True)

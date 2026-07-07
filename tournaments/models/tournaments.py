import uuid
from django.db import models
from django.utils import timezone

class TournamentStatus(models.TextChoices):
    UPCOMING = 'UPCOMING', 'Upcoming'
    ACCEPTING_APPLICATIONS = 'ACCEPTING_APPLICATIONS', 'Accepting Applications'
    APPLICATIONS_CLOSED = 'APPLICATIONS_CLOSED', 'Applications Closed'
    ONGOING = 'ONGOING', 'Ongoing'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'

class InstitutionType(models.TextChoices):
    UNIVERSITY = 'UNIVERSITY', 'University'
    SCHOOL = 'SCHOOL', 'School'
    CLUB = 'CLUB', 'Club'
    SPORTS_BOARD = 'SPORTS_BOARD', 'Sports Board'
    CORPORATE = 'CORPORATE', 'Corporate'
    OTHER = 'OTHER', 'Other'

class TournamentCategory(models.TextChoices):
    INTER_COLLEGE = 'INTER_COLLEGE', 'Inter College'
    INTER_SCHOOL = 'INTER_SCHOOL', 'Inter School'
    CLUB = 'CLUB_LEVEL', 'Club Level'
    DISTRICT = 'DISTRICT_LEVEL', 'District Level'
    STATE = 'STATE_LEVEL', 'State Level'
    NATIONAL = 'NATIONAL_LEVEL', 'National Level'
    CORPORATE = 'CORPORATE_LEVEL', 'Corporate level'
    OPEN = 'OPEN', 'Open'

class Tournament(models.Model):
    tournament_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    regulation = models.ForeignKey(
        'tournaments.Regulation',
        on_delete=models.PROTECT,
        related_name='tournaments'
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="created_by",
        related_name='created_tournaments'
    )
    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=20,
        choices=TournamentCategory.choices
    )
    status = models.CharField(
        max_length=30,
        choices=TournamentStatus.choices,
        default=TournamentStatus.UPCOMING
    )
    locations = models.JSONField(default=list, blank=True)
    banner_image = models.ImageField(
        upload_to='tournament_banners/',
        blank=True,
        null=True
    )
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    application_starts_from = models.DateTimeField(null=True, blank=True)
    application_deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    winner_team = models.ForeignKey(
        'teams.Team', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='tournaments_won'
    )

    class Meta:
        db_table = 'tournaments'
        ordering = ['-created_at']
    
    def refresh_status(self):
        if self.status == 'ACCEPTING_APPLICATIONS' and self.application_deadline and timezone.now() >= self.application_deadline:
            self.status = 'APPLICATIONS_CLOSED'
            self.save(update_fields=['status'])

    def __str__(self):
        return f"{self.name} ({self.category})"


class TournamentOrganizer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='organizers'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='organized_tournaments'
    )
    institution_name = models.CharField(max_length=255, blank=True)
    institution_type = models.CharField(max_length=20, choices=InstitutionType.choices, blank=True)
    institution_email = models.EmailField(blank=True)
    institution_logo = models.ImageField(upload_to='institution_logos/', blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tournament_organizers'
        constraints = [
            models.UniqueConstraint(
                fields=['tournament', 'user'],
                name='unique_organizer_per_tournament'
            )
        ]

    def __str__(self):
        return f"{self.user.email} — {self.tournament.name}"


class Group(models.Model):
    group_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tournament = models.ForeignKey('tournaments.Tournament', on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=50)

    class Meta:
        db_table = 'groups'
        constraints = [models.UniqueConstraint(fields=['tournament', 'name'], name='unique_group_name_per_tournament')]

    def __str__(self):
        return f"{self.name} — {self.tournament.name}"
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from datetime import date, time, timedelta
from pathlib import Path

from .models import Poster, Flyer, Announcement, Tag

class PosterTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='posteruser',
            email='posteruser@email.com',
            password='testpass123',
        )       
        self.poster = Poster.objects.create(
            poster_type = 'PARISH',
            name = 'Test Parish',
            bio = 'An awesome Parish near you.',
            address = 'Awesome Street 1234',
            email = 'parish@email.com',
            phone_number = '+521234567890',
        )
        self.user.poster_for.add(self.poster)

    def test_poster_model(self):
        self.assertEqual(self.poster.poster_type,'PARISH')
        self.assertEqual(self.poster.name, 'Test Parish')
        self.assertEqual(self.poster.bio,'An awesome Parish near you.')
        self.assertEqual(self.poster.address,'Awesome Street 1234')
        self.assertEqual(self.poster.email,'parish@email.com')
        self.assertEqual(self.poster.phone_number, '+521234567890')
        self.assertIn(self.poster,self.user.poster_for.all())
        self.assertTrue(
            self.user.poster_for.filter(pk=self.poster.pk).exists()
        )

    def test_poster_detail_view(self):
        response = self.client.get(self.poster.get_absolute_url())
        no_response = self.client.get('/ps/100000000')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, "An awesome Parish near you.")
        self.assertTemplateUsed(response, 'poster_detail.html')

class AnnouncementTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123',
        )
        self.poster = Poster.objects.create(
            poster_type = 'GROUP',
            name = 'Test Group',
            bio = 'An awesome Group near you.',
            address = 'Cool Street 1234',
            email = 'group@email.com',
            phone_number = '+521234567890',
        )
        self.user.poster_for.add(self.poster)

        self.announcement = Announcement.objects.create(
            title = 'A sample announcement',
            description = 'An important announcement.',
            posted_by = self.poster,
        )

    def test_announcement_model(self):
        self.assertEqual(self.announcement.title, 'A sample announcement')
        self.assertEqual(self.announcement.description, 'An important announcement.')
        self.assertEqual(self.announcement.posted_by.name, 'Test Group')
        self.assertEqual(str(self.announcement), "A sample announcement by Test Group")
        # Missing Reverse match, no URL created yet.

class FlyerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
                    username='testuser',
                    email='testuser@email.com',
                    password='testpass123',
                )
        self.other_user = get_user_model().objects.create_user(
            username='otheruser',
            email='otheruser@email.com',
            password='testpass123',
        )
        self.poster = Poster.objects.create(
                    poster_type = 'GROUP',
                    name = 'Test Group',
                    bio = 'An awesome Group near you.',
                    address = 'Cool Street 1234',
                    email = 'group@email.com',
                    phone_number = '+521234567890',
                )
        self.user.poster_for.add(self.poster)
        self.user.can_post = True
        self.user.save(update_fields=["can_post"])

        self.image_content = (
            Path(__file__).resolve().parents[1] / "media/images/IMG_0822.png"
        ).read_bytes()

        self.flyer = Flyer.objects.create(
            image =  SimpleUploadedFile(
                     name='test_image.png',
                     content=self.image_content,
                     content_type='image/png',
            ),
            event_name = 'Awesome event',
            description = 'Awesome description.',
            event_date = date(2012, 12, 12),
            event_start_time = time(12, 12),
            posted_by = self.poster,
        )

        
    def test_flyer_model(self):
        self.assertEqual(self.flyer.event_name,'Awesome event')
        self.assertEqual(self.flyer.description,'Awesome description.')
        self.assertEqual(self.flyer.event_date, date(2012, 12, 12))
        self.assertEqual(self.flyer.event_start_time, time(12, 12))
        self.assertEqual(self.flyer.posted_by, self.poster)

        self.assertTrue(self.flyer.image.name.startswith("images/"))
        self.assertEqual(self.flyer.image.size, len(self.image_content))

        with self.flyer.image.open("rb") as uploaded_image:
           self.assertEqual(uploaded_image.read(), self.image_content)

    def test_flyer_list_view(self):
        response = self.client.get(reverse("flyer_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<img")
        self.assertContains(response, self.flyer.image.url)
        self.assertTemplateUsed(response, 'flyer_list_all.html')

    def test_flyer_detail_view(self):
        response = self.client.get(self.flyer.get_absolute_url())
        no_response = self.client.get('posts/100000/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(no_response.status_code, 404)
        self.assertContains(response, "Awesome event")
        self.assertContains(response, '<img')
        self.assertContains(response, self.flyer.image.url)
        self.assertNotContains(response, reverse("flyer_edit", kwargs={"pk": self.flyer.pk}))
        self.assertNotContains(response, reverse("flyer_delete", kwargs={"pk": self.flyer.pk}))
        self.assertTemplateUsed(response, 'flyer_detail.html')

    def test_flyer_detail_shows_actions_to_authorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.flyer.get_absolute_url())
        self.assertContains(response, reverse("flyer_edit", kwargs={"pk": self.flyer.pk}))
        self.assertContains(response, reverse("flyer_delete", kwargs={"pk": self.flyer.pk}))

    def test_flyer_detail_does_not_show_actions_to_unauthorized_user(self):
        self.client.force_login(self.other_user)
        response = self.client.get(self.flyer.get_absolute_url())
        self.assertNotContains(response, reverse("flyer_edit", kwargs={"pk": self.flyer.pk}))
        self.assertNotContains(response, reverse("flyer_delete", kwargs={"pk": self.flyer.pk}))

    def test_flyer_edit_view_shows_current_tags_and_image(self):
        self.client.force_login(self.user)

        tags = {
            "target_tags": Tag.objects.create(name="Families", category="TARGET"),
            "activity_tags": Tag.objects.create(name="Retreat", category="ACTIVITY"),
            "organizer_tags": Tag.objects.create(name="Parish", category="ORGANIZER"),
        }
        self.flyer.tags.add(*tags.values())

        response = self.client.get(reverse("flyer_edit", kwargs={"pk": self.flyer.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'src="{self.flyer.image.url}"')
        for field_name, tag in tags.items():
            self.assertEqual(response.context["form"][field_name].value(), [tag.pk])

    def test_flyer_following_list_if_not_logged_in(self):
        response = self.client.get(reverse("following_flyer_list"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/posts/following/')

    def test_flyer_following_list_if_logged_in(self):
        self.user.followed_groups.add(self.poster)
        self.client.force_login(self.user)

        response = self.client.get(reverse("following_flyer_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<img")
        self.assertContains(response, self.flyer.image.url)
        self.assertTemplateUsed(response, 'flyer_list_following.html')

    def test_flyer_create_view(self):
        self.client.login(username='testuser', password='testpass123')

        target_tag = Tag.objects.create(name='Families',category='TARGET')
        activity_tag = Tag.objects.create(name='Retreat',category='ACTIVITY')
        organizer_tag = Tag.objects.create(name='Parish',category='ORGANIZER')

        response = self.client.post(
            reverse('flyer_new'),
            {
                'event_name': 'A new event',
                'description': 'A new decription.',
                'event_date': date(2026, 10, 10),
                'event_start_time': time(11,11),
                'posted_by': self.poster.pk,
                'target_tags': [target_tag.pk],
                'activity_tags': [activity_tag.pk],
                'organizer_tags': [organizer_tag.pk],
                'image': SimpleUploadedFile(
                    name='test_image.png',
                    content=self.image_content,
                    content_type='image/png',
                ),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Flyer.objects.last().event_name, 'A new event')
        self.assertEqual(Flyer.objects.last().posted_by, self.poster)
        self.assertEqual(set(Flyer.objects.last().tags.all()), {
        target_tag,
        activity_tag,
        organizer_tag,
    })

    def test_cannot_create_flyer_without_tags(self):
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(
            reverse('flyer_new'),
            {
                'event_name': 'A new event',
                'description': 'A new decription.',
                'event_date': date(2026, 10, 10),
                'event_start_time': time(11,11),
                'posted_by': self.poster.pk,
                'image': SimpleUploadedFile(
                    name='test_image.png',
                    content=self.image_content,
                    content_type='image/png',
                ),
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_cannot_create_flyer_with_one_tag_category_only(self):
        self.client.login(username='testuser', password='testpass123')

        target_tag = Tag.objects.create(name='Families',category='TARGET')

        response = self.client.post(
            reverse('flyer_new'),
            {
                'event_name': 'A new event',
                'description': 'A new decription.',
                'event_date': date(2026, 10, 10),
                'event_start_time': time(11,11),
                'posted_by': self.poster.pk,
                'target_tags': [target_tag.pk],
                'image': SimpleUploadedFile(
                    name='test_image.png',
                    content=self.image_content,
                    content_type='image/png',
                ),
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_flyer_update_view_for_poster_user(self):  # new
        self.client.login(username="testuser", password="testpass123")

        target_tag = Tag.objects.create(name='Families',category='TARGET')
        activity_tag = Tag.objects.create(name='Retreat',category='ACTIVITY')
        organizer_tag = Tag.objects.create(name='Parish',category='ORGANIZER')

        response = self.client.post(
            reverse("flyer_edit", args=[self.flyer.pk]),
            {
                'event_name': 'Updated title',
                'description': 'An udated description.',
                'event_date': date(2026, 10, 10),
                'event_start_time': time(11,11),
                'posted_by': self.poster.pk,
                'target_tags': [target_tag.pk],
                'activity_tags': [activity_tag.pk],
                'organizer_tags': [organizer_tag.pk],
                'image': SimpleUploadedFile(
                    name='test_image.png',
                    content=self.image_content,
                    content_type='image/png',
                ),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.flyer.refresh_from_db()
        self.assertEqual(self.flyer.event_name, "Updated title")
        self.assertEqual(self.flyer.description, "An udated description.")

    def test_flyer_update_view_forbidden_for_non_poster_user(self):  # new
        self.client.login(username="otheruser", password="testpass123")
        response = self.client.post(
            reverse("flyer_edit", args=[self.flyer.pk]),
            {"event_name": "Should not save", "event_description": "Should not save."},
        )
        self.assertEqual(response.status_code, 403)

    def test_flyer_delete_view_for_poster_user(self):  # new
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("flyer_delete", args=[self.flyer.pk])
        )
        self.assertRedirects(response, reverse("flyer_list"))

    def test_flyer_delete_view_forbidden_for_non_poster_user(self):  # new
        self.client.login(username="otheruser", password="testpass123")
        response = self.client.post(
            reverse("flyer_delete", args=[self.flyer.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_following_page_parish_flyers(self):
        parish = Poster.objects.create(
            poster_type="PARISH",
            name="Test Parish",
            bio="A parish",
            address="Test Street",
            email="parish@example.com",
        )
        self.user.followed_parish = parish
        self.user.save(update_fields=["followed_parish"])

        Flyer.objects.create(
            event_name="Parish event",
            description="A parish event",
            event_date=date(2026, 10, 10),
            event_start_time=time(11, 11),
            posted_by=parish,
            image=SimpleUploadedFile(
                name="parish.png",
                content=self.image_content,
                content_type="image/png",
            ),
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("following_flyer_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Parish event")

    def test_following_page_with_no_followed_groups(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("following_flyer_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "¡No estás siguiendo algún grupo en este momento!",
        )

    def test_following_page_followed_group_with_no_flyers(self):
        empty_group = Poster.objects.create(
            poster_type="GROUP",
            name="Empty Group",
            bio="No flyers",
            address="Test Street",
            email="empty@example.com",
        )
        self.user.followed_groups.add(empty_group)

        self.client.force_login(self.user)
        response = self.client.get(reverse("following_flyer_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Los Grupos que sigues aún no publican Flyers.",
        )

    def test_following_page_recent_vs_old_announcements(self):
        recent = Announcement.objects.create(
            title="Recent announcement",
            description="Recent",
            posted_by=self.poster,
        )
        older = Announcement.objects.create(
            title="Old announcement",
            description="Old",
            posted_by=self.poster,
        )
        Announcement.objects.filter(pk=older.pk).update(
            upload_date=timezone.now() - timedelta(days=8)
        )

        self.user.followed_groups.add(self.poster)
        self.client.force_login(self.user)

        response = self.client.get(reverse("following_flyer_list"))

        self.assertContains(response, "Recent")
        self.assertNotContains(response, "Old")

    def test_toggle_group_follow(self):
        self.client.force_login(self.user)
        url = reverse("toggle_follow", args=[self.poster.pk])

        response = self.client.post(url)
        self.assertRedirects(response, self.poster.get_absolute_url())
        self.assertTrue(
            self.user.followed_groups.filter(pk=self.poster.pk).exists()
        )

        response = self.client.post(url)
        self.assertRedirects(response, self.poster.get_absolute_url())
        self.assertFalse(
            self.user.followed_groups.filter(pk=self.poster.pk).exists()
        )

    def test_toggle_parish_follow(self):
        parish = Poster.objects.create(
            poster_type="PARISH",
            name="Test Parish",
            bio="A parish",
            address="Test Street",
            email="parish@example.com",
        )

        self.client.force_login(self.user)
        url = reverse("toggle_follow", args=[parish.pk])

        response = self.client.post(url)
        self.user.refresh_from_db()

        self.assertRedirects(response, parish.get_absolute_url())
        self.assertEqual(self.user.followed_parish, parish)

        response = self.client.post(url)
        self.user.refresh_from_db()

        self.assertRedirects(response, parish.get_absolute_url())
        self.assertIsNone(self.user.followed_parish)
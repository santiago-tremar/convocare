from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from datetime import date, time
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
        self.poster = Poster.objects.create(
                    poster_type = 'GROUP',
                    name = 'Test Group',
                    bio = 'An awesome Group near you.',
                    address = 'Cool Street 1234',
                    email = 'group@email.com',
                    phone_number = '+521234567890',
                )
        self.user.poster_for.add(self.poster)

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
        self.assertTemplateUsed(response, 'flyer_detail.html')

    def test_flyer_edit_view_shows_current_tags_and_image(self):
        self.user.can_post = True
        self.user.save(update_fields=["can_post"])
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

    def test_flyer_following_list_unauthenticated_view(self):
        response = self.client.get(reverse("following_flyer_list"))
        self.assertEqual(response.status_code, 302)

    def test_flyer_following_list_authenticated_view(self):
        self.user.followed_groups.add(self.poster)
        self.client.force_login(self.user)

        response = self.client.get(reverse("following_flyer_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<img")
        self.assertContains(response, self.flyer.image.url)
        self.assertTemplateUsed(response, 'flyer_list_following.html')



# Flyer creation and tags: Submit a valid form with an image and tags from all three categories; verify the Flyer saves and all selected tags are attached. 
# Also test that a missing required category or a tag from the wrong category is rejected.
# Form widgets and description: Check the rendered form uses a textarea, type="date", and type="time". Check description line breaks appear on the detail page.
# Following-page branches: Test parish flyers, no followed groups, followed groups with no flyers, and recent versus older announcements. A parish with no announcements currently risks raising Announcement.DoesNotExist because the view calls .latest('upload_date').
# Follow/unfollow behavior: Test group follow/unfollow, parish follow/unfollow, and the confirmation needed to switch parishes.
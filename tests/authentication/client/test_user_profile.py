"""User profile tests."""
from tests.authentication.client.test_base import BaseTest
from rest_framework import status
from tests.utils.utils import TestUtils
from tempfile import NamedTemporaryFile
from unittest.mock import patch
from tempfile import NamedTemporaryFile
from unittest.mock import patch, Mock
from django.test.client import encode_multipart
from cloudinary.api import Error


class TestClientAdmin(TestUtils):
    '''Contains tests for the User profile'''

    def test_get_user_profile(self):
        """
        Retreive User profile
        """
        self.set_token()
        response = self.client.get(
            self.client_profile, format="json")
        self.assertEqual(response.data['message'],
                         "Profile retreived successfully")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile_when_not_logged_in(self):
        """
        System should return an error when user tries to access 
        profile when not logged in
        """
        response = self.client.get(
            self.client_profile, format="json")
        self.assertEqual(str(response.data['errors']),
                         "Please log in to proceed.")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_profile(self):
        """
        Users should be able to update their own profile successfully
        """
        self.set_token()
        response = self.client.patch(
            self.client_profile, self.updated_profile, format="json")
        self.assertEqual(response.data['data']['message'],
                         "Profile updated successfully")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('authentication.views.uploader.upload')
    def test_upload_profile_picture(self, mock_upload):
        """
        Users should be able to upload their profile picture
        """
        self.set_token()
        image = NamedTemporaryFile(suffix='.jpg')
        mock_upload.return_value = {
            'url': 'http://res.cloudinary.com/landville/image/upload/v1561568984/xep5qlwc8.png'}
        data = self.updated_profile_with_image
        data['image'] = image
        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        response = self.client.patch(
            self.client_profile, content, content_type=content_type)
        image.close()
        self.assertEqual(response.data['data']['message'],
                         "Profile updated successfully")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('authentication.views.uploader.upload')
    def test_update_existing_profile_picture(self, mock_upload):
        """
        Users should be able to update their profile picture
        """
        self.set_token()
        self.client.patch(self.client_profile,
                          self.profile_with_image, format='json')
        image = NamedTemporaryFile(suffix='.jpg')
        mock_upload.return_value = {
            'url': 'http://res.cloudinary.com/landville/image/upload/v1561568984/xep5qlwc8.png'}
        data = self.updated_profile_with_image
        data['image'] = image
        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        response = self.client.patch(
            self.client_profile, content, content_type=content_type)
        image.close()
        self.assertEqual(response.data['data']['message'],
                         "Profile updated successfully")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('authentication.views.uploader.upload')
    def test_return_no_url_when_image_is_uploaded(self, mock_upload):
        """
        Test when upload function returns None instead of url 
        when picture is uploaded
        """
        self.set_token()
        image = NamedTemporaryFile(suffix='.jpg')
        mock_upload.return_value = {'url': None}
        data = self.updated_profile_with_image
        data['image'] = image
        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        response = self.client.patch(
            self.client_profile, content, content_type=content_type)
        image.close()
        self.assertIn('Enter a valid URL.',
                      str(response.data['errors']['image']))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_invalid_image(self):
        """
        Error should be thrown when an invalid image is uploaded
        """
        uploader = Mock()
        uploader.upload.side_effects = Error
        self.set_token()
        image = NamedTemporaryFile(suffix='txt')
        data = self.updated_profile_with_image
        data['image'] = image
        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        response = self.client.patch(
            self.client_profile, content, content_type=content_type)
        image.close()
        self.assertIn("Please provide a valid image format.",
                      str(response.data['errors']['image']))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('authentication.views.uploader.upload')
    def test_update_profile_without_employer_field(self, mock_upload):
        """
        Updating users profile without employer field should throw an error
        """
        self.set_token()
        image = NamedTemporaryFile(suffix='.jpg')
        mock_upload.return_value = {'url': 'http://www.upload.com/'}
        data = self.updated_profile_without_employer_field
        data['image'] = image
        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        response = self.client.patch(
            self.client_profile, content, content_type=content_type)
        image.close()
        self.assertIn("Please provide an employer",
                      str(response.data['errors']['employer']))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_profile_with_empty_city_field(self):
        """
        Updating users own profile with empty City address should raise an error
        """
        self.set_token()
        response = self.client.patch(
            self.client_profile, self.updated_profile_with_empty_city_field, format="json")
        self.assertIn("City cannot be empty!",
                      str(response.data['errors']['address']))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_profile_without_security_answer_field(self):
        """
        Updating users own profile without security answer field should raise an error
        """
        self.set_token()
        response = self.client.patch(
            self.client_profile, self.updated_profile_without_security_answer_field, format="json")
        self.assertIn("Please provide an answer to the selected question",
                      str(response.data['errors']['security_answer']))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_profile_without_phone_field(self):
        """
        Updating users own profile without phone field
        """
        self.set_token()
        response = self.client.patch(
            self.client_profile, self.updated_profile_without_phone_field, format="json")
        self.assertEqual(response.data['data']['profile']['phone'], None)
        self.assertEqual(response.data['data']['message'],
                         "Profile updated successfully")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user_profile_with_invalid_phonenumber(self):
        """
        Updating users own profile with an invalid phone number
        """
        self.set_token()
        response = self.client.patch(
            self.client_profile, self.updated_profile_with_invalid_phonenumber, format="json")
        self.assertIn("Phone number must be of the format +234 123 4567890",
                      str(response.data['errors']['phone']))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_profile_without_address_field(self):
        """
        Updating users own profile without address field
        """
        self.set_token()
        response = self.client.patch(
            self.client_profile, self.updated_profile_without_address_field, format="json")
        self.assertEqual(response.data['data']['profile']['address'], {})
        self.assertEqual(response.data['data']['message'],
                         "Profile updated successfully")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_if_user_profile_doesnt_contain_security_info(self):
        """
        Users profile data should not contain their security question and
        answer when retreived
        """
        self.set_token()
        response = self.client.patch(
            self.client_profile, self.updated_profile, format="json")
        self.assertNotIn('security_question', response.data['data']['profile'])
        self.assertNotIn('security_answer', response.data['data']['profile'])
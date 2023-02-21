from django.urls import reverse


def helper_test_page_obj_attribute(self, response,
                                   attribute, reverse_name, cls):
    if attribute != 'page_obj':
        return

    first_object = response.context[attribute][0]

    if reverse_name == reverse('posts:follow_index'):
        self.assertEqual(first_object.text, cls.following_post.text)
        self.assertEqual(first_object.author, cls.following)
        self.assertEqual(first_object.group, cls.following_group)
        self.assertEqual(first_object.group.id, cls.following_group.id)
        self.assertTrue(first_object.image)
    elif reverse_name == reverse('posts:index'):
        self.assertEqual(first_object.text, cls.post.text)
        self.assertEqual(first_object.author, cls.user)
        self.assertEqual(first_object.group, cls.group)
        self.assertEqual(first_object.group.id, cls.group.id)
        self.assertTrue(first_object.image)


def helper_test_group_attribute(self, response, attribute, cls):
    if attribute != 'group':
        return

    first_object = response.context[attribute]

    self.assertEqual(first_object.title, cls.group.title)
    self.assertEqual(first_object.slug, cls.group.slug)
    self.assertEqual(first_object.description, cls.group.description)
    self.assertEqual(first_object.id, cls.group.id)


def helper_test_author_attribute(self, response, attribute, cls):
    if attribute != 'author':
        return

    first_object = response.context[attribute]

    self.assertEqual(first_object.username, cls.user.username)


def helper_test_post_attribute(self, response, attribute, cls):
    if attribute != 'post':
        return

    first_object = response.context[attribute]

    self.assertEqual(first_object.text, cls.post.text)
    self.assertEqual(first_object.author, cls.user)
    self.assertEqual(first_object.group, cls.group)
    self.assertTrue(first_object.image)


def helper_test_form_attribute(self, form_fields, response, attribute):
    if attribute != 'form':
        return

    for value, expected in form_fields.items():
        with self.subTest(value=value):
            form_field = response.context.get(attribute).fields.get(value)
            self.assertIsInstance(form_field, expected)
